import json
import logging
import os

import requests
from flask import Blueprint, request, redirect, url_for, current_app
from flask_login import current_user, login_required, logout_user, login_user
from oauthlib.oauth2 import WebApplicationClient

from user import User

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

oauth = Blueprint('oauth', __name__, template_folder='../templates/oauth')

# Oauth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'

oauth_client = WebApplicationClient(GOOGLE_CLIENT_ID)

# This import has to be here, else import error (circular dependency)
from main import login_manager


def is_admin(user_id):
    config = current_app.jinja_env.globals['CONFIG']
    admins = config['user_ids_admins']
    if admins is not None:
        admins_list = admins.replace(' ', '').split(',')
        if user_id in admins_list:
            return True
    return False


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@login_manager.unauthorized_handler
def unauthorized():
    return 'You must be logged in to access this content.', 403


@oauth.route('/welcome')
def login_welcome():
    if current_user.is_authenticated:
        return (
            f'<p>Hello, {current_user.name}! You are logged in as {current_user.email}</p>'
            f'<p><a href="/">Home</a> - <a href="/admin/">Admin</a> - <a href="/logout">Logout</a></p>'
            )
    else:
        return '<a class="button" href="/login">Google Login</a>'


@oauth.route('/login')
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']
    request_uri = oauth_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['openid', 'email', 'profile'],
    )
    return redirect(request_uri)


@oauth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('blog.home'))


@oauth.route('/login/callback')
def callback():
    code = request.args.get('code')
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']
    token_url, headers, body = oauth_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    oauth_client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get('email_verified'):
        user_id = userinfo_response.json()['sub']
        email = userinfo_response.json()['email']
        picture = userinfo_response.json()['picture']
        name = userinfo_response.json()['given_name']
    else:
        return 'User email not available or not verified by Google.', 400

    user = User(id=user_id, name=name, email=email, profile_pic=picture)

    if not User.get(user_id):
        if not is_admin(user_id):
            log.warning(f'{user_id}, {email}, {name}: is not in the admins list; access not granted')
            return 'Login unsuccessful', 403
        else:
            User.create(user)

    login_success = login_user(user)
    if not login_success:
        return 'Login unsuccessful', 403

    return redirect(url_for('oauth.login_welcome'))

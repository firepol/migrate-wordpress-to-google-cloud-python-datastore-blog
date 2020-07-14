import calendar
import json
import os
import re

import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, logout_user, login_required, login_user
from jinja2 import evalcontextfilter, Markup, escape
from oauthlib.oauth2 import WebApplicationClient

from datastore_queries import *
from admin import admin
from user import User
from utils import clean_pre
from utils_flask import refresh_config

# Oauth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.register_blueprint(admin)  # Blueprint for Admin panel, to edit posts and configs
login_manager = LoginManager()
login_manager.init_app(app)
oauth_client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Flask-Login helper to retrieve a saved user
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403


@app.route("/welcome")
def login_welcome():
    if current_user.is_authenticated:
        return (
            f'<p>Hello, {current_user.name}! You are logged in! Email: {current_user.email}</p>'
            f'<div>'
            f'<p>Google Profile Picture:</p><img src="{current_user.profile_pic}" alt="Google profile pic"></img>'
            f'</div>'
            f'<br/><a href="/">Home</a> - <a href="/logout">Logout</a>'
            )
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = oauth_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
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
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(id=unique_id, name=users_name, email=users_email, profile_pic=picture)

    if not User.get(unique_id):
        User.create(user)

    login_success = login_user(user)
    if not login_success:
        return "Login unsuccessful", 403

    return redirect(url_for("login_welcome"))


def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.route('/')
def home():
    home_page = get_post('home')
    recent_posts = get_all_posts(limit=5)
    archives = get_archives()
    return render_template('home.html', post=home_page, recent_posts=recent_posts, archives=archives)


@app.route('/<slug>/')
def post(slug):
    if slug == 'favicon.ico':
        return ''
    result = get_post(slug)
    # result['content'] = fix_double_slash_escaping(result['content'])
    result['content'] = clean_pre(result['content'])
    return render_template(f"{result['post_type']}.html", post=result)


@app.route('/index/')
def posts_list():
    posts = get_all_posts('post')
    return render_template('posts_list.html', posts=posts)


@app.route('/<int:year>/<int:month>/')
def archives_list(year, month):
    posts = get_posts_by_archive(year, month)
    recent_posts = get_all_posts(limit=5)
    archives = get_archives()
    month_name = calendar.month_name[month]
    return render_template('archives_list.html', posts=posts, year=year, month_name=month_name,
                           recent_posts=recent_posts, archives=archives)


if __name__ == '__main__':
    refresh_config(app)
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.run(ssl_context='adhoc', host='127.0.0.1', port=8080, debug=True)

import os
import re

from flask import Flask
from flask_login import LoginManager
from jinja2 import evalcontextfilter
from markupsafe import escape, Markup

from user import User
from utils_flask import set_global_config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

set_global_config(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# These imports have to be here (especially oauth), else import error (circular dependency)
from blueprints.admin import admin
from blueprints.blog import blog
from blueprints.oauth import oauth

app.register_blueprint(blog)
app.register_blueprint(oauth)
app.register_blueprint(admin)


@app.template_filter()
def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


if __name__ == '__main__':
    app.run(
        ssl_context='adhoc',
        host='localhost',
        port=8080,
        debug=True
    )

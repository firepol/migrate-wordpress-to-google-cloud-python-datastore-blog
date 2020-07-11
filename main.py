import calendar
import re

from flask import Flask, render_template
from jinja2 import evalcontextfilter, Markup, escape

from datastore_queries import *
from admin import admin
from utils import clean_pre
from utils_flask import refresh_config

app = Flask(__name__)
app.register_blueprint(admin)


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
    app.run(host='localhost', port=8080, debug=True)

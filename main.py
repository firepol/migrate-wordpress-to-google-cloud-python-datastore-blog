from flask import Flask, render_template
from jinja2 import Environment, PackageLoader, select_autoescape
import configparser

from datastore_queries import get_all_posts, get_post, delete_all_posts
from utils import replace_pre

app = Flask(__name__)

ini = configparser.ConfigParser()
ini.read('./data/settings.ini')
app.jinja_env.globals['INI'] = ini


def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


app.jinja_env.filters['datetimeformat'] = datetimeformat


@app.route('/index/')
def root():
    posts = get_all_posts('post')
    return render_template('index.html', posts=posts)


@app.route('/')
def render_home():
    post = get_post('home')
    return render_template('home.html', post=post)


@app.route('/<slug>/')
def render_post(slug):
    if slug == 'favicon.ico':
        return ''
    post = get_post(slug)
    # post['content'] = clean_post(post['content'])
    post['content'] = replace_pre(post['content'])
    return render_template(f"{post['post_type']}.html", post=post)


@app.route('/delete_all_posts_now')
def delete_all_posts_now():
    delete_all_posts()
    return 'All posts deleted'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

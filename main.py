import re

from flask import Flask, render_template, request, redirect, url_for
from jinja2 import evalcontextfilter, Markup, escape
import configparser

from datastore_queries import get_all_posts, get_post, delete_all_posts, get_post_by_id, update_post
from utils import replace_pre

app = Flask(__name__)

ini = configparser.ConfigParser()
ini.read('./data/settings.ini')
app.jinja_env.globals['INI'] = ini


def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


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


# ADMIN #

@app.route('/admin/')
def admin_home():
    posts = get_all_posts()
    return render_template('index-admin.html', posts=posts)


@app.route('/admin/edit/<post_id>')
def admin_edit_post(post_id):
    post = get_post_by_id(post_id)
    return render_template('edit.html', post=post)


@app.route('/admin/edit/<post_id>', methods=['POST'])
def admin_save_updated_post(post_id):
    content = request.form['content']
    update_post(post_id, content)
    return redirect(url_for('admin_edit_post', post_id=post_id))


@app.route('/admin/delete_all_posts_now')
def admin_delete_all_posts_now():
    delete_all_posts()
    return 'All posts deleted'


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

import re

from flask import Flask, render_template, request, redirect, url_for, abort
from jinja2 import evalcontextfilter, Markup, escape

from datastore_queries import *
from utils import prettyprint_pre

app = Flask(__name__)


def refresh_config():
    """
    Set or refresh the CONFIG dictionary (used in templates) based on datastore Config entities
    """
    app.jinja_env.globals['CONFIG'] = get_config_dictionary()


refresh_config()


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
    recent_posts = get_all_posts(limit=5)
    archives = get_archives()
    return render_template('home.html', post=post, recent_posts=recent_posts, archives=archives)


@app.route('/<slug>/')
def render_post(slug):
    if slug == 'favicon.ico':
        return ''
    post = get_post(slug)
    # post['content'] = fix_double_slash_escaping(post['content'])
    post['content'] = prettyprint_pre(post['content'])
    return render_template(f"{post['post_type']}.html", post=post)


@app.route('/<int:year>/<int:month>/')
def render_archive(year, month):
    posts = get_posts_by_archive(year, month)
    recent_posts = get_all_posts(limit=5)
    archives = get_archives()
    month_name = calendar.month_name[month]
    return render_template('archives.html', posts=posts, year=year, month_name=month_name,
                           recent_posts=recent_posts, archives=archives)


# ADMIN #

@app.route('/admin/')
def admin_home():
    return render_template('admin.html')


# ADMIN CONFIGS

@app.route('/admin/configs/')
def admin_configs():
    configs = get_configs()
    return render_template('admin_configs.html', configs=configs)


@app.route('/admin/config/<config_id>')
def admin_edit_config(config_id):
    if config_id == 'new':
        config = {
            'name': 'new'
        }
    else:
        config = get_config_by_id(config_id)
        config['name'] = config.key.id_or_name
    refresh_config()
    return render_template('admin_config.html', config=config)


@app.route('/admin/config/<config_id>', methods=['POST'])
def admin_save_updated_config(config_id):
    request_form = request.form
    config = update_config(config_id, request_form)
    refresh_config()
    return redirect(url_for('admin_edit_config', config_id=config.key.id_or_name))


@app.route('/admin/config/delete/<config_id>', methods=['DELETE'])
def admin_delete_config(config_id):
    try:
        delete_config(config_id)
        refresh_config()
        return '', 204
    except:
        abort(500)


# ADMIN POSTS

@app.route('/admin/posts/')
def admin_posts():
    posts = get_all_posts()
    return render_template('admin_posts.html', posts=posts)


@app.route('/admin/post/<post_id>')
def admin_edit_post(post_id):
    if post_id == 'new':
        post = {
            'id': 'new'
        }
    else:
        post = get_post_by_id(post_id)
    return render_template('admin_post.html', post=post)


@app.route('/admin/post/<post_id>', methods=['POST'])
def admin_save_updated_post(post_id):
    request_form = request.form
    post = update_post(post_id, request_form)
    return redirect(url_for('admin_edit_post', post_id=post.key.id))


@app.route('/admin/post/delete/<post_id>', methods=['DELETE'])
def admin_delete_post(post_id):
    try:
        delete_post(post_id)
        return '', 204
    except:
        abort(500)


@app.route('/admin/insert_archives')
def admin_insert_archives():
    posts = get_all_posts('post')
    insert_archives(posts)
    return 'Archives index created'


@app.route('/admin/delete_all')
def admin_delete_all():
    delete_all_blog_entities()
    return 'All configs, posts and archives deleted'


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

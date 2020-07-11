from flask import Blueprint, render_template, abort, request, redirect, url_for, current_app

from datastore_queries import get_all_posts
from datastore_queries_admin import *
from utils_flask import refresh_config

admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates/admin')


@admin.route('/')
def admin_home():
    return render_template('index_admin.html')


# ADMIN CONFIGS

@admin.route('/configs/')
def configs():
    result = get_configs()
    return render_template('configs.html', configs=result)


@admin.route('/config/<config_id>')
def config_edit(config_id):
    if config_id == 'new':
        config = {
            'name': 'new'
        }
    else:
        config = get_config_by_id(config_id)
        config['name'] = config.key.id_or_name
    return render_template('config_edit.html', config=config)


@admin.route('/config/<config_id>', methods=['POST'])
def config_save(config_id):
    request_form = request.form
    config = update_config(config_id, request_form)
    refresh_config(current_app)
    return redirect(url_for('admin.config_edit', config_id=config.key.id_or_name))


@admin.route('/config/delete/<config_id>', methods=['DELETE'])
def config_delete(config_id):
    try:
        delete_config(config_id)
        refresh_config(current_app)
        return '', 204
    except:
        abort(500)


# ADMIN POSTS

@admin.route('/posts/')
def posts():
    result = get_all_posts()
    return render_template('posts.html', posts=result)


@admin.route('/post/<post_id>')
def post_edit(post_id):
    if post_id == 'new':
        post = {
            'id': 'new'
        }
    else:
        post = get_post_by_id(post_id)
    return render_template('post_edit.html', post=post)


@admin.route('/post/<post_id>', methods=['POST'])
def post_save(post_id):
    request_form = request.form
    post = update_post(post_id, request_form)
    return redirect(url_for('admin.post_edit', post_id=post.key.id))


@admin.route('/post/delete/<post_id>', methods=['DELETE'])
def post_delete(post_id):
    try:
        delete_post(post_id)
        return '', 204
    except:
        abort(500)


@admin.route('/insert_archives')
def insert_archives():
    result = get_all_posts('post')
    insert_archives(result)
    return 'Archives index created'


@admin.route('/delete_all')
def delete_all():
    delete_all_blog_entities()
    return 'All configs, posts and archives deleted'

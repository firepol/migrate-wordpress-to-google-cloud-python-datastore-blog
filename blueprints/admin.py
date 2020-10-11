import logging

from flask import Blueprint, render_template, abort, request, redirect, url_for, current_app, flash
from flask_login import login_required

from blobs.blob_group import get_dict_blob_group
from datastore_queries import get_all_posts
from datastore_queries_admin import *
from utils_flask import set_global_config
from utils_google_cloud_bucket import upload_to_bucket, get_all_bucket_blobs

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')


@admin.route('/')
@login_required
def admin_home():
    return render_template('index_admin.html')


# ADMIN CONFIGS

@admin.route('/configs/')
@login_required
def configs():
    result = get_configs()
    return render_template('configs.html', configs=result)


@admin.route('/config/<config_id>')
@login_required
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
@login_required
def config_save(config_id):
    request_form = request.form
    config = update_config(config_id, request_form)
    set_global_config(current_app)
    return redirect(url_for('admin.config_edit', config_id=config.key.id_or_name))


@admin.route('/config/delete/<config_id>', methods=['DELETE'])
@login_required
def config_delete(config_id):
    try:
        delete_config(config_id)
        set_global_config(current_app)
        return '', 204
    except:
        abort(500)


# ADMIN POSTS

@admin.route('/posts/')
@login_required
def posts():
    result = get_all_posts()
    return render_template('posts.html', posts=result)


@admin.route('/post/<post_id>')
@login_required
def post_edit(post_id):
    if post_id == 'new':
        post = {
            'id': 'new'
        }
    else:
        post = get_post_by_id(post_id)
    return render_template('post_edit.html', post=post)


@admin.route('/post/<post_id>', methods=['POST'])
@login_required
def post_save(post_id):
    request_form = request.form
    post = update_post(post_id, request_form)
    return redirect(url_for('admin.post_edit', post_id=post.key.id))


@admin.route('/post/delete/<post_id>', methods=['DELETE'])
@login_required
def post_delete(post_id):
    try:
        delete_post(post_id)
        return '', 204
    except:
        abort(500)


# BUCKET

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:  # check if the post request has the file part
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':  # if user selects no file, browser also submits an empty part without filename
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        blob_public_url = upload_to_bucket(file)
        return {
            'location': blob_public_url
        }


@admin.route('/uploads/')
@login_required
def uploads():
    bucket_blobs = get_all_bucket_blobs()
    result = get_dict_blob_group(bucket_blobs)
    return render_template('uploads.html', grouped_blobs=result)


# ADMIN USERS

@admin.route('/users/')
@login_required
def users():
    result = get_users()
    return render_template('users.html', users=result)

# DELETE


@admin.route('/insert_archives')
@login_required
def insert_archives():
    result = get_all_posts('post')
    insert_archives(result)
    return 'Archives index created'


@admin.route('/delete_all')
@login_required
def delete_all():
    delete_all_blog_entities()
    return 'All configs, posts and archives deleted'

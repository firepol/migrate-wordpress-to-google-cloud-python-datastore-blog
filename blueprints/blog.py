import calendar

from flask import Blueprint, render_template

from datastore_queries import get_post, get_all_posts, get_archives, get_posts_by_archive
from utils import clean_pre

blog = Blueprint('blog', __name__, template_folder='../templates')


@blog.route('/')
def home():
    home_page = get_post('home')
    recent_posts = get_all_posts(limit=5)
    archives = get_archives()
    return render_template('home.html', post=home_page, recent_posts=recent_posts, archives=archives)


@blog.route('/<slug>/')
def post(slug):
    if slug == 'favicon.ico':
        return ''
    result = get_post(slug)
    result['content'] = clean_pre(result['content'])
    return render_template(f"{result['post_type']}.html", post=result)


@blog.route('/index/')
def posts_list():
    posts = get_all_posts('post')
    return render_template('posts_list.html', posts=posts)


@blog.route('/<int:year>/<int:month>/')
def archives_list(year, month):
    posts = get_posts_by_archive(year, month)
    recent_posts = get_all_posts(limit=5)
    archives = get_archives()
    month_name = calendar.month_name[month]
    return render_template('archives_list.html', posts=posts, year=year, month_name=month_name,
                           recent_posts=recent_posts, archives=archives)

from flask import Flask, render_template
from db.db_model import get_db_session
from db.db_queries import get_published_posts, get_post
from tools.local_utils import get_settings
from utils import fix_double_slash_escaping


app = Flask(__name__)

ini = get_settings()
app.jinja_env.globals['CONFIG'] = ini['blog_config']

@app.template_filter()
def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)

@app.route('/')
def posts_list():
    session = get_db_session()
    posts = get_published_posts(session)
    return render_template('posts_list.html', posts=posts)


@app.route('/<slug>')
def post(slug):
    session = get_db_session()
    result = get_post(session, slug)
    result.content = fix_double_slash_escaping(result.content)
    return render_template('post.html', post=result)


if __name__ == '__main__':
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.run(host='127.0.0.1', port=8082, debug=True)

from flask import Flask, render_template
from db_model import get_db_session
from db_queries import get_published_posts, get_post
from utils import clean_post


app = Flask(__name__)


@app.route('/')
def root():
    session = get_db_session()
    posts = get_published_posts(session)
    return render_template('index.html', posts=posts)


@app.route('/<slug>')
def render_post(slug):
    session = get_db_session()
    post = get_post(session, slug)
    post.content = clean_post(post.content)
    return render_template('post.html', post=post)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

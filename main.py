from flask import Flask, render_template
from datastore_queries import get_all_posts, get_post, delete_all_posts


app = Flask(__name__)


@app.route('/')
def root():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)


@app.route('/<slug>')
def render_post(slug):
    post = get_post(slug)
    # post['content'] = clean_post(post['content'])
    return render_template('post.html', post=post)


@app.route('/delete_all_posts_now')
def delete_all_posts_now():
    delete_all_posts()
    return 'All posts deleted'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

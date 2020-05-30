from db_model import Post


def get_published_posts(session):
    return session.query(Post)\
        .filter(Post.status == 'publish') \
        .filter(Post.post_type == 'post') \
        .filter(Post.password == '')\
        .order_by(Post.date)\
        .all()


def get_post(session, slug):
    return session.query(Post) \
        .filter(Post.slug == slug) \
        .one_or_none()

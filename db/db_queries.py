from db.db_model import Post


def get_published_posts(session, post_type=None):
    query = session.query(Post)\
        .filter(Post.status == 'publish') \
        .filter(Post.post_type.in_(['post', 'page']))\
        .filter(Post.password == '')

    if post_type in ['post', 'page']:
        query = query.filter(Post.post_type == post_type)

    return query.order_by(Post.date).all()


def get_post(session, slug):
    return session.query(Post) \
        .filter(Post.slug == slug) \
        .one_or_none()

from db_model import Post


def get_published_posts(session):
    query = session.query(Post)\
        .filter(Post.status == 'publish') \
        .filter(Post.post_type == 'post') \
        .filter(Post.password == '')

    return query.all()


def get_post(session, slug):
    return session.query(Post) \
        .filter(Post.slug == slug) \
        .one_or_none()

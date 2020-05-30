from google.cloud import datastore


def get_all_posts():
    client = datastore.Client()
    kind = 'Post'
    query = client.query(kind=kind, order=('date',))
    result = query.fetch()
    return result


def get_post(slug):
    client = datastore.Client()
    kind = 'Post'
    query = client.query(kind=kind)
    query.add_filter('slug', '=', slug)
    result = list(query.fetch(1))
    if len(result) < 1:
        return None
    else:
        return result[0]


def delete_all_posts():
    client = datastore.Client()
    kind = 'Post'
    posts = client.query(kind=kind).fetch()

    for p in posts:
        client.delete(p.key)
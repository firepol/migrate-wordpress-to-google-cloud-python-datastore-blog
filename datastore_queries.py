from google.cloud import datastore

from datastore_queries_admin import get_configs


def get_config_dictionary():
    configs = get_configs()
    result = {}
    for c in configs:
        result[c.key.id_or_name] = c['value']
    return result


def get_all_posts(post_type=None, limit=None):
    """
    :param post_type: 'post' or 'page'
    :param limit: max nr of posts to retrieve
    """
    client = datastore.Client()
    query = client.query(kind='Post', order=('-date',))
    if post_type in ['post', 'page']:
        query.add_filter('post_type', '=', post_type)
    return query.fetch(limit=limit)


def get_posts_by_archive(year, month):
    client = datastore.Client()
    query = client.query(kind='Post', order=('-date',))
    query.add_filter('year', '=', year)
    query.add_filter('month', '=', month)
    return query.fetch()


def get_post(slug):
    client = datastore.Client()
    query = client.query(kind='Post')
    query.add_filter('slug', '=', slug)
    result = list(query.fetch(1))
    if len(result) < 1:
        return None
    else:
        return result[0]


def get_archives():
    client = datastore.Client()
    query = client.query(kind='Archive')
    query.order = ['-year', '-month']
    return query.fetch()

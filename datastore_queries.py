import calendar
import locale

from google.cloud import datastore


def get_configs():
    client = datastore.Client()
    query = client.query(kind='Config')
    return query.fetch()


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


def get_post_by_id(post_id):
    client = datastore.Client()
    key = client.key('Post', int(post_id))
    return client.get(key)


def update_post(post_id, request_form):
    client = datastore.Client()
    key = client.key('Post', int(post_id))
    post = client.get(key)
    post['title'] = request_form['title']
    post['content'] = request_form['content']
    client.put(post)


def get_archives():
    client = datastore.Client()
    query = client.query(kind='Archive')
    query.order = ['-year', '-month']
    return query.fetch()


def insert_archives(posts):
    client = datastore.Client()
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        print('en_US locale could not be found')

    for post in posts:
        insert_archive_by_post(client, post)


def insert_archive_by_post(client, post):
    key = client.key('Archive', f"{post['year']}-{post['month']:02d}")
    item = datastore.Entity(key=key)
    item['year'] = post['year']
    item['month'] = post['month']
    item['month_name'] = calendar.month_name[post['month']]
    client.put(item)


def delete_all_blog_entities():
    client = datastore.Client()
    delete_all_entities_by_kind(client, 'Config')
    delete_all_entities_by_kind(client, 'Post')
    delete_all_entities_by_kind(client, 'Archive')


def delete_all_entities_by_kind(client, kind):
    posts = client.query(kind=kind).fetch()
    for p in posts:
        client.delete(p.key)

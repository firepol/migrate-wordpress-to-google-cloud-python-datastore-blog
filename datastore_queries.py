import calendar
import datetime
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


def get_config_by_id(config_id):
    client = datastore.Client()
    key = client.key('Config', config_id)
    return client.get(key)


def update_config(config_id, request_form):
    client = datastore.Client()
    key = client.key('Config', config_id)
    config = client.get(key)
    config['value'] = request_form['value']
    client.put(config)


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
    post_date = datetime.datetime.now()
    if post_id != 'new':
        key = client.key('Post', int(post_id))
        post = client.get(key)
    else:
        key = client.key('Post')
        post = datastore.Entity(key=key)
        post['date'] = post_date
        # comment_count needed only for imported posts
    post['title'] = request_form['title']
    post['slug'] = request_form['slug']
    post['content'] = request_form['content']
    post['post_type'] = request_form['post_type']
    post['modified'] = post_date
    post['year'] = post['date'].year
    post['month'] = post['date'].month
    client.put(post)
    insert_archive_by_post(client, post)
    return post.key.id


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


def delete_post(post_id):
    client = datastore.Client()
    key = client.key('Post', int(post_id))
    client.delete(key)


def delete_all_entities_by_kind(client, kind):
    entities = client.query(kind=kind).fetch()
    for entity in entities:
        client.delete(entity.key)

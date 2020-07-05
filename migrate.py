import locale
import re
import configparser
import sys

from datastore_queries import insert_archive_by_post
from db_model import get_db_session
from db_queries import get_published_posts
from google.cloud import datastore
from utils import clean_post

settings = configparser.ConfigParser()
settings.read('./data/settings.ini')

wp_uploads_dir = 'wp-content/uploads'  # WordPress has all the uploads in this relative directory
external_url = settings['blog_config']['external_url']  # This is the website URL (assuming new website is the same)
blob_name_prefix = settings['blog_config']['blob_name_prefix']  # Instead of wp_uploads_dir, use this directory
bucket_name = settings['blog_config']['google_cloud_bucket_name']
bucket_host = 'https://storage.googleapis.com'

_re_compiled = re.compile(r"<pre.*?>(.*?)</pre>", re.DOTALL)


def nl2br(value):
    # split(escape(value)) causes html tags to be escaped: just split without escaping
    _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                          for p in _paragraph_re.split(value))
    return result


def replace_media_urls(content, old_url, new_url):
    """
    Fix URLs in content, replace them with a new URL with different prefix

    >>> replace_media_urls('Check http://foo.bar/wp-content/uploads/foo.jpg or http://foo.bar',\
    'http://foo.bar/wp-content/uploads/', 'https://storage.googleapis.com/media/')
    'Check https://storage.googleapis.com/media/foo.jpg or http://foo.bar'
    """

    return content.replace(old_url, new_url)


def replace_br_in_pre(content):
    """
    Fix URLs in content, replace them with a new URL with different prefix

    >>> replace_br_in_pre('Check <pre> a b c <br> a b <br></pre> a b <br> c')
    'Check <pre> a b c  a b </pre> a b  c'
    """

    return content.replace('<br>', '')


def remove_br_in_pre(content):
    """
    Fix URLs in content, replace them with a new URL with different prefix

    >>> remove_br_in_pre('Check <pre> a b c <br> a b <br></pre> a b <br> c <pre>final<br></pre>')
    'Check <pre> a b c  a b </pre> a b <br> c <pre>final</pre>'
    """

    return re.sub(_re_compiled, lambda match: replace_br_in_pre(match.group()), content)


def save_configs_to_datastore():
    client = datastore.Client()
    print('Saving configs...')
    for config_name, config_value in settings.items('blog_config'):
        print(f'{config_name}: {config_value}')
        key = client.key('Config', config_name)
        item = datastore.Entity(key=key)
        item['value'] = config_value
        client.put(item)


def save_posts_to_datastore():
    # Locale is preferred, to have the date in US format
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        print('en_US locale could not be found')

    session = get_db_session()
    posts = get_published_posts(session)
    client = datastore.Client()

    if len(list(posts)) == 0:
        print('The `wp_posts` table is empty: if not done already, please run `db_init.py`, '
              'then import your posts (that you exported in CSV format)')
        sys.exit()
    print('Saving posts...')
    for p in posts:
        print(f'{p.id}: {p.title}')
        key = client.key('Post', p.id)
        item = datastore.Entity(key=key, exclude_from_indexes=('content',))
        item['slug'] = p.slug
        item['title'] = p.title
        item['post_type'] = p.post_type
        item['date'] = p.date
        item['year'] = p.date.year
        item['month'] = p.date.month
        item['modified'] = p.modified.isoformat()
        item['comment_count'] = p.comment_count

        item['content'] = clean_post(p.content)
        item['content'] = nl2br(item['content'])
        item['content'] = replace_media_urls(item['content'], f'{external_url}/{wp_uploads_dir}',
                                             f'{bucket_host}/{bucket_name}/{blob_name_prefix}')
        item['content'] = remove_br_in_pre(item['content'])

        client.put(item)

        insert_archive_by_post(client, item)


if __name__ == '__main__':
    save_configs_to_datastore()
    save_posts_to_datastore()

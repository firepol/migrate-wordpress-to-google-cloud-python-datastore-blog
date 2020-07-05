import configparser
import locale
import sys

from google.cloud import datastore

from datastore_queries import insert_archive_by_post
from db_model import get_db_session
from db_queries import get_published_posts
from utils import apply_all_cleanings

settings = configparser.ConfigParser()
settings.read('./data/settings.ini')

wp_uploads_dir = 'wp-content/uploads'  # WordPress has all the uploads in this relative directory
external_url = settings['blog_config']['external_url']  # This is the website URL (assuming new website is the same)
blob_name_prefix = settings['blog_config']['blob_name_prefix']  # Instead of wp_uploads_dir, use this directory
bucket_name = settings['blog_config']['google_cloud_bucket_name']
bucket_host = 'https://storage.googleapis.com'


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

        clean_content = apply_all_cleanings(p.content)
        # Replace old wp_uploads URL with new google bucket URL
        item['content'] = clean_content.replace(f'{external_url}/{wp_uploads_dir}',
                                                f'{bucket_host}/{bucket_name}/{blob_name_prefix}')

        client.put(item)

        insert_archive_by_post(client, item)


if __name__ == '__main__':
    save_configs_to_datastore()
    save_posts_to_datastore()

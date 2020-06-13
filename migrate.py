import locale
import re
import configparser
import sys

from datastore_queries import insert_archive_by_post
from db_model import get_db_session
from db_queries import get_published_posts
from google.cloud import datastore
from utils import clean_post

client = datastore.Client()

session = get_db_session()
posts = get_published_posts(session)

try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except:
    print('en_US locale could not be found')


def nl2br(value):
    # split(escape(value)) causes html tags to be escaped: just split without escaping
    _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                          for p in _paragraph_re.split(value))
    return result


settings = configparser.ConfigParser()
settings.read('./data/settings.ini')

print('Saving configs...')
for config_name, config_value in settings.items('blog_config'):
    print(f'{config_name}: {config_value}')
    key = client.key('Config', config_name)
    item = datastore.Entity(key=key)
    item['value'] = config_value
    client.put(item)

if len(list(posts)) == 0:
    print(f"Empty database created at {settings['config']['db_url']}; "
          f"please create the `wp_posts` table and then import your posts exported (in CSV format)")
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

    content = clean_post(p.content)
    nl2br_content = nl2br(content)

    item['content'] = nl2br_content

    client.put(item)

    insert_archive_by_post(client, item)

    # print(f'Saved {item.key.name}')

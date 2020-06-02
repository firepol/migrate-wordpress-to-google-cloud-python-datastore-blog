import re

from db_model import get_db_session
from db_queries import get_published_posts
from google.cloud import datastore
from jinja2 import evalcontextfilter, Markup, escape
from utils import clean_post, replace_pre

datastore_client = datastore.Client()

session = get_db_session()
posts = get_published_posts(session)

kind = 'Post'


def nl2br(value):
    # split(escape(value)) causes html tags to be escaped: just split without escaping
    _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                          for p in _paragraph_re.split(value))
    return result


for p in posts:
    print(f'Saving {p.id}: {p.title}')
    key = datastore_client.key(kind, p.id)
    item = datastore.Entity(key=key, exclude_from_indexes=('content',))
    item['slug'] = p.slug
    item['title'] = p.title
    item['post_type'] = p.post_type
    item['date'] = p.date
    item['modified'] = p.modified.isoformat()
    item['comment_count'] = p.comment_count

    content = clean_post(p.content)
    nl2br_content = nl2br(content)

    item['content'] = nl2br_content

    datastore_client.put(item)
    # print(f'Saved {item.key.name}')

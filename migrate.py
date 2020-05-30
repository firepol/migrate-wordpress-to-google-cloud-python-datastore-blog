from db_model import get_db_session
from db_queries import get_published_posts
from google.cloud import datastore

from utils import clean_post

datastore_client = datastore.Client()

session = get_db_session()
posts = get_published_posts(session)

kind = 'Post'

for p in posts:
    print(f'Saving {p.id}: {p.title}')
    key = datastore_client.key(kind, p.id)
    item = datastore.Entity(key=key, exclude_from_indexes=('content',))
    item['slug'] = p.slug
    item['title'] = p.title
    item['content'] = clean_post(p.content)
    item['date'] = p.date.isoformat()
    item['modified'] = p.modified.isoformat()
    item['comment_count'] = p.comment_count
    datastore_client.put(item)
    # print(f'Saved {item.key.name}')

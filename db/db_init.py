import csv
import os
import sqlite3

import configparser

import click

from tools.local_utils import get_settings

settings = get_settings()
config = settings['config']


def create_wp_posts_table(db_file_path):
    print(f'Creating `{db_file_path}` DB with the `wp_posts` table to be used to import your WordPress posts...')
    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()
    with open('create_wp_posts.sql') as sql_file:
        sql_as_string = sql_file.read()
        cursor.executescript(sql_as_string)

    csv_path = config['wp_posts_csv_path']
    if os.path.isfile(csv_path):
        print(f'Importing data from {csv_path}...')
        with open(csv_path, 'r') as csv_file:
            dr = csv.DictReader(csv_file)
            to_db = [(tuple([i[field] for field in dr.fieldnames])) for i in dr]
        question_marks = '(?' + 22*', ?' + ')'  # 23 columns, question marks like that for the string format
        cursor.executemany(f'INSERT INTO `wp_posts` VALUES {question_marks};', to_db)
        connection.commit()

    connection.close()


db_url = config['db_url']
db_file = db_url.replace('sqlite:///', '')

db_exists = False
if os.path.isfile(db_file):
    db_exists = True
    if click.confirm(f'This will delete `wp_posts` and create the table again. Do you want to proceed?', default=True):
        create_wp_posts_table(db_file)
else:
    create_wp_posts_table(db_file)

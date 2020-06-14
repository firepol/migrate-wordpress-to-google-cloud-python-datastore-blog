import os
import sqlite3

import configparser

import click


def create_wp_posts_table(db_file_path):
    print(f'Creating `{db_file_path}` DB with the `wp_posts` table to be used to import your WordPress posts...')
    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()
    sql_file = open('db/create_wp_posts.sql')
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)


settings = configparser.ConfigParser()
settings.read('./data/settings.ini')
db_url = settings['config']['db_url']
db_file = db_url.replace('sqlite:///', '')

db_exists = False
if os.path.isfile(db_file):
    db_exists = True
    if click.confirm(f'This will delete `wp_posts` and create the table again. Do you want to proceed?', default=True):
        create_wp_posts_table(db_file)
else:
    create_wp_posts_table(db_file)

import os


def clean_post(content):
    return content.replace(u'\\r\\n', os.linesep)\
        .replace('\\"', '"')

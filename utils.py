import os


def clean_post(content):
    return content.replace(u'\\r\\n', os.linesep)\
        .replace('\\"', '"')


def replace_pre(content):
    return content.replace(u'<pre class="lang:default decode:true ">', '<pre class="prettyprint">')\
        .replace(u'<pre class="lang:default decode:true">', '<pre class="prettyprint">')

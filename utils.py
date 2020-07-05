import os
import re


def apply_all_cleanings(content):
    return remove_br_in_pre(nl2br(fix_double_slash_escaping(content)))


def fix_double_slash_escaping(content):
    """
    Fix the double backslashes used to escape content and fix with proper replacement
    """
    return content.replace(u'\\r\\n', os.linesep)\
        .replace('\\"', '"')


def prettyprint_pre(content):
    """
    Add class="prettyprint" to <pre> tags. This will make the prettyprint plugin work.
    """
    return content.replace(u'<pre class="lang:default decode:true ">', '<pre class="prettyprint">')\
        .replace(u'<pre class="lang:default decode:true">', '<pre class="prettyprint">')


def nl2br(content):
    """
    Replace \r\n (new line) with <br>
    """
    # split(escape(value)) causes html tags to be escaped: just split without escaping
    _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')\
                          for p in _paragraph_re.split(content))
    return result


def remove_br_in_pre(content):
    """
    Fix URLs in content, replace them with a new URL with different prefix

    >>> remove_br_in_pre('Check <pre> a b c <br> a b <br></pre> a b <br> c <pre>final<br></pre>')
    'Check <pre> a b c  a b </pre> a b <br> c <pre>final</pre>'
    """
    _re_content_in_pre = re.compile(r"<pre.*?>(.*?)</pre>", re.DOTALL)
    return re.sub(_re_content_in_pre, lambda match: match.group().replace('<br>', ''), content)

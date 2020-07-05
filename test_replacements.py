import logging
import os

from utils import remove_br_in_pre

FORMAT = "[%(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='test.log', level=logging.INFO, format=FORMAT)


def test_replace_1_line():
    content = 'Check <pre> a b c <br> a b <br></pre> a b <br> c <pre>final<br></pre>'
    expected_result = 'Check <pre> a b c  a b </pre> a b <br> c <pre>final</pre>'
    result = remove_br_in_pre(content)
    assert result == expected_result


def test_replace_2_lines():
    content = 'Check <pre> foo <br> bar <br></pre> a b <br> c <pre>new line:<br>' + os.linesep\
              + 'final</pre>'
    expected_result = 'Check <pre> foo  bar </pre> a b <br> c <pre>new line:' + os.linesep\
                      + 'final</pre>'
    result = remove_br_in_pre(content)
    assert result == expected_result


if __name__ == '__main__':
    test_replace_1_line()
    test_replace_2_lines()

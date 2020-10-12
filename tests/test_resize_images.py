import logging
import os

import requests

from utils_image import make_small_square

FORMAT = "[%(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='test.log', level=logging.INFO, format=FORMAT)


def test_landscape():
    filepath = 'landscape.jpg'
    url = 'https://picsum.photos/400/300'
    response = requests.get(url, stream=True)
    result = make_small_square(response.raw, filepath, 150)
    result[1].save(os.path.join('output/', result[0]), quality=85)
    assert result[0] == 'landscape-150x150.jpg'


def test_portrait():
    filepath = 'portrait.jpg'
    url = 'https://picsum.photos/200/300'
    response = requests.get(url, stream=True)
    result = make_small_square(response.raw, filepath, 150)
    result[1].save(os.path.join('output/', result[0]), quality=85)
    assert result[0] == 'portrait-150x150.jpg'


def test_little():
    filepath = 'little.jpg'
    url = 'https://picsum.photos/140/120'
    response = requests.get(url, stream=True)
    result = make_small_square(response.raw, filepath, 150)
    result[1].save(os.path.join('output/', result[0]), quality=85)
    assert result[0] == 'little-150x150.jpg'


if __name__ == '__main__':
    test_little()
    test_landscape()
    test_portrait()

import logging
import os
import re
from dataclasses import dataclass, InitVar
from google.cloud.storage import Blob
from blobs.file_type import FileType

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
resized_pic_re = re.compile(r'(?P<group_name>.*)(-(?P<width>\d+)x(?P<height>\d+))')


@dataclass
class BlobFile:
    original_blob: InitVar[Blob]
    public_url: str = None
    name: str = None
    group_name: str = None
    file_type: FileType = None
    width: int = None
    height: int = None

    def __post_init__(self, original_blob):
        self.public_url = original_blob.public_url
        self.name = original_blob.name
        self.group_name = get_group_name(self.name)
        log.debug(f'BLOB: {self.name}; GROUP: {self.group_name}')
        try:
            self.file_type, self.width, self.height = get_file_info(self.name)
        except:
            log.exception(f'Error trying to initialize blob_file for {self.name}')
            raise


def get_group_name(name):
    """
    Of a given wordpress file name (available in different sizes), return a group name to identify all images
    belonging to the same group

    >>> get_group_name('media/2013/01/foo-150x150.png')
    'media/2013/01/foo'

    >>> get_group_name('media/2013/01/foo-150x150')
    'media/2013/01/foo'

    >>> get_group_name('media/2013/01/foo.png')
    'media/2013/01/foo'

    >>> get_group_name('media/2013/01/foo150x150')
    'media/2013/01/foo150x150'

    >>> get_group_name('media/2016/08/xk-detect-x380.jpg')
    'media/2016/08/xk-detect-x380'
    """
    prefix, extension = os.path.splitext(name)

    matches = resized_pic_re.search(prefix)
    if matches is None:
        return prefix
    group_name = matches.group('group_name')
    return group_name


def get_file_info(name):
    """
    Of a given wordpress file name (available in different sizes), return FileType, Width and Heigth

    >>> get_file_info('foo-1024x768')
    (<FileType.Large: (1024,)>, 1024, 768)

    >>> get_file_info('foo-768x1024')
    (<FileType.Large: (1024,)>, 768, 1024)

    >>> get_file_info('foo-150x150.png')
    (<FileType.LittleSquare: (150,)>, 150, 150)

    >>> get_file_info('foo-140x10000')
    (<FileType.Small: (1,)>, 140, 10000)

    >>> get_file_info('foo.png')
    (<FileType.Original: (10000,)>, None, None)

    >>> get_file_info('foo.pdf')
    (<FileType.Other: (0,)>, None, None)

    >>> get_file_info('foo-bar-x380.jpg')
    (<FileType.Original: (10000,)>, None, None)

    >>> get_file_info('foo-288x300.png')
    (<FileType.Thumbnail: (300,)>, 288, 300)
    """

    prefix, extension = os.path.splitext(name)

    matches = resized_pic_re.search(prefix)

    if matches is None and extension in IMAGE_EXTENSIONS:
        return FileType.Original, None, None
    elif matches is None and extension not in IMAGE_EXTENSIONS:
        return FileType.Other, None, None

    matched_width = matches.group('width')
    matched_height = matches.group('height')
    if matched_width == '' or matched_height == '':
        return FileType.Original, None, None

    width = int(matched_width)
    height = int(matched_height)

    file_type = None

    if width == 1024 or height == 1024:
        file_type = FileType.Large
    elif width == 768 or height == 768:
        file_type = FileType.MediumLarge
    elif width == 624 or height == 624:
        file_type = FileType.Medium
    elif width == 300 or height == 300:
        file_type = FileType.Thumbnail
    elif width == 150 and height == 150:
        file_type = FileType.LittleSquare
    elif width < 150 or height < 150:
        file_type = FileType.Small
    return file_type, width, height

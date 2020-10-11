from dataclasses import dataclass, InitVar
from typing import Dict, List

from google.cloud.storage import Blob

from blobs.blob_file import BlobFile
from blobs.file_type import FileType, get_fallback


@dataclass
class BlobGroup:
    name: str
    files: Dict[FileType, BlobFile] = None
    thumbnail_url: str = None

    def __init__(self, name: str):
        self.name = name
        self.files = dict()

    def get_thumbnail(self):
        return get_blob_version(300, self.files)


def get_blob_version(max_size: int, blob_files: Dict[FileType, BlobFile]):
    """
    Return blob of maximum size, or the original, or None if the file is not an image
    """

    wished_file_type = FileType.Original
    if max_size <= 150:
        wished_file_type = FileType.LittleSquare
    elif max_size <= 300:
        wished_file_type = FileType.Thumbnail
    elif max_size <= 624:
        wished_file_type = FileType.Medium
    elif max_size <= 1024:
        wished_file_type = FileType.Large

    available_file_types = [b.file_type for b in blob_files.values()]
    file_type = get_fallback(wished_file_type, available_file_types)
    return blob_files[file_type]


def get_dict_blob_group(blobs: List[Blob]):
    """
    From a given list of blobs, get a dictionary with keys = group names, values = BlobGroups
    """
    result = dict()
    for b in blobs:
        blob_file = BlobFile(b)
        group_name = blob_file.group_name
        if group_name not in result:
            result[group_name] = BlobGroup(group_name)
        group = result[group_name]
        group.files[blob_file.file_type] = blob_file
        group.thumbnail_url = group.get_thumbnail().public_url
    return result

import logging

from google.cloud import storage
from werkzeug.utils import secure_filename

from blobs.file_type import FileType
from datastore_queries import get_config_dictionary
from datetime import datetime

from utils_image import resize, make_small_square, get_size

log = logging.getLogger()


def upload_to_bucket(file):
    """
    Upload file to google cloud bucket using as name scheme year/month/filename e.g. 2020/12/foo.jpg
    :param file: file to upload
    :return: blob public url
    """
    config = get_config_dictionary()
    bucket_name = config['google_cloud_bucket_name']
    blob_name_prefix = config['blob_name_prefix']
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    today = datetime.today()
    file_name = secure_filename(file.filename)
    if file_name != file.filename:
        log.info(f'Original file `{file.filename}` renamed to `{file_name}`')
    blob_name = f'{blob_name_prefix}/{today.year}/{today.month:02}/{file_name}'
    log.info(f'Uploading file {file_name} to bucket')
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)

    # TODO: do this only for pics
    results = dict()
    results[FileType.LittleSquare] = make_small_square(file, file_name, 150)
    for file_type in FileType:
        if file_type not in [FileType.Original, FileType.Other, FileType.Small, FileType.LittleSquare]:
            result = resize_if_bigger(file, file_name, file_type.value[0])
            if result:
                results[file_type] = result

    return blob.public_url


def resize_if_bigger(file, file_name, wished_side):
    original_width, original_height = get_size(file)
    # resize original and upload it:
    if original_width > wished_side or original_height > wished_side:
        return resize(file, file_name, (wished_side, wished_side))
    return None


def get_all_bucket_blobs():
    """Lists all the blobs in the bucket."""
    config = get_config_dictionary()
    bucket_name = config['google_cloud_bucket_name']
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)
    return list(blobs)

import logging

from google.cloud import storage
from werkzeug.utils import secure_filename

from tools.local_utils import get_settings
from datetime import datetime

log = logging.getLogger()


def upload_to_bucket(file):
    """
    Upload file to google cloud bucket using as name scheme year/month/filename e.g. 2020/12/foo.jpg
    :param file: file to upload
    :return: blob public url
    """
    settings = get_settings()
    bucket_name = settings['blog_config']['google_cloud_bucket_name']
    blob_name_prefix = settings['blog_config']['blob_name_prefix']
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
    return blob.public_url

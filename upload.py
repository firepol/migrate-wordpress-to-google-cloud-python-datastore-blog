import logging
import os

import configparser
import time
from concurrent import futures
from multiprocessing import cpu_count

from google.cloud import storage


logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


def get_elapsed_seconds(start_time):
    return round(time.time() - start_time, 2)


def get_upload_variables():
    settings = configparser.ConfigParser()
    settings.read('./data/settings.ini')
    bucket_name = settings['blog_config']['google_cloud_bucket_name']
    source_root = settings['config']['wp_uploads_path']
    blob_name_prefix = settings['config']['blob_name_prefix']
    max_files_to_upload = int(settings['config']['max_files_to_upload'])
    log.info(f'Copying {max_files_to_upload} files from: {source_root} to blob name prefixed with `{blob_name_prefix}`')
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    return blob_name_prefix, bucket, max_files_to_upload, source_root


def upload_file_to_bucket(source_root, subdir, file, bucket, blob_name_prefix, log_upload_file_message_prefix=''):
    # TODO: test with Windows paths (C:, D: etc.)
    partial_blob_name = f'{subdir}/{file}'.replace(source_root, '')
    blob_name = f'{blob_name_prefix}{partial_blob_name}'
    log.info(f'{log_upload_file_message_prefix}Uploading file {partial_blob_name}')
    file_path = os.path.join(subdir, file)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    return blob.public_url, True


def upload_files_to_bucket():
    blob_name_prefix, bucket, max_files_to_upload, source_root = get_upload_variables()

    start_time = time.time()
    files_count = 0
    for subdir, dirs, files in os.walk(os.path.join(source_root)):
        log.info(f'Processing directory: {subdir}')
        for file in files:
            if files_count == max_files_to_upload:
                elapsed_time = get_elapsed_seconds(start_time)
                log.info(f'Uploaded {max_files_to_upload} files in {elapsed_time} seconds')
                return
            files_count += 1
            blob_url = upload_file_to_bucket(source_root, subdir, file, bucket, blob_name_prefix, f'{files_count}: ')
            log.info(f'File uploaded: {blob_url}')

    elapsed_time = get_elapsed_seconds(start_time)
    log.info(f'Uploaded a total of {files_count} files in {elapsed_time} seconds')


def upload_files_to_bucket_in_parallel():
    # Inspired by https://github.com/googleapis/python-storage/issues/36

    blob_name_prefix, bucket, max_files_to_upload, source_root = get_upload_variables()

    pool = futures.ThreadPoolExecutor(max_workers=cpu_count())
    uploads = []

    start_time = time.time()
    files_count = 0
    for subdir, dirs, files in os.walk(os.path.join(source_root)):
        log.info(f'Processing directory: {subdir}')
        for file in files:
            files_count += 1
            upload = pool.submit(upload_file_to_bucket, source_root, subdir, file, bucket, blob_name_prefix)
            uploads.append(upload)

    future_count = 0
    successes = []
    for f in futures.as_completed(uploads):
        future_count += 1
        blob_url, success = f.result()
        successes.append(success)
        if success:
            log.info(f'File uploaded: {blob_url}')
        else:
            log.error(f'Error uploading: {blob_url}')

    if files_count != future_count:
        log.error('Some upload jobs did not complete!')
    if not all(successes):
        log.error('Some upload jobs completed but were not successful!')

    elapsed_time = get_elapsed_seconds(start_time)
    log.info(f'Uploaded a total of {files_count} files in {elapsed_time} seconds')


# upload_files_to_bucket()
upload_files_to_bucket_in_parallel()

import os

import configparser
import time

from google.cloud import storage


def get_elapsed_seconds(start_time):
    return round(time.time() - start_time, 2)


def upload_files_to_bucket():
    settings = configparser.ConfigParser()
    settings.read('./data/settings.ini')
    bucket_name = settings['blog_config']['google_cloud_bucket_name']
    source_root = settings['config']['wp_uploads_path']
    blob_prefix = settings['config']['blob_prefix']
    max_files_to_upload = int(settings['config']['max_files_to_upload'])
    print(f'Copying {max_files_to_upload} files from: {source_root} to bucket name prefixed with `{blob_prefix}`')

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    start_time = time.time()
    files_copied = 0
    for subdir, dirs, files in os.walk(os.path.join(source_root)):
        print(f'Processing directory: {subdir}')
        for file in files:
            if files_copied == max_files_to_upload:
                elapsed_time = get_elapsed_seconds(start_time)
                print(f'Uploaded {max_files_to_upload} files in {elapsed_time} seconds')
                return
            files_copied += 1
            # TODO: test with Windows paths (C:, D: etc.)
            partial_blob_name = f'{subdir}/{file}'.replace(source_root, '')
            blob_name = f'{blob_prefix}{partial_blob_name}'
            print(f'{files_copied}: Upload file {partial_blob_name}')
            file_path = os.path.join(subdir, file)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path)
            print(f'File uploaded. Public URL: {blob.public_url}')

    elapsed_time = get_elapsed_seconds(start_time)
    print(f'Uploaded a total of {files_copied} files in {elapsed_time} seconds')


upload_files_to_bucket()

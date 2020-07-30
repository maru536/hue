from google.cloud import storage as gcs
from django.core.files.temp import NamedTemporaryFile
import time
import os
import tarfile


TEMP_BUCKET = 'kimdc-temp-bucket'
TEMP_DIR = '/tmp'

class Storage(object):
    def __init__(self):
        self.client = gcs.Client()

    def download(self, table):
        bucket = self.client.bucket(TEMP_BUCKET)
        blobs = list(self.client.list_blobs(bucket, prefix=table+'/'))
        # compose_blob = bucket.blob('{}/{}'.format(table, 'compose.gzip'))
        # compose_blob.compose(blobs)

        temp_dir = '{}/{}/'.format(TEMP_DIR, table)
        try:
            if not(os.path.isdir(temp_dir)):
                os.mkdir(temp_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create directory!!!!!")
                raise

        zip_file = NamedTemporaryFile(suffix='.tar', dir=temp_dir)
        with tarfile.open(fileobj=zip_file, mode='w') as zip_file:
            for blob in blobs:
                temp_file = NamedTemporaryFile(
                    prefix=blob.name.split('/')[-1]+'-', 
                    dir=temp_dir)

                self.client.download_blob_to_file(blob, temp_file)
                zip_file.add(temp_file.name)

        return zip_file

    def delete(self, table):
        print(':::delete:::')
        bucket = self.client.bucket(TEMP_BUCKET)
        blobs = list(bucket.list_blobs(prefix=table+'/'))
        bucket.delete_blobs(blobs)
        
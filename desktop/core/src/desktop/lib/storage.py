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

    def download(self, gcs_dir):
        start = time.time()
        bucket = self.client.bucket(TEMP_BUCKET)
        blobs = list(bucket.list_blobs(prefix=gcs_dir))

        temp_dir = '{}/{}'.format(TEMP_DIR, gcs_dir)
        if not(os.path.isdir(temp_dir)):
            os.mkdir(temp_dir)

        start = time.time()
        merge_file = open(temp_dir+'/merge.tar', 'w+b')
        with tarfile.open(fileobj=merge_file, mode='w') as zip_file:
            print('pre_download:::', time.time()-start)
            download_time = 0
            compression_time = 0

            for blob in blobs:
                file_name = blob.name.split('/')[-1]
                dot_idx = file_name.find('.')
                
                if dot_idx >= 0:
                    temp_file = NamedTemporaryFile(
                        prefix=file_name[:dot_idx]+'-', 
                        suffix=file_name[dot_idx:],
                        dir=temp_dir)
                else:
                    temp_file = NamedTemporaryFile(
                        prefix=file_name,
                        dir=temp_dir
                    )

                download_start = time.time()
                self.client.download_blob_to_file(blob, temp_file)
                temp_file.file.flush()
                download_time += time.time()-download_start
                compression_start = time.time()
                zip_file.add(temp_file.name)
                temp_file.close()
                compression_time += time.time()-compression_start

            print('download_time:::', download_time)
            print('compression_time:::', compression_time)

        return merge_file

    def delete(self, gcs_dir):
        bucket = self.client.bucket(TEMP_BUCKET)
        blobs = list(bucket.list_blobs(prefix=gcs_dir))
        bucket.delete_blobs(blobs)
        
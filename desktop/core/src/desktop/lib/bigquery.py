from google.cloud import bigquery as bq
from desktop.lib.storage import Storage
from desktop.lib.temp_file import TempFile
import time

TEMP_DATASET = 'temp_dataset'
TEMP_BUCKET = 'kimdc-temp-bucket'

COMPRESSION_TO_FILE_EXTENSION = {
    bq.Compression.GZIP: 'gz',
    bq.Compression.SNAPPY: 'sn',
    bq.Compression.DEFLATE: 'de',
    bq.Compression.NONE: None
}

FILE_EXTENSION_TO_FORMAT = {
    'csv': bq.DestinationFormat.CSV,
    'json': bq.DestinationFormat.NEWLINE_DELIMITED_JSON,
    'avro': bq.DestinationFormat.AVRO
}

class BigQuery(object):
    def __init__(self, user_id):
        self.client = bq.Client()
        self.user_id = user_id
    
    def get_project_id(self):
        return self.client.project

    def _get_gcs_uri(self, gcs_dir, format, compression):
        uri = 'gs://{}/{}*.{}'.format(TEMP_BUCKET, gcs_dir, format)
        extension = COMPRESSION_TO_FILE_EXTENSION[compression]
        if extension:
            uri += '.%s'%extension

        return uri



    def query(self, sql, dest_table=None):
        config = None
        if dest_table:
            config = bq.QueryJobConfig(destination=dest_table_id)
        
        res = self.client.query(sql, job_config=config).result()

    def extract_table(self, table_id, gcs_dir, format='csv', compression='NONE'):
        config = bq.ExtractJobConfig(
            destination_format=FILE_EXTENSION_TO_FORMAT[format], 
            compression=compression)

        gcs_uri = self._get_gcs_uri(gcs_dir, format, compression)
        res = self.client.extract_table(
            table_id,
            gcs_uri,
            job_config=config
        ).result()
        return res.destination_uri_file_counts

    def del_table(self, table_id):
        res = self.client.delete_table(table_id)

    def download_table(self, table_id, format='csv', compression='NONE'):
        gcs = Storage()
        gcs_dir = '{}_{}/'.format(self.user_id.replace('.', '_'), str(time.time()).replace('.', ''))
        read_file = None
        try:
            extract_start = time.time()
            self.extract_table(table_id, gcs_dir, format, compression)
            print('extract table done:::', time.time()-extract_start)
            download_start = time.time()
            merge_file = gcs.download(gcs_dir)
            print('download_table_done:::', time.time()-download_start)
            read_file = TempFile(merge_file.name, 'rb')
            read_file.set_start()
            merge_file.close()
        finally:
            delete_start = time.time()
            gcs.delete(gcs_dir)
            print('delete_done:::', time.time()-delete_start)

        return read_file
        
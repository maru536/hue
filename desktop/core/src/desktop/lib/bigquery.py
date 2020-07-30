from google.cloud import bigquery as bq

TEMP_DATASET = 'temp_dataset'
TEMP_BUCKET = 'kimdc-temp-bucket'

class BigQuery(object):
    def __init__(self):
        self.client = bq.Client()

    def _get_table_id(self, table):
        return '.'.join([self.client.project, TEMP_DATASET, table])

    def _get_gcs_uri(self, table):
        #suffix = 'json' if format == 'NEWLINE_DELIMITED_JSON' else format
        #return 'gs://{}/{}/*.{}'.format(TEMP_BUCKET, table, suffix)
        return 'gs://{}/{}/*'.format(TEMP_BUCKET, table)

    def query(self, sql, dest_table=None):
        if dest_table:
            dest_table_id = self._get_table_id(dest_table)
            config = bq.QueryJobConfig(destination=dest_table_id)
        
        res = self.client.query(sql, job_config=config).result()
        print('query:::', res)

    def extract_table(self, table, format, compression=None):
        config = bq.ExtractJobConfig(destination_format=format, compression=compression)
        res = self.client.extract_table(
            self._get_table_id(table),
            self._get_gcs_uri(table),
            job_config=config
        ).result()
        print('extract_table:::', res.destination_uri_file_counts)
        return res.destination_uri_file_counts

    def del_table(self, table):
        table_id = self._get_table_id(table)
        res = self.client.delete_table(table_id)
        print('del_table:::', res)
        
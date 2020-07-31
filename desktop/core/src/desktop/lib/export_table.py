#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Common library to export either CSV or XLS.
"""
from future import standard_library
standard_library.install_aliases()
from builtins import next, object
import gc
import logging
import numbers
import openpyxl
import re
import six
import sys
import tablib

from django.http import StreamingHttpResponse, HttpResponse, FileResponse
from django.utils.encoding import smart_str
from django.utils.http import urlquote
from desktop.lib import i18n
from desktop.lib.bigquery import BigQuery
if sys.version_info[0] > 2:
  from io import BytesIO as string_io
else:
  from StringIO import StringIO as string_io


LOG = logging.getLogger(__name__)

DOWNLOAD_CHUNK_SIZE = 1 * 1024 * 1024 # 1MB
ILLEGAL_CHARS = r'[\000-\010]|[\013-\014]|[\016-\037]'
FORMAT_TO_CONTENT_TYPE = {
    'csv': 'application/csv',
    'avro': 'application/vnd.kafka.avro.v1+json',
    'json': 'application/json'
}


def nullify(cell):
  return cell if cell is not None else "NULL"

def file_reader(fh):
  """Generator that reads a file, chunk-by-chunk."""
  while True:
    chunk = fh.read(DOWNLOAD_CHUNK_SIZE)
    if chunk == '':
      fh.close()
      break
    yield chunk

def make_response(dataset, table, user_id, format='csv', compression='NONE', name='test', encoding=None, user_agent=None): #TODO: Add support for 3rd party (e.g. nginx file serving)
  """
  @param data An iterator of rows, where every row is a list of strings
  @param format Either "csv" or "xls"
  @param name Base name for output file
  @param encoding Unicode encoding for data
  """
  content_type = FORMAT_TO_CONTENT_TYPE.get(format, 'application/octet-stream')

  bq = BigQuery(user_id)
  table_file = bq.download_table('.'.join([bq.get_project_id(), dataset, table]), format, compression)
  resp = FileResponse(table_file, content_type=content_type)

  try:
    name = name.encode('ascii')
    format = format.encode('ascii')
    resp['Content-Disposition'] = b'attachment; filename="%s"' % name
  except UnicodeEncodeError:
    name = urlquote(name)
    if user_agent is not None and 'Firefox' in user_agent:
      # Preserving non-ASCII filename. See RFC https://tools.ietf.org/html/rfc6266#appendix-D, only FF works
      resp['Content-Disposition'] = 'attachment; filename*="%s"' % name
    else:
      resp['Content-Disposition'] = 'attachment; filename="%s"' % name

  return resp

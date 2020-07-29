## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from django.utils.translation import ugettext as _
%>

<%namespace name="comps" file="../components.mako" />

<form method="POST" class="form-horizontal" id="load-data-form" onsubmit="return false;">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Import Data')}</h2>
    </div>
    <div class="modal-body">
        <div class="format-select-group">
          <div class='plain'> Format </div>
          <select name="format" id="format" onchange="set_compression(this)">
          % for format in formats:
            <option value="${format}">${format}</option>
          % endfor
          </select>
        </div>

        <div class="compression-select-group">
          <div class='plain'> Compression </div>
          <select name="compression" id="compression">
          % for compression in compressions['CSV']:
            <option value="${compression}">${compression}</option>
          % endfor
          </select>
        </div>
    </div>

    <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <button class="btn btn-primary" id="export-data-btn">${_('Export')}</button>
    </div>
</form>


<style type="text/css">
   #filechooser {
     display: none;
     min-height: 100px;
     height: 380px;
     overflow-y: auto;
     margin-top: 10px;
   }

   .plain {
     font-size: 200%,
     font-weight: bold;
   }

   .compression-select-group {
     margin-top: 10px;
   }

   .modal-body {
     max-height: 540px;
   }

   .form-horizontal .controls {
     margin-left: 0;
   }

   .form-horizontal .control-label {
     width: auto;
     padding-right: 10px;
   }
</style>

<script type="text/javascript">
  $(document).ready(function () {
    $("#export-data-btn").click(function (e) {
      $.post("${ url('metastore:export_table', database=database, table=table.name) }",
        $("#load-data-form").serialize(),
        function (response) {
          if (response['status'] != 0) {
            if (response['status'] == 1) {
              $('#load-data-error').html(response['data']);
              $('#load-data-error').show();
            } else {
              $('#import-data-modal').html(response['data']);
            }
          } else {
            huePubSub.publish('notebook.task.submitted', response);
            $("#import-data-modal").modal("hide");
          }
        }
      ).always(function () {
        $("#load-data-submit-btn").button('reset');
        $("#load-data-submit-btn").removeAttr("disabled");
      });
    });
  });

  function set_compression(selected_format) {
    var value = selected_format.options[selected_format.selectedIndex].value;
    var target = document.getElementById("compression");

    csv_compressions = ["NONE", "GZIP"];
    json_compressions = ["NONE", "GZIP"];
    compressions = {
      "CSV": ["NONE", "GZIP"],
      "JSON": ["NONE", "GZIP"],
      'AVRO': ["SNAPPY", "DEFLATE"]
    };

    target.options.length = 0;

    for(var i=0, compression; compression=compressions[value][i]; i++) {
      var opt = document.createElement("option");
      opt.value = compression;
      opt.innerHTML = compression;
      target.appendChild(opt);
    }
  };
</script>

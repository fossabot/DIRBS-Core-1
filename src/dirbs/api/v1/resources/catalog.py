"""
DIRBS REST-ful data_catalog API module.

Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following
  disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
  products derived from this software without specific prior written permission.
- The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
  If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the
  details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
- Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
- This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
from psycopg2 import sql
from flask import jsonify

from dirbs.api.common.db import get_db_connection
from dirbs.api.common.catalog import _build_sql_query_filters
from dirbs.api.v1.schemas.catalog import CatalogFile


def catalog_api(max_results=None, **kwargs):
    """
    Data catalog API endpoint.

    :param max_results: max output results
    :param kwargs: input args
    :return: json response
    """
    # Build filters to be applied to the SQL query
    filters, filter_params = _build_sql_query_filters(**kwargs)

    query = sql.SQL("""SELECT array_agg(status ORDER BY run_id DESC)::TEXT[] AS status_list, dc.*
                         FROM (SELECT file_id,
                                      filename,
                                      file_type,
                                      compressed_size_bytes,
                                      modified_time,
                                      is_valid_zip,
                                      is_valid_format,
                                      md5,
                                      extra_attributes,
                                      first_seen,
                                      last_seen,
                                      uncompressed_size_bytes,
                                      num_records
                                 FROM data_catalog
                                      {filters}
                             ORDER BY last_seen DESC, file_id DESC
                                LIMIT %s) dc
                    LEFT JOIN (SELECT run_id, status, extra_metadata
                                 FROM job_metadata
                                WHERE command = 'dirbs-import') jm
                               ON md5 = (extra_metadata->>'input_file_md5')::uuid
                     GROUP BY file_id,
                              filename,
                              file_type,
                              compressed_size_bytes,
                              modified_time,
                              is_valid_zip,
                              is_valid_format,
                              md5,
                              extra_attributes,
                              first_seen,
                              last_seen,
                              uncompressed_size_bytes,
                              num_records
                     ORDER BY last_seen DESC, file_id DESC""")  # noqa Q444

    where_clause = sql.SQL('')
    if len(filters) > 0:
        where_clause = sql.SQL('WHERE {0}').format(sql.SQL(' AND ').join(filters))

    # Append max_results to the list of arguments to be supplied to the query.
    filter_params.append(max_results)

    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(cursor.mogrify(query.format(filters=where_clause), filter_params))
        resp = [CatalogFile().dump(rec._asdict()).data for rec in cursor]
        return jsonify(resp)

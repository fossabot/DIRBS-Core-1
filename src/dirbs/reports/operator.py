"""
Module for generating DIRBS operator-level reports.

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

from .base_operator_country import BaseOperatorCountryReport


class OperatorReport(BaseOperatorCountryReport):
    """Class used to generation operator-specific reports."""

    def __init__(self, conn, data_id, config, month, year, operator,
                 has_compliance_data=False):
        """Constructor."""
        self.operator_name = operator.name
        self.operator_id = operator.id
        self.mcc_mnc_pairs = operator.mcc_mnc_pairs
        super(OperatorReport, self).__init__(conn, data_id, config, month, year, 'operator_report.html',
                                             self.operator_id, has_compliance_data=has_compliance_data)

    def gen_report_data(self):
        """Overrides BaseOperatorCountryReport.gen_report_data."""
        data = self._gen_base_report_data()
        data['operator_id'] = self.operator_id
        data['operator_name'] = self.operator_name
        data['mcc_mnc_pairs'] = self.mcc_mnc_pairs
        return data

    @property
    def report_title(self):
        """Overrides BaseOperatorCountryReport.report_title."""
        return 'DIRBS operator report for {0} ({1:02d}/{2:04d})'.format(self.operator_name, self.month, self.year)

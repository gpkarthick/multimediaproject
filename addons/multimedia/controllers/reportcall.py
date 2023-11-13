##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import http
from odoo.http import request
import base64
from odoo.http import content_disposition
import smtplib
import datetime
from datetime import datetime, date
import io
import zipfile

class ReportCall(http.Controller):
        
    _cp_path = '/multimedia'

    @http.route('/multimedia/attachment_download', type='http', auth="public")
    def attachment_download(self, **data):
        curid = data.get('id')
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zipf:
            attachment_obj = request.env['ir.attachment']
            attachment_ids = attachment_obj.search([
                ('res_model', '=', 'farmer.insurance'),
                ('res_id', '=', curid)
            ])
            if attachment_ids:
                for attachment in attachment_ids:
                    file_name = attachment.name
                    file_data = base64.b64decode(attachment.datas)
                    zipf.writestr(file_name, file_data)
        buffer.seek(0)
        file_content = buffer.read()
        insurance_ids = http.request.env['farmer.insurance'].search([('id', '=', data.get('id')), ('id', '>', 745)])

        if file_content and insurance_ids:
            filename = str(insurance_ids.form_application_no) + '.zip'
            return request.make_response(file_content, headers=[
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', content_disposition(filename))
            ])

    @http.route('/multimedia/multi_attachment_download', type='http', auth="public")
    def multi_attachment_download(self, **data):
        curid = data.get('id')
        start = data.get('start_no')
        end = data.get('end_no')
        insurance_numbers = data.get('insurance_numbers')
        if start and end:
          print (start,type(start),insurance_numbers,type(insurance_numbers))
          numbers = [i for i in range(int(start), int(end) + 1)]
          buffer = io.BytesIO()
          insurance_check_ids = request.env['farmer.insurance'].search([('form_application_no', 'in', numbers), ('id', '>', 745)])
          if insurance_check_ids:
            with zipfile.ZipFile(buffer, 'w') as zipf_bulk:
                insurance_ids = request.env['farmer.insurance'].search([('form_application_no', 'in', numbers), ('id', '>', 745)])
                for insurance in insurance_ids:
                    subfolder_buffer = io.BytesIO()
                    with zipfile.ZipFile(subfolder_buffer, 'w') as zipf_individual:
                        attachment_obj = request.env['ir.attachment']
                        attachment_ids = attachment_obj.search([
                            ('res_model', '=', 'farmer.insurance'),
                            ('res_id', '=', insurance.id)
                        ])
                        if attachment_ids:
                            for attachment in attachment_ids:
                                file_name = attachment.name
                                file_data = base64.b64decode(attachment.datas)
                                zipf_individual.writestr(file_name, file_data)

                    subfolder_buffer.seek(0)
                    zipf_bulk.writestr(f'farmer_{insurance.form_application_no}.zip', subfolder_buffer.read())

            buffer.seek(0)
            file_content = buffer.read()

            if file_content:
                filename = 'bulk_attachments.zip'
                return request.make_response(file_content, headers=[
                    ('Content-Type', 'application/zip'),
                    ('Content-Disposition', content_disposition(filename))
                ])
        if insurance_numbers:
            integer_list = [int(x) for x in insurance_numbers.split(',')]        
            insurance_check_ids = request.env['farmer.insurance'].search([('form_application_no', 'in', integer_list), ('id', '>', 745)])
            if insurance_check_ids:
                with zipfile.ZipFile(buffer, 'w') as zipf_bulk:
                  insurance_ramdom_ids = request.env['farmer.insurance'].search([('form_application_no', 'in', integer_list), ('id', '>', 745)])
                  for insurance in insurance_ramdom_ids:
                      subfolder_buffer = io.BytesIO()
                      with zipfile.ZipFile(subfolder_buffer, 'w') as zipf_individual:
                          attachment_obj = request.env['ir.attachment']
                          attachment_ids = attachment_obj.search([
                              ('res_model', '=', 'farmer.insurance'),
                              ('res_id', '=', insurance.id)
                          ])
                          if attachment_ids:
                              for attachment in attachment_ids:
                                  file_name = attachment.name
                                  file_data = base64.b64decode(attachment.datas)
                                  zipf_individual.writestr(file_name, file_data)

                      subfolder_buffer.seek(0)
                      zipf_bulk.writestr(f'farmer_{insurance.form_application_no}.zip', subfolder_buffer.read())

                buffer.seek(0)
                file_content = buffer.read()

                if file_content:
                    filename = 'bulk_attachments.zip'
                    return request.make_response(file_content, headers=[
                        ('Content-Type', 'application/zip'),
                        ('Content-Disposition', content_disposition(filename))
                    ])
          


    # @http.route('/multimedia/attachment_download', type='http', auth="public")
    # def attachment_download(self, **data):
    #     print ("+++++++++++++++++++++++++")
        
    #     print ("________________________")
    #     curid = data.get('id')
    #     buffer = io.BytesIO()
    #     with zipfile.ZipFile(buffer, 'w') as zipf:
    #         attachment_obj = http.request.env['ir.attachment']
    #         attachment_ids = attachment_obj.search([
    #             ('res_model', '=', 'farmer.insurance'),
    #             ('res_id', '=', curid)
    #         ])
    #         if attachment_ids:
    #             for attachment in attachment_ids:
    #                 # file_name = attachment.name  # Use 'name' instead of 'datas_fname'
    #                 file_data = base64.b64decode(attachment.datas)
    #                 zipf.writestr(file_name, file_data)
    #         insurance_ids = http.request.env['farmer.insurance'].search([('id', '=', data.get('id'))])
    #         file_content = base64.b64decode(zipf)
    #         filename = insurance_ids.name
    #         if file_content and filename:
    #             return request.make_response(file_content,
    #                                          headers=[('Content-Type', 'application/octet-stream'),
    #                                                   ('Content-Disposition', content_disposition(filename))])

        # buffer.seek(0)
        # file_name = 'attachments.zip'
        # content_type = 'application/zip'
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': '/web/content/?model={}&id={}&field=attachment_ids&filename_field=name&download=true'.format(self._name, self.id),
        #     'target': 'self',
        #     'res_id': self.id,
        #     'headers': [('Content-Type', content_type), ('Content-Disposition', content_disposition(file_name))],
        # }
                                                      
    @http.route('/multimedia/insurance_preview', type='http', auth="public")
    def insurance_preview(self, **data):
        farmer_insurance_obj = http.request.env['farmer.insurance']
        curid = data.get('id')
        farmer_insurance_ids = farmer_insurance_obj.search([('id', '=', curid)])
        html = '''
                    <html>
                       <head>
                            <style>
                            table {
                              font-family: arial, sans-serif;
                              border-collapse: collapse;
                              width: 40%;
                            }
                            
                            td, th {
                              border: 1px solid #dddddd;
                              text-align: left;
                              padding: 8px;
                              line-height: 1.5;
                            }
                            
                            tr:nth-child(even) {
                              background-color: #eeedec;
                            }
                            
                            .evaluation_head {
                                width:70%;
                                border: 1px solid black;
                                background-color: burlywood;
                            }
                            .evaluation_data {
                                    width:100%;
                                            }
                            .evaluation_data td {
                                border: none;
                                font-size: 14px;
                                line-height:100%;
                                padding-right:4px;
                                padding-left: 8px;
                                    }
                            .evaluation_data p {
                                font-size:14px;
                                text-align:left;
                                font-weight: bold;
                                color: maroon;
                                margin-left:2px;
                            }           html+= """
                            
                            
                            </style>
                            </head>
                            <body>
                            
                            
                            <h2 style="text-align: center;width:40%;color:#2b8088;">Insurance Datas</h2>
                                <table>
                                      <tr>
                                        <th style="width:20%">Name</th>
                                        <th style="width:20%">Details</th>
                                      </tr>
                            '''

        for insurance in farmer_insurance_ids:
            aadhar_name = ''
            aadhar_no = ''
            community_type = ''
            farmer_age = 0
            farmer_category_type = ''
            farmer_state_id = farmer_district_id =  farmer_village_id = pincode = farmer_addr = ''
            state2_id = district_id = subdistrict_id = block_id = firka_id = village_id = ''
            sowing_date = ''
            
            if insurance.aadhar_name:
                aadhar_name = insurance.aadhar_name
            if insurance.aadhar_no:
                aadhar_no = insurance.aadhar_no
            if insurance.community_type:
                community_type = insurance.community_type
            if insurance.farmer_category_type:
                farmer_category_type = insurance.farmer_category_type
            if insurance.farmer_age:
                farmer_age = insurance.farmer_age

            if insurance.farmer_state_id:
                farmer_state_id = insurance.farmer_state_id.name
            if insurance.farmer_district_id:
                farmer_district_id = insurance.farmer_district_id.name
            if insurance.farmer_village_id:
                farmer_village_id = insurance.farmer_village_id.name
            if insurance.pincode:
                pincode = insurance.pincode
            if insurance.farmer_addr:
                farmer_addr = insurance.farmer_addr

            if insurance.state2_id:
                state2_id = insurance.state2_id.name
            if insurance.district_id:
                district_id = insurance.district_id.name
            if insurance.subdistrict_id:
                subdistrict_id = insurance.subdistrict_id.name
            if insurance.block_id:
                block_id = insurance.block_id.name
            if insurance.firka_id:
                firka_id = insurance.firka_id.name
            if insurance.village_id:
                village_id = insurance.village_id.name
            if insurance.sowing_date:
                sowing_date = datetime.strptime(str(insurance.sowing_date), "%Y-%m-%d").date().strftime("%d-%m-%Y")
            html += """
            <tr>
                <td>""" + 'Farmer Name' + """</td>
                <td>""" + insurance.farmer_name  + """</td>
              </tr>
              <tr>
                <td>""" + 'IFSC Code' + """</td>
                <td>""" + insurance.ifsc_code + """</td>
              </tr>
              <tr>
                <td>""" + 'Bank Account No' + """</td>
                <td>""" + insurance.bank_account_no + """</td>
              </tr>
              <tr>
                <td>""" + 'Name as per Passbook' + """</td>
                <td>""" + insurance.farmer_name + """</td>
              </tr>
              <tr>
                <td>""" + 'Name as per Aadhar' + """</td>
                <td>""" + aadhar_name + """</td>
              </tr>
              <tr>
                <td>""" + 'Aadar No' + """</td>
                <td>""" + aadhar_no + """</td>
              </tr>
              
              <tr>
                <td>""" + 'Relative Name' + """</td>
                <td>""" + insurance.relative_name + """</td>
              </tr>
              <tr>
                <td>""" + 'Mobile No' + """</td>
                <td>""" + insurance.mobile_no + """</td>
              </tr>
              <tr>
                <td>""" + 'Age' + """</td>
                <td>""" + str(farmer_age) + """</td>
              </tr>
              <tr>
                <td>""" + 'Gender' + """</td>
                <td>""" + insurance.gender_type + """</td>
              </tr>
              <tr>
                <td>""" + 'Caste Category' + """</td>
                <td>""" + community_type + """</td>
              </tr>
              <tr>
                <td>""" + 'Farmer Type' + """</td>
                <td>""" + farmer_category_type + """</td>
              </tr>
              <tr>
                <td>""" + 'State' + """</td>
                <td>""" + farmer_state_id + """</td>
              </tr>
              <tr>
                <td>""" + 'District' + """</td>
                <td>""" + farmer_district_id + """</td>
              </tr>              
              <tr>
                <td>""" + 'Residential Village/Town' + """</td>self.id
                <td>""" + farmer_addr + """</td>
              </tr>
              
              <tr>
                <td>""" + 'State' + """</td>
                <td>""" + state2_id + """</td>
              </tr>
              <tr>
                <td>""" + 'District' + """</td>
                <td>""" + district_id + """</td>
              </tr>
              <tr>
                <td>""" + 'Sub District' + """</td>
                <td>""" + subdistrict_id + """</td>
              </tr>
              <tr>
                <td>""" + 'Block' + """</td>
                <td>""" + block_id + """</td>
              </tr>
              <tr>
                <td>""" + 'Firka' + """</td>
                <td>""" + firka_id + """</td>
              </tr>
              <tr>
                <td>""" + 'Village' + """</td>
                <td>""" + village_id + """</td>
              </tr>
              <tr>
                <td>""" + 'Sowing Date' + """</td>
                <td>""" + sowing_date + """</td>
              </tr>
               
            """

            html += """
            </table>
            """

            html+= """
                <h2 style="text-align: center;width:40%;color:#2b8088;">Crop Details</h2>
            """

            html+= """
            <table align="left" width="100%">
                <tr bgcolor='#CCCCFF'>
                    <th>Survey No</th>
                    <th>Area Insured</th>
                </tr>
            """

            count = 0

            for line in insurance.crop_line_ids:
                count += 1
                if count % 2 == 0:
                    color = "#C9E2E9"
                else:
                    color = "#fce4ec"
                html += """<tr bgcolor='""" + color + """'>
                       <td align='right'>""" + str(line.survey_no) + ' / ' + str(line.khasra_no) + """</td>
                       <td align='right'>""" + str(line.area_insured) + """</td>
                       </tr>
                    """
        html += """
                    </table>
                    
                     <h2 style="text-align: center;width:40%;color:#2b8088;">Total Area Insured: """ + str( '%.3f' % insurance.total_area_insured) +"""</h2>
                      <h2 style="text-align: center;width:40%;color:#2b8088;">Total Premium Paid : """ +str( '%.2f' % insurance.total_premium_paid) +"""</h2>
                    """




        html += '''        
                        </body>
                    </html>
                    '''
        return html
        

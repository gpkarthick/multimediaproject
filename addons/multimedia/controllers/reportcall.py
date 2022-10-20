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

class ReportCall(http.Controller):
        
    _cp_path = '/multimedia'
                                                      
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
                <td>""" + 'Residential Village/Town' + """</td>
                <td>""" + farmer_village_id + """</td>
              </tr>
              <tr>
                <td>""" + 'Pincode' + """</td>
                <td>""" + pincode + """</td>
              </tr>
              <tr>
                <td>""" + 'Address' + """</td>
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
                <td>""" + 'Crop' + """</td>
                <td>""" + 'CROP' + """</td>
              </tr>
              <tr>
                <td>""" + 'Sowing Date' + """</td>
                <td>""" + sowing_date + """</td>
              </tr>
              <tr>
                <td>""" + 'Survey No' + """</td>
                <td>""" + insurance.farmer_name + """</td>
              </tr>
              <tr>
                <td>""" + 'Insured Area' + """</td>
                <td>""" + '' + """</td>
              </tr>   
            """
        html += '''        
                        </body>
                    </html>
                    '''
        return html
        

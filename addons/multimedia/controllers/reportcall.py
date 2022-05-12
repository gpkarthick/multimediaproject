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
                                                      
    @http.route('/marine/image_preview', type='http', auth="public")
    def image_preview_download(self, **data):
        pan_obj = http.request.env['pan.form']
        curid = data.get('id')
        pan_ids = pan_obj.search([('id', '=', curid)])
        html = '''
                    <html>
                        <head>
                        </head>
                            <body>
                                <div align="center">
                            '''
        for x in pan_ids:
            field_list = []
            if x.pan_type == 'major':
                field_list = ['writtern_form','pan_front','pan_back']
            html += '''<h1 style="text-align:center;">Pan Documents ( ''' + 'Pan Details' + ''' )</h1> '''
            if field_list:
                for ll in field_list:
                    print (ll)
                    value = x.writtern_form.decode("utf-8")
                    print (value)
                    html += '''
                                    <img src="data:image/;base64,''' + value + '''" alt="Red dot" style="width:900px;border-radius: 15px;"/>
                                 '''
        html += '''
                            </div>
                        </body>
                    </html>
                    '''
        return html
        

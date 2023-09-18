from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PMJAYHealthInsurance(models.Model):
    _name = 'pmjay.health.insurance'
    _description = 'PMJAY Health Insurance'
    _order = "id DESC"

    name = fields.Char('Ration Card Number', required=True)
    # member_name = fields.Char('Name', required=True)
    kyc_update = fields.Boolean('KYC Update')
    # amount_paid = fields.Boolean('Amount Paid', required=True)
    # updated_date = fields.Datetime(string='Updated Date', readonly=True)
    serial_no = fields.Integer('Serial No', required=True)
    mobile_no = fields.Integer('Mobile No')
    alternate_mobile_no = fields.Integer('Alternate Mobile No')
    insurance_id = fields.Many2one('pmjay.report', string='PMJAY Report')
    pmjay_village_id = fields.Many2one('pmjay.village', string='PMJAY Village')
    create_date = fields.Datetime(string='Created Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', readonly=True, default='draft')
    pmjay_hi_members_ids = fields.One2many('pmjay.member.line', 'pmjay_id', "Family Members")

    # @api.depends('name', 'member_name', 'state')
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = str(record.serial_no) + ' - ' + record.name + ' - ' + record.member_name + ' - ' + record.state
    #         result.append((record.id, name))
    #     return result

class PMJAYDistrict(models.Model):
    _name = 'pmjay.district'
    _description = 'PMJAY District Master'
    _order = "name asc"

    name = fields.Char('District Name', required=True)
    district_code = fields.Char('District Code')
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    block_ids = fields.One2many('pmjay.block', 'district_id', "Block Records")
    active = fields.Boolean('Active', default=True)

    @api.constrains('name')
    def _district_name_unique(self):
        lst = [x.name.lower().replace(" ", "") for x in self.search([('id', '!=', self.id)])]
        if self.name.lower().replace(" ", "") in lst:
            raise ValidationError(_('The Same District is already available'))

class PMJAYBlock(models.Model):
    _name = 'pmjay.block'
    _description = 'PMJAY Block Master'
    _order = "name asc"

    name = fields.Char('Block Name', required=True)
    block_code = fields.Char('Block Code')
    panchayat_ids = fields.One2many('pmjay.panchayat', 'block_id', "Panchayat Records")
    active = fields.Boolean('Active', default=True)
    district_id = fields.Many2one('pmjay.district', string='District', required=True)

class PMJAYPanchayat(models.Model):
    _name = 'pmjay.panchayat'
    _description = 'PMJAY Panchayat Master'
    _order = "name asc"

    name = fields.Char('Panchayat Name', required=True)
    panchayat_code = fields.Char('Panchayat Code')
    village_ids = fields.One2many('pmjay.village', 'panchayat_id', "Village Records")
    active = fields.Boolean('Active', default=True)
    block_id = fields.Many2one('pmjay.block', string='Block', required=True)
    district_id = fields.Many2one('pmjay.district', string='District', required=True)

class PMJAYVillage(models.Model):
    _name = 'pmjay.village'
    _description = 'PMJAY Village'
    _order = "id DESC"

    name = fields.Char('Name', required=True)
    village_code = fields.Char('Village Code', required=True)
    panchayat_id = fields.Many2one('pmjay.panchayat', string='Panchayat', required=True)
    block_id = fields.Many2one('pmjay.block', string='Block', required=True)
    district_id = fields.Many2one('pmjay.district', string='District', required=True)

class PMJAYHealthInsuranceUpdate(models.Model):
    _name = 'pmjay.health.insurance.update'
    _description = 'PMJAY Health Insurance Update'
    _order = "id DESC"

    @api.constrains('pmjay_id', 'mobile_no','alternate_mobile_no','kyc_update','amount_paid')
    def pmjay_update(self):
        for order in self:
            if not order.mobile_no:
                raise ValidationError(_('Please Enter Mobile No'))
            if order.pmjay_id.state == 'draft':
                if order.kyc_update and order.amount_paid:
                    if not order.pmjay_id.updated_date:
                        order.pmjay_id.update({
                            'updated_date': fields.Datetime.now()
                        })
                    order.pmjay_id.update({
                        'kyc_update': True,
                        'amount_paid': True,
                        'mobile_no':order.mobile_no,
                        'alternate_mobile_no':order.alternate_mobile_no,
                        'state':'done'
                    })

    pmjay_id = fields.Many2one('pmjay.health.insurance', string='Ration Card No', required=True)
    name = fields.Char('Ration Card Number', required=True)
    member_name = fields.Char('Name', required=True)
    kyc_update = fields.Boolean('KYC Update', required=True)
    amount_paid = fields.Boolean('Amount Paid', required=True)
    serial_no = fields.Integer('Serial No', required=True)
    mobile_no = fields.Integer('Mobile No', required=True)
    alternate_mobile_no = fields.Integer('Alternate Mobile No', required=True)
    pmjay_village_id = fields.Many2one('pmjay.village', string='PMJAY Village', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', readonly=True, default='draft')

    @api.onchange('pmjay_id')
    def onchange_user_id(self):
        if self.pmjay_id:
            self.name = self.pmjay_id.name
            self.member_name = self.pmjay_id.member_name

class PmjayMembersLine(models.Model):
    _name = 'pmjay.member.line'
    _description = 'Pmjay Family Members Line'
    _order = "id asc"

    name = fields.Char('Name', required=True)
    kyc_update = fields.Boolean('KYC Update', required=True)
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')
    pmjay_id = fields.Many2one('pmjay.health.insurance', string='PMJAY ID')

class PmjayReport(models.Model):
    _name = 'pmjay.report'
    _description = 'Pmjay Report'
    _order = "id asc"

    name = fields.Char('Name', required=True)
    pmjay_district_id = fields.Many2one('pmjay.district', string='District')
    pmjay_block_id = fields.Many2one('pmjay.block', string='Block')
    pmjay_panchayat_id = fields.Many2one('pmjay.panchayat', string='Panchayat')
    pmjay_village_ids = fields.Many2many('pmjay.village', 'pmjay_village_rel', 'pmjay_id', 'village_id',
                                           string='Villages')
    pmjay_health_insurance_ids = fields.One2many('pmjay.health.insurance', 'insurance_id', "Family Records")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft')
    import_file = fields.Binary('Import CSV File')
    file_name = fields.Char('Name', required=True)

    def pmjay_member_kyc_print(self):
        return self.env.ref('multimedia.action_report_pmjay_kyc_data').report_action(self)

    def upload_pmjay_ration_data(self):
        import base64
        import csv
        import io
        for order in self:
            count = 0
            decrypted = base64.b64decode(order.import_file).decode('utf-8')
            with io.StringIO(decrypted) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                parent_list = []
                child_list = []
                for row in reader:
                    # if not row:
                    #     break
                    count += 1
                    # print (count,len(row),"----------------")
                    if count > 1:
                        parent_data = {
                            'name': row[1],
                            'serial_no': row[0],
                            'insurance_id':self.id
                        }
                        parent_list.append(parent_data)

                        if row[3] == 'Y':
                            val = True
                        if row[3] == 'N':
                            val = False

                        child_data = {
                            'name': row[2],
                            # 'parent_id': parent_record.id,
                            'kyc_update': val,
                        }
                        child_list.append(child_data)

                        if not row[0]:
                            print (parent_list,"ccccccccccccc")
                            print (parent_list[:-1][-1],child_list[:-1],"--------------------")
                            parent_list = parent_list[:-1][-1]
                            child_list = child_list[:-1]
                            result = []
                            print (parent_list,"ffffffffff")
                            if parent_list:
                                parent = self.env['pmjay.health.insurance'].create(parent_list)
                                print (parent,"xxxxxxxxxxxxxxx")
                                for line in child_list:
                                    result.append((0, 0, line))
                                    # line.update({'pmjay_id':parent.id})
                                parent.write({'pmjay_hi_members_ids':result})

                                    # self.env[self.child_model.model].create(child_data)
                            # parent_list = list(set(parent_list))
                            # child_list = list(set(child_list))
                            parent_list = []
                            child_list = []

class PmjayRationSearch(models.Model):
    _name = 'pmjay.ration.search'
    _description = 'Pmjay ration Search'
    _order = "id asc"

    pmjay_health_insurance_id = fields.Many2one('pmjay.health.insurance', string='PMJAY Ration ID')
    doc_html = fields.Html('Family Members')
    name = fields.Char('Name')

    @api.onchange('pmjay_health_insurance_id')
    def onchange_user_id(self):
        html = ''
        if self.pmjay_health_insurance_id:
            # html = """
            #     <html>
            #     <body>
            #                Sample      
                    
            #     </body>
            #     </html> 
            # """
            # self.doc_html = html


            html = """
						<html>
						  <body>
					"""


            
            html += """
                    
                        <table cellspacing="2.5" cellpadding="3.5" border="0"  width="500">
                            <td>        
                                <table cellspacing="0.0" cellpadding="6.3" border="1" width="500"> 
                                    
                                    <tr height="22" align="center">
                                        <th width="70" colspan="3" bgcolor='#CC99CC' >Member List</th>
                                    </tr>
                                    <tr bgcolor='#CCCCFF' align='center'>
                                        <th>Member Name</th> 
                                        <th>Gender</th>                               
                                        <th>Kyc Update</th>
                                    </tr>
                                    """
            for row in self.pmjay_health_insurance_id.pmjay_hi_members_ids:
                color = "#fce4ec"
                # if pending_request_list.index(row) % 2 == 0:
                #     color = "#C9E2E9"
                # else:
                #     color = "#fce4ec"
                gender = ''
                kyc_update = ''
                print (row.kyc_update,"xxxxxxxxxxxx")
                if row.gender:
                    gender = row.gender
                if row.kyc_update == True:
                    kyc_update = '\u2717'
                if row.kyc_update == False:
                    kyc_update = '\u2713'
                html += """
                        <tr bgcolor='""" + color + """'>
                             <td align='left'>""" + row.name + """</td>
                             <td align='center'>""" + gender + """</td>
                             <td align='center'>""" + kyc_update + """</td>
                        </tr> """
            html += """    
                        </table>
                    """
            
            html += """
                    </body>
                </html> 
                    """
            print (html,"xxxxxxxxxxxxx")
            self.doc_html = html



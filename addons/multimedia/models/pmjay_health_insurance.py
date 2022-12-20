from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PMJAYHealthInsurance(models.Model):
    _name = 'pmjay.health.insurance'
    _description = 'PMJAY Health Insurance'
    _order = "id DESC"

    name = fields.Char('Ration Card Number', required=True)
    member_name = fields.Char('Name', required=True)
    kyc_update = fields.Boolean('KYC Update', required=True)
    amount_paid = fields.Boolean('Amount Paid', required=True)
    updated_date = fields.Datetime(string='Updated Date', readonly=True)
    serial_no = fields.Integer('Serial No', required=True)
    mobile_no = fields.Integer('Mobile No', required=True)
    alternate_mobile_no = fields.Integer('Alternate Mobile No', required=True)
    pmjay_village_id = fields.Many2one('pmjay.village', string='PMJAY Village')
    create_date = fields.Datetime(string='Created Date', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', readonly=True, default='draft')

    @api.depends('name', 'member_name', 'state')
    def name_get(self):
        result = []
        for record in self:
            name = str(record.serial_no) + ' - ' + record.name + ' - ' + record.member_name + ' - ' + record.state
            result.append((record.id, name))
        return result

class PMJAYVillage(models.Model):
    _name = 'pmjay.village'
    _description = 'PMJAY Village'
    _order = "id DESC"

    name = fields.Char('Name', required=True)

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





from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountVerification(models.Model):
    _name = 'account.verification'
    _description = 'Account Verification'
    _order = "name asc"

    name = fields.Char('Ref Number', required=True, default=lambda self: _('New'), readonly=True)
    transaction_mode = fields.Char('Transaction Mode', required=True, default='IMPS')
    transaction_date = fields.Datetime(string='Transaction Date', readonly=True, default=fields.Datetime.now)
    sender_name = fields.Char(string='Sender Name', required=True, default='Prime')
    order_id = fields.Char(string='Order ID', required=True, default=lambda self: _('New'), readonly=True)
    benificiary_name = fields.Char(string='Benificiary Name', required=True)
    ifsc_code = fields.Char('IFSC Code', size=32, track_visibility='always', required=True)
    bank_account_no = fields.Char('Account Number', size=32, track_visibility='always', required=True)
    branch_name = fields.Char('Branch Name', size=60, required=True)
    bank_name = fields.Char('Bank Name', size=60, required=True)
    mobile_no = fields.Char(string='Mobile No', required=True)
    transation_amt = fields.Float(string='Transation Amount', required=True, default=1)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('account.verification.ref') or _('New')
        if vals.get('order_id', _('New')) == _('New'):
            vals['order_id'] = self.env['ir.sequence'].next_by_code('account.verification.order') or _('New')
        return super(AccountVerification, self).create(vals)

    @api.onchange('ifsc_code')
    def onchange_ifsc_code(self):
        import requests
        datas = {}
        if not self.ifsc_code:
            datas = {'branch_name': '',
                     'bank_name': ''}
        if self.ifsc_code:
            datas = {}
            result = ''
            url = "https://ifsc.razorpay.com/{0}".format(self.ifsc_code)
            try:
                result = requests.get(url).json()
            except Exception as e:
                raise UserError(_('Wrong IFSC Code, Please check it (%s).') % e)
            if result == 'Not Found':
                datas.update({
                    'branch': '',
                    'bank_address': 'Wrong IFSC Code'
                })
            else:
                datas.update({
                    'branch_name': result['BRANCH'].replace('┬á', ''),
                    'bank_name': result['BANK'].replace('┬á', ''),
                })
        return {'value': datas}
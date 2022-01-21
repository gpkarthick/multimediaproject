from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PanForm(models.Model):
    _name = "pan.form"
    _description = "Pan form"
    _order = 'id desc'

    def _default_form_type(self):
        return self.env.context.get('form_type')

    name = fields.Char(string='Pan No')
    party_name = fields.Char(string='Party Name')
    mobile_no = fields.Char(string='Mobile No')
    address = fields.Text(string='Address')
    seq_no = fields.Char(string='Sequence No', size=18, readonly=True, default=lambda self: _('New'))
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    attachment = fields.Binary(string="Image", attachment=True)
    form_type = fields.Selection([('new_pan', 'New Pan'), ('update_pan', 'Update Pan'), ('child_pan', 'Child Pan')], string='Type',
                             readonly=True, default=_default_form_type)
    state = fields.Selection([('draft', 'Draft'), ('processing', 'Processing'), ('done', 'Done')], string='Status', readonly=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('seq_no', _('New')) == _('New'):
            vals['seq_no'] = self.env['ir.sequence'].next_by_code('pan.form') or _('New')
        return super(PanForm, self).create(vals)

    def action_process(self):
        self.write({'state': 'processing'})

    def action_reset(self):
        self.write({'state': 'draft'})

    def action_done(self):
        if not self.mobile_no:
            raise UserError(_('Please enter the mobile Number.'))
        if len(self.mobile_no) != 10:
            raise UserError(_('Please enter the 10 Digit mobile Number.'))
        if not self.name:
            raise UserError(_('Please enter the PAN Number.'))
        if not self.party_name:
            raise UserError(_('Please enter the Party Name'))
        if not self.address:
            raise UserError(_('Please enter the Party Address'))
        self.write({'state': 'done'})
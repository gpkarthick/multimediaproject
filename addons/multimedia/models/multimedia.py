from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class MultimediaEBBill(models.Model):
    _name = "multimedia.eb.bill"
    _description = "Multi Media EB Bill Operation"
    _order = 'due_date desc'
        
    name = fields.Char(string='EB Bill No', required=True)
    auto_no = fields.Char(string='EB Bill No', default=lambda self: self.env['ir.sequence'].next_by_code('multimedia.eb.bill.auto.no'))
    seq_no = fields.Char(string='Seq No', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    bill_name = fields.Char(string='Bill Name', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    paid_date = fields.Datetime(string='Paid Date')
    mobile_no = fields.Char(string='Mobile No')
    due_amount = fields.Float(string='Due Amount', required=True)
    paid_amount = fields.Float(string='Paid Amount', required=True)    
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    payment_mode_id = fields.Many2one('payment.mode', string='Payment Through')
    attachment = fields.Binary(string="Image", attachment=True)
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], string='Status', readonly=True, default='draft')

    def bill_print(self):
        return self.env.ref('multimedia.action_report_multimedia').report_action(self)        
    
    def get_invoice_date_time(self, current_date):  
        from datetime import datetime
        from datetime import timedelta
        changed_format_time_value = ''  
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        addtime =  datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
        changed_format_time_value = datetime.strptime(str(addtime), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
        return str(changed_format_time_value)
                
    def action_pay_bill(self):
        if self.due_amount == 0:
            raise UserError(_('Please enter the customer due Amount'))        
        if self.mobile_no and len(self.mobile_no) != 10:
            raise UserError(_('Please enter the 10 Digit mobile Number.'))
        if self.paid_amount == 0:
            raise UserError(_('Please enter the Paid Amount'))
        if not self.payment_mode_id:
            raise UserError(_('Please enter the payment made by'))
        if self.seq_no == 'New':
            seq = self.env['ir.sequence'].sudo().next_by_code('multimedia.eb.bill') or 'New'
            self.write({'seq_no':seq})
        if self.paid_date:
            self.write({'state':'paid'})
        else:
            self.write({'state':'paid','paid_date':fields.Datetime.now()})
    
class PaymentMode(models.Model):
    _name = "payment.mode"
    _description = "Payment Mode operation"    
        
    name = fields.Char(string='Name', required=True)

class Attachment(models.Model):
    _inherit = 'ir.attachment'

    attach_rel = fields.Many2many('res.partner', 'attachment', 'attachment_id3', 'document_id',string="Attachment", invisible=1 )
        
class InvoicePayment(models.Model):
    _name = "invoice.payment"
    _description = "EB Bill Payments"    
        
    name = fields.Char(string='Seq No', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    payment_type = fields.Selection([('credit', 'Credit'),('debit', 'debit')], string='Type', readonly=True, default='credit')
    date = fields.Date(string='Date', required=True)
    bank_id = fields.Many2one('payment.mode', string='Bank', required=True)
    amount = fields.Float(string='Amount', required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', readonly=True, default='draft')    
    note = fields.Text('Remarks')
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    
    def action_confirm(self):
        self.write({'state':'done'})
        


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"
    _order = "name"

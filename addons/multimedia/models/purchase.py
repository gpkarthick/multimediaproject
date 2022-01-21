from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError, Warning
from datetime import datetime, timedelta

class PurchaseBills(models.Model):
    _name = "purchase.bills"
    _order = 'id desc'
    _description = "Purchase Bills"

    @api.depends('bill_lines','purchase_date','partner_id')
    def _amount_all(self):
        """
        Compute the total amounts of the Purchases.
        """
        for order in self:
            total = 0.0
            for line in order.bill_lines:
                total += line.subtotal    
                line.write({'purchase_date': order.purchase_date,
                            'partner_id': order.partner_id.id
                    })            
            order.update({
                'total_amount': total,
            })  
    
    name = fields.Char('Sequence No', size=18, readonly=True, default=lambda self: _('New'))
    purchase_date = fields.Date('Purchase Date', required=True, select=True)
    partner_id = fields.Many2one('res.partner', 'Party', required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    currency_id = fields.Many2one("res.currency", 'Currency', readonly=True)
    bill_lines = fields.One2many('purchase.bill.line', 'bill_id', 'Bill Lines')
    total_amount = fields.Float(string='Total Amount', store=True, readonly=True, compute='_amount_all', digits='Product Unit of Measure')
    state = fields.Selection([('draft','Draft'),('reset','Reset'),('done','Done')], 'State', readonly=True, index=True, tracking=3, default='draft')    
    reason = fields.Text('Reason')
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
        
    def action_confirm(self):
        if self.name == 'New':
            seqval = self.env['ir.sequence'].sudo().next_by_code('purchase.bills') or 'New'
            self.write({'name': seqval})
        for order in self:
            for line in order.bill_lines:
                line.write({'purchase_date': order.purchase_date,
                            'partner_id': order.partner_id.id
                    })
        return self.write({'state': 'done'})
        
    def button_reset(self):
        self.write({'state': 'draft'})

class PurchaseBillLine(models.Model):
    _name = "purchase.bill.line"
    _order = 'id desc'
    _description = "Purchase Bill Line"
    
    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            total = line.price_unit * line.product_uom_qty
            line.update({
                'subtotal': total
            })
    
    product_category_id = fields.Many2one('product.category', string='Category', domain="[('parent_id', '!=', False)]", required=True)
    purchase_date = fields.Date('Purchase Date')
    partner_id = fields.Many2one('res.partner', 'Party')
    product_id = fields.Many2one('product.product', string='Product', domain="[('product_tmpl_id.categ_id', '=', product_category_id),('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",  change_default=True, ondelete='restrict', check_company=True, required=True) 
    product_template_id = fields.Many2one('product.template', string='Product Template', related="product_id.product_tmpl_id")    
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    subtotal = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    bill_id = fields.Many2one('purchase.bills', 'Purchase ID')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    currency_id = fields.Many2one("res.currency", 'Currency', readonly=True)
    
    @api.onchange('product_id')
    def onchange_category(self):
        if self.product_id:
            self.product_uom_id = self.product_id.product_tmpl_id.uom_id.id or False
    
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    def _default_supplier_rank(self):
        if self.env.context.get('supplier_rank') == 1:
            return self.env.context.get('supplier_rank')
        else:
            return 0 
    
    supplier_rank = fields.Integer(default=_default_supplier_rank)

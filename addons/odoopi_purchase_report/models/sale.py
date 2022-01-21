# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

status = [
    'draft', 'sent', 'sale', 'done', 'cancel'
]


class DashboardSales(models.Model):
    _name = 'dashboard.sales'

    user_id = fields.Many2one('res.users')
    name = fields.Char(related='user_id.name')
    image_128 = fields.Binary(related='user_id.image_128')

    sales_request_no = fields.Integer()
    sales_request_amount = fields.Float()

    sales_order_no = fields.Integer()
    sales_order_amount = fields.Float()

    sales_invoiced_no = fields.Integer()
    sales_invoiced_amount = fields.Float()

    sales_locked_no = fields.Integer()
    sales_locked_amount = fields.Float()

    sales_canceled_no = fields.Integer()
    sales_canceled_amount = fields.Float()

    partner_sales_no = fields.Integer()
    total_sales_amount = fields.Integer()
    
    #, ('invoice_status', 'not in', ['invoiced'])
    def get_sales_no(self, state, user_id):
        data = self.env['sale.order'].search(
            [('state', 'in', state), ('user_id', '=', user_id)])
        return len(data)
    
    #('invoice_status', 'not in', ['invoiced']), 
    def get_sales_amount(self, state, user_id):
        data = self.env['sale.order'].search(
            [('state', 'in', state), ('user_id', '=', user_id)])
        return sum([val.amount_total for val in data])
    
    #, ('invoice_status', 'in', ['invoiced'])
    def get_sales_invoiced_no(self, state, user_id):
        data = self.env['sale.order'].search(
            [('invoice_status', 'in', ['invoiced']),('state', 'in', state), ('user_id', '=', user_id)])
        return len(data)
    
    #('invoice_status', 'in', ['invoiced']), 
    def get_sales_invoiced_amount(self, state, user_id):
        data = self.env['sale.order'].search(
            [('invoice_status', 'in', ['invoiced']),('state', 'in', state), ('user_id', '=', user_id)])
        return sum([val.amount_total for val in data])

    def get_partner_no(self, user_id):
        data = self.env['sale.order'].search([('user_id', '=', user_id)])
        # print(len(list(dict.fromkeys([val.partner_id for val in data]))), '///////// partner')
        return len(list(dict.fromkeys([val.partner_id for val in data])))
        
    def get_amount_total(self, user_id):
        data = self.env['sale.order'].search([('user_id', '=', user_id)])
        # print(len(list(dict.fromkeys([val.partner_id for val in data]))), '///////// partner')
        return sum(([val.amount_total for val in data]))

    # --------------view action --------------- #

    def partner_sales_view(self):
        data = self.env['sale.order'].search([('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.partner_id.id for val in data])],
                "res_model": "res.partner",
                "name": _('Partner %s') % self.user_id.name,
            }
            
    def amount_sales_view(self):
        data = self.env['sale.order'].search([('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "sale.order",
                "name": _('Sale Orders %s') % self.user_id.name,
            }
    
    #('invoice_status', 'in', ['invoiced']), 
    def order_sales_invoiced_view(self):
        data = self.env['sale.order'].search(
            [('state', 'in', [status[2]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "sale.order",
                "name": _('Invoiced sales User (%s)') % self.user_id.name,
            }
    
    #('invoice_status', 'not in', ['invoiced']), 
    def order_sales_view(self):
        data = self.env['sale.order'].search(
            [('state', 'in', [status[2]]),
             ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "sale.order",
                "name": _('Ordered sales User (%s)') % self.user_id.name,
            }

    def lock_sales_view(self):
        data = self.env['sale.order'].search([('state', 'in', [status[3]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "sale.order",
                "name": _('Locked  sales User (%s)') % self.user_id.name,
            }

    def cancel_sales_view(self):
        data = self.env['sale.order'].search([('state', 'in', [status[4]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "sale.order",
                "name": _('Canceled  sales User (%s)') % self.user_id.name,
            }

    def request_sales_view(self):
        data = self.env['sale.order'].search(
            [('state', 'in', [status[0], status[1]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "sale.order",
                "name": _('Quatations  sales User (%s)') % self.user_id.name,
            }

    # --------------view action --------------- #

    def data_dashboard_sales(self):
        uid = self.env.uid
        users = []
        if uid == 2:    
            for val in self.env['sale.order'].search([]):
                users.append(val.user_id.id)
            users = list(dict.fromkeys(users))
        if uid != 2:
            for val in self.env['sale.order'].search([('create_uid','=',uid)]):
                users.append(val.user_id.id)
            users = list(dict.fromkeys(users))          
        print(users,"lllllllllllllllllllll")
        if users:
            for user in users:
                dashboard = self.env['dashboard.sales'].search([('user_id', '=', user)])
                if dashboard:
                    # [
                    #     'draft', 'sent', 'to approve', 'sales', 'done', 'cancel'
                    # ]
                    dashboard.write(
                        {
                            'sales_request_no': self.get_sales_no([status[0], status[1]], user),
                            'sales_request_amount': self.get_sales_amount([status[0], status[1]],
                                                                                user),
                            'sales_order_no': self.get_sales_no([status[2]], user),
                            'sales_order_amount': self.get_sales_amount([status[2]], user),
                            'sales_invoiced_no': self.get_sales_invoiced_no([status[2]], user),
                            'sales_invoiced_amount': self.get_sales_invoiced_amount([status[2]], user),
                            'sales_locked_no': self.get_sales_no([status[3]], user),
                            'sales_locked_amount': self.get_sales_amount([status[3]], user),
                            'sales_canceled_no': self.get_sales_no([status[4]], user),
                            'sales_canceled_amount': self.get_sales_amount([status[4]], user),
                            'partner_sales_no': self.get_partner_no(user),
                            'total_sales_amount': self.get_amount_total(user),
                        }
                    )
                else:
                    self.env['dashboard.sales'].create(
                        {
                            'user_id': user,
                            'sales_request_no': self.get_sales_no([status[0], status[1]], user),
                            'sales_request_amount': self.get_sales_amount([status[0], status[1]],
                                                                                user),
                            'sales_order_no': self.get_sales_no([status[2]], user),
                            'sales_order_amount': self.get_sales_amount([status[2]], user),
                            'sales_invoiced_no': self.get_sales_invoiced_no([status[2]], user),
                            'sales_invoiced_amount': self.get_sales_invoiced_amount([status[2]], user),
                            'sales_locked_no': self.get_sales_no([status[3]], user),
                            'sales_locked_amount': self.get_sales_amount([status[3]], user),
                            'sales_canceled_no': self.get_sales_no([status[4]], user),
                            'sales_canceled_amount': self.get_sales_amount([status[4]], user),
                            'partner_sales_no': self.get_partner_no(user),
                            'total_sales_amount': self.get_amount_total(user),
                        }
                    )

        return {
            "type": "ir.actions.act_window",
            "view_mode": "kanban,search,graph",
            # "context": {'search_default_type_expenses': 'sheet'},
            "res_model": self._name,
            "name": _('sales Dashboard'),
        }

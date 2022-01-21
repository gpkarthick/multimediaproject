# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

status = [
    'draft', 'confirmed', 'load_sheet', 'production_completed', 'pandl_process', 'done'
]


class Dashboard(models.Model):
    _name = 'dashboard.purchase'

    user_id = fields.Many2one('res.users')
    name = fields.Char(related='user_id.name')
    image_128 = fields.Binary(related='user_id.image_128')

    purchase_request_no = fields.Integer()
    purchase_request_amount = fields.Float()

    purchase_order_no = fields.Integer()
    purchase_order_amount = fields.Float()

    purchase_invoiced_no = fields.Integer()
    purchase_invoiced_amount = fields.Float()

    purchase_locked_no = fields.Integer()
    purchase_locked_amount = fields.Float()

    purchase_canceled_no = fields.Integer()
    purchase_canceled_amount = fields.Float()

    partner_purchase_no = fields.Integer()
    
    #, ('invoice_status', 'not in', ['invoiced'])
    def get_purchase_no(self, state, user_id):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', state), ('user_id', '=', user_id)])
        return len(data)
    
    #('invoice_status', 'not in', ['invoiced']), 
    def get_purchase_amount(self, state, user_id):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', state), ('user_id', '=', user_id)])
        return sum([val.total_amount for val in data])
    
    #, ('invoice_status', 'in', ['invoiced'])
    def get_purchase_invoiced_no(self, state, user_id):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', state), ('user_id', '=', user_id)])
        return len(data)
    
    #('invoice_status', 'in', ['invoiced']), 
    def get_purchase_invoiced_amount(self, state, user_id):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', state), ('user_id', '=', user_id)])
        return sum([val.total_amount for val in data])

    def get_partner_no(self, user_id):
        arrival_id =self.env['purchase.arrival'].search([('user_id', '=', user_id)])
        data = self.env['purchase.arrival.line'].search([('arrival_id', 'in', arrival_id.ids)])
        # print(len(list(dict.fromkeys([val.partner_id for val in data]))), '///////// partner')
        return len(list(dict.fromkeys([val.partner_id for val in data])))

    # --------------view action --------------- #

    def partner_purchase_view(self):
        arrival_id = self.env['purchase.arrival'].search([('user_id', '=', self.user_id.id)])
        data = self.env['purchase.arrival.line'].search([('arrival_id','in',arrival_id.ids)])
        print(data,"data")
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.partner_id.id for val in data])],
                "res_model": "res.partner",
                "name": _('Partner %s') % self.user_id.name,
            }
    
    #('invoice_status', 'in', ['invoiced']), 
    def load_sheet_purchase_view(self):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', [status[2]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "purchase.arrival",
                "name": _('Load Sheet Purchase User (%s)') % self.user_id.name,
            }
    
    #('invoice_status', 'not in', ['invoiced']), 
    def production_purchase_view(self):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', [status[3]]),
             ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "purchase.arrival",
                "name": _('Production Completed Purchase User (%s)') % self.user_id.name,
            }

    def pandl_purchase_view(self):
        data = self.env['purchase.arrival'].search([('state', 'in', [status[4]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "purchase.arrival",
                "name": _('Profit and Loss  Purchase User (%s)') % self.user_id.name,
            }

    def completed_purchase_view(self):
        data = self.env['purchase.arrival'].search([('state', 'in', [status[5]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "purchase.arrival",
                "name": _('Completed  Purchase User (%s)') % self.user_id.name,
            }

    def request_purchase_view(self):
        data = self.env['purchase.arrival'].search(
            [('state', 'in', [status[0], status[1], status[2]]), ('user_id', '=', self.user_id.id)])
        if data:
            return {
                "type": "ir.actions.act_window",
                "view_mode": "kanban,tree,form",
                "context": {'create': False},
                "domain": [('id', 'in', [val.id for val in data])],
                "res_model": "purchase.arrival",
                "name": _('Requested  Purchase User (%s)') % self.user_id.name,
            }

    # --------------view action --------------- #

    def data_dashboard_purchase(self):
        print('////////////')
        uid = self.env.uid
        users = []
        if uid == 2:    
            for val in self.env['purchase.arrival'].search([]):
                users.append(val.user_id.id)
            users = list(dict.fromkeys(users))
        if uid != 2:
            for val in self.env['purchase.arrival'].search([('create_uid','=',uid)]):
                users.append(val.user_id.id)
            users = list(dict.fromkeys(users))          
        print(users,"lllllllllllllllllllll")
        if users:
            for user in users:
                dashboard = self.env['dashboard.purchase'].search([('user_id', '=', user)])
                if dashboard:
                    # [
                    #     'draft', 'sent', 'to approve', 'purchase', 'done', 'cancel'
                    # ]
                    dashboard.write(
                        {
                            'purchase_request_no': self.get_purchase_no([status[0], status[1], status[2]], user),
                            'purchase_request_amount': self.get_purchase_amount([status[0], status[1], status[2]],
                                                                                user),
                            'purchase_order_no': self.get_purchase_no([status[3]], user),
                            'purchase_order_amount': self.get_purchase_amount([status[3]], user),
                            'purchase_invoiced_no': self.get_purchase_invoiced_no([status[3]], user),
                            'purchase_invoiced_amount': self.get_purchase_invoiced_amount([status[3]], user),
                            'purchase_locked_no': self.get_purchase_no([status[4]], user),
                            'purchase_locked_amount': self.get_purchase_amount([status[4]], user),
                            'purchase_canceled_no': self.get_purchase_no([status[5]], user),
                            'purchase_canceled_amount': self.get_purchase_amount([status[5]], user),
                            'partner_purchase_no': self.get_partner_no(user),
                        }
                    )
                else:
                    self.env['dashboard.purchase'].create(
                        {
                            'user_id': user,
                            'purchase_request_no': self.get_purchase_no([status[0], status[1], status[2]], user),
                            'purchase_request_amount': self.get_purchase_amount([status[0], status[1], status[2]],
                                                                                user),
                            'purchase_order_no': self.get_purchase_no([status[3]], user),
                            'purchase_order_amount': self.get_purchase_amount([status[3]], user),
                            'purchase_invoiced_no': self.get_purchase_invoiced_no([status[3]], user),
                            'purchase_invoiced_amount': self.get_purchase_invoiced_amount([status[3]], user),
                            'purchase_locked_no': self.get_purchase_no([status[4]], user),
                            'purchase_locked_amount': self.get_purchase_amount([status[4]], user),
                            'purchase_canceled_no': self.get_purchase_no([status[5]], user),
                            'purchase_canceled_amount': self.get_purchase_amount([status[5]], user),
                            'partner_purchase_no': self.get_partner_no(user),
                        }
                    )

        return {
            "type": "ir.actions.act_window",
            "view_mode": "kanban,search,graph",
            # "context": {'search_default_type_expenses': 'sheet'},
            "res_model": self._name,
            "name": _('Purchase Dashboard'),
        }

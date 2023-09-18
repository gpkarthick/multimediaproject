from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PrimePMFBYCalculator(models.Model):
    _name = "prime.pmfby.calculator"
    _description = "Prime PMFBY Calculator"
    _order = 'name desc'

    def _default_service_charge(self):
        amount = 0
        if self.env.user.user_type == 'shop':
            amount = 150
        else:
            amount = 250
        return amount

    name = fields.Char(string='Season', readonly=True, default='Rabi')
    year = fields.Char(string='Year', readonly=True, default='2021-2022')
    scheme = fields.Char(string='Scheme', readonly=True, default='Pradhan Mantri Fasal Bima Yojana')
    state = fields.Char(string='State', readonly=True, default='Tamil Nadu')
    crop = fields.Char(string='Crop', readonly=True, default='Paddy-II')
    area = fields.Float(string='Area(Hectare)', required=True)
    premium_amount = fields.Float(string='Premium Amt (Rs)', required=True)
    service_charge = fields.Float(string='Service Amount', default=_default_service_charge)
    total_amount = fields.Float(string='Total Amount', required=True)

    measurement = fields.Selection([('Kuzhi', 'Kuzhi'), ('Maa', 'Maa'), ('Acre', 'Acre'), ('Hectare', 'Hectare')], string='Measurement')
    measurement_area = fields.Float(string='Measurement Area')
    convertion_amount = fields.Float(string='Convertion Amount Ares')

    @api.onchange('measurement_area','measurement')
    def onchange_measurement(self):
        if self.measurement == 'Kuzhi':
            self.convertion_amount = self.measurement_area * 0.137 * 12.67
        if self.measurement == 'Maa':
            self.convertion_amount = self.measurement_area * 13.66 * 12.67
        if self.measurement == 'Acre':
            self.convertion_amount = self.measurement_area * 40.5 * 12.67
        if self.measurement == 'Hectare':
            self.convertion_amount = self.measurement_area * 100 * 12.67

    # Old Calculation
    # @api.onchange('area', 'service_charge')
    # def onchange_area_insured(self):
    #     # ~ base_insured_amt = 803.99000
    #     base_insured_amt = 844.74000
    #     # service_charge = 250
    #     if self.area * 100 > 0:
    #         area_insured = self.area * 100
    #         premium_amt = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
    #         self.premium_amount = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
    #         self.service_charge = self.service_charge
    #         self.total_amount = premium_amt + self.service_charge

    @api.onchange('area','service_charge')
    def onchange_area_insured(self):
        # ~ base_insured_amt = 803.99000
        base_insured_amt = 870.68000
        # service_charge = 250
        if self.area * 100 > 0:
            area_insured = self.area * 100
            premium_amt = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
            self.premium_amount = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
            self.service_charge = self.service_charge
            self.total_amount = premium_amt + self.service_charge

    # @api.onchange('service_charge')
    # def onchange_service_charge(self):
    #     self.total_amount = self.premium_amount + self.service_charge

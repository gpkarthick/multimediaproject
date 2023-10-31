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

    district_id = fields.Many2one('district.master', string='District', required=True)
    name = fields.Char(string='Season', readonly=True, default='Rabi')
    year = fields.Char(string='Year', readonly=True, default='2021-2022')
    scheme = fields.Char(string='Scheme', readonly=True, default='Pradhan Mantri Fasal Bima Yojana')
    state = fields.Char(string='State', readonly=True, default='Tamil Nadu')
    crop = fields.Char(string='Crop', readonly=True, default='Paddy-II')
    area = fields.Float(string='Area(Hectare)', required=True)
    premium_amount = fields.Float(string='Premium Amt (Rs)', required=True)
    service_charge = fields.Float(string='Service Amount', default=_default_service_charge)
    total_amount = fields.Float(string='Total Amount', required=True)

    farmer_birth_year = fields.Integer('Birth Year', required=True)
    farmer_age = fields.Integer('Age', readonly=True)

    measurement = fields.Selection([('Kuzhi', 'Kuzhi'), ('Maa', 'Maa'), ('Acre', 'Acre'), ('Hectare', 'Hectare')], string='Measurement', required=True)
    measurement_area = fields.Float(string='Measurement Area', required=True)
    convertion_amount = fields.Float(string='Convertion Amount Ares', required=True)

    # village_id = fields.Many2one('village.master', string='Village')
    # firka_id = fields.Many2one('firka.master', string='Firka')
    # block_id = fields.Many2one('block.master', string='Block')
    # subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District')
    # state2_id = fields.Many2one('state.master', string='State')

    village_id = fields.Many2one('village.master', string='Village', required=True)
    firka_id = fields.Many2one('firka.master', string='Firka', required=True)
    block_id = fields.Many2one('block.master', string='Block', required=True)
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)

    @api.onchange('village_id')
    def onchange_village_id(self):
        if not self.village_id:
            self.firka_id = False
            self.block_id = False
            self.subdistrict_id = False
            self.district_id = False

        if self.village_id:
            self.firka_id = self.village_id.firka_id.id
            self.block_id = self.village_id.block_id.id
            self.subdistrict_id = self.village_id.subdistrict_id.id
            self.district_id = self.village_id.district_id.id


    @api.onchange('farmer_birth_year')
    def onchange_age_calculation(self):
        if self.farmer_birth_year:
            get_age = datetime.now().year - self.farmer_birth_year
            self.farmer_age = get_age    

    @api.onchange('measurement_area','measurement', 'district_id')
    def onchange_measurement(self):
        # 2022 value is 12.67
        if self.measurement == 'Kuzhi':
            self.convertion_amount = self.measurement_area * 0.137 * self.district_id.area_calculation
        if self.measurement == 'Maa':
            self.convertion_amount = self.measurement_area * 13.66 * self.district_id.area_calculation
        if self.measurement == 'Acre':
            self.convertion_amount = self.measurement_area * 40.5 * self.district_id.area_calculation
        if self.measurement == 'Hectare':
            self.convertion_amount = self.measurement_area * 100 * self.district_id.area_calculation

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

    @api.onchange('area','service_charge','district_id')
    def onchange_area_insured(self):
        # ~ base_insured_amt = 803.99000
        base_insured_amt = self.district_id.base_insured_amt
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

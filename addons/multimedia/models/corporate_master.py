from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class FarmerStateMaster(models.Model):
    _name = 'farmer.state.master'
    _description = 'State Master'
    _order = "name asc"

    name = fields.Char('State Name', required=True)
    state_code = fields.Char('State Code', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    district_ids = fields.One2many('farmer.district.master', 'state_id', "District Records")

    @api.constrains('name')
    def _state_name_unique(self):
        lst = [x.name.lower().replace(" ", "") for x in self.search([('id', '!=', self.id)])]
        if self.name.lower().replace(" ", "") in lst:
            raise ValidationError(_('The Same State is already available'))

    @api.constrains('state_code')
    def _state_code_unique(self):
        res = [x.state_code.lower().replace(" ", "") for x in self.search([('id', '!=', self.id)])]
        if self.state_code.lower().replace(" ", "") in res:
            raise ValidationError(_('The same State Code is already available'))

    @api.depends('name', 'state_code')
    def name_get(self):
        result = []
        for record in self:
            name = '[' + record.state_code + '] ' + record.name
            result.append((record.id, name))
        return result

class FarmerDistrictMaster(models.Model):
    _name = 'farmer.district.master'
    _description = 'Farmer District Master'
    _order = "name asc"

    name = fields.Char('District Name', required=True)
    district_code = fields.Char('District Code')
    state_id = fields.Many2one('farmer.state.master', string='State', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    taluk_ids = fields.One2many('farmer.taluk.master', 'district_id', "Taluk Records")
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', 'state_id')
    def _district_name_unique(self):
        lst = [x.name.lower().replace(" ", "") for x in
               self.search([('id', '!=', self.id), ('state_id', '=', self.state_id.id)])]
        if self.name.lower().replace(" ", "") in lst:
            raise ValidationError(_('The Same District Name is already available'))

class FarmerTalukMaster(models.Model):
    _name = 'farmer.taluk.master'
    _description = 'Farmer Taluk Master'
    _order = "name asc"

    name = fields.Char('Taluk Name', required=True)
    taluk_code = fields.Char('Taluk Code')
    state_id = fields.Many2one('farmer.state.master', string='State', required=True)
    district_id = fields.Many2one('farmer.district.master', string='District', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    village_ids = fields.One2many('farmer.village.master', 'taluk_id', "Village Records")
    active = fields.Boolean('Active', default=True)

    # @api.constrains('name', 'state_id')
    # def _taluk_name_unique(self):
    #     lst = [x.name.lower().replace(" ", "") for x in
    #            self.search([('id', '!=', self.id), ('state_id', '=', self.state_id.id)])]
    #     if self.name.lower().replace(" ", "") in lst:
    #         raise ValidationError(_('The Same District Name is already available'))

class FarmerVillageMaster(models.Model):
    _name = 'farmer.village.master'
    _description = 'Farmer Village Master'
    _order = "name asc"

    name = fields.Char('Village Name', required=True)
    village_code = fields.Char('Village Code')
    taluk_id = fields.Many2one('farmer.taluk.master', string='Taluk', required=True)
    district_id = fields.Many2one('farmer.district.master', string='District', required=True)
    state_id = fields.Many2one('farmer.state.master', string='State', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)

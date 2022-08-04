from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class SiteAccessURL(models.Model):
    _name = 'site.access.url'
    _description = 'Site Access'
    _order = "name asc"

    name = fields.Char('Name', required=True)
    site_url = fields.Char('URL', required=True)
    site_image = fields.Image('Image', attachment=True)
    site_category_id = fields.Many2one('site.category', help='Category', string="Category", required=True)
    site_sub_category_id = fields.Many2one('site.sub.category', help='Sub Category', string="Sub Category", required=True)

    def action_redirect_url(self):
        return {
            'name': _("Visit Webpage"),
            'type': 'ir.actions.act_url',
            'url': '%s' % (self.site_url),
            'target': 'new',
        }

    @api.onchange('site_sub_category_id')
    def _onchange_sub_category_id(self):
        if self.site_sub_category_id:
            self.site_category_id = self.site_sub_category_id.parent_categ_id

class BannerImages(models.Model):
    _name = 'banner.image'
    _description = 'Banner Images'
    _order = "name asc"

    name = fields.Char('Name', required=True)
    site_image = fields.Image('Image', attachment=True)
    site_category_id = fields.Many2one('site.category', help='Category', string="Category", required=True)
    site_sub_category_id = fields.Many2one('site.sub.category', help='Sub Category', string="Sub Category", required=True)

    @api.onchange('site_sub_category_id')
    def _onchange_sub_category_id(self):
        if self.site_sub_category_id:
            self.site_category_id = self.site_sub_category_id.parent_categ_id

class SiteCategory(models.Model):
    _name = 'site.category'
    _description = 'Site Category'
    _order = "name asc"

    name = fields.Char('Name', required=True)

class SiteSubCategory(models.Model):
    _name = 'site.sub.category'
    _description = 'Site Sub Category'
    _order = "name asc"

    name = fields.Char('Name', required=True)
    parent_categ_id = fields.Many2one('site.category', help='Parent Category', string="Parent Category", required=True)

class Attachment(models.Model):
    _inherit = "ir.attachment"

    def _default_get_value(self):
        if self.env.context.get('form_image_attachment') == True:
            return self.env.context.get('form_image_attachment')

    form_image_attachment = fields.Boolean(index=True, default=_default_get_value)
    form_name = fields.Char(string="Form Name")
    site_sub_category_id = fields.Many2one('site.sub.category', help='Sub Category', string="Sub Category",
                                           required=True)
    site_category_id = fields.Many2one('site.category', help='Category', string="Category", required=True)

    @api.onchange('site_sub_category_id')
    def _onchange_sub_category_id(self):
        if self.site_sub_category_id:
            self.site_category_id = self.site_sub_category_id.parent_categ_id

    def action_download(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'Form Image Download',
            'url': "web/content/?model=" + self._name + "&id=" + str(
                self.id) + "&filename_field=name&field=datas&download=true&filename=" + self.name,
            'target': 'self',
        }

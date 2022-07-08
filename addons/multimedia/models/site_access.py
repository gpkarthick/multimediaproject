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
    site_category_id = fields.Many2one('site.category', help='Site Category', string="Site Category", required=True)

    def action_redirect_url(self):
        return {
            'name': _("Visit Webpage"),
            'type': 'ir.actions.act_url',
            'url': '%s' % (self.site_url),
            'target': 'new',
        }

class SiteCategory(models.Model):
    _name = 'site.category'
    _description = 'Site Category'
    _order = "name asc"

    name = fields.Char('Name', required=True)
    parent_categ_id = fields.Many2one('site.category', help='Parent Category', string="Parent Category")

    @api.depends('name', 'parent_categ_id')
    def name_get(self):
        result = []
        name = ''
        for categ in self:
            if categ.name:
                name = '%s' % categ.name
            if categ.parent_categ_id:
                name = name + ' / %s' % categ.parent_categ_id.name
            result.append((categ.id, name))
        return result

class BannerImages(models.Model):
    _name = 'banner.image'
    _description = 'Banner Images'
    _order = "name asc"

    name = fields.Char('Name', required=True)
    site_image = fields.Image('Image', attachment=True)
    site_category_id = fields.Many2one('site.category', help='Site Category', string="Site Category", required=True)

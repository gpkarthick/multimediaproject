from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class PanForm(models.Model):
    _name = "pan.form"
    _description = "Pan form"
    _order = 'id desc'

    def _default_pan_type(self):
        return self.env.context.get('pan_type')

    def _default_work_type(self):
        return self.env.context.get('work_type')

    name = fields.Char(string='Pan Card No')
    party_name = fields.Char(string='Name')
    father_name = fields.Char(string='Father Name')
    mobile_no = fields.Char(string='Mobile No')
    address = fields.Text(string='Address')
    mail_id = fields.Char(string='Mail ID')
    dob = fields.Date(string='DOB')
    assigned_to_uid = fields.Many2one('res.users', string='Assigned to')
    seq_no = fields.Char(string='Sequence No', size=18, readonly=True, default=lambda self: _('New'))
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    attachment = fields.Binary(string="Image", attachment=True)
    aadhar_front = fields.Binary(string="Aadhar Front", attachment=True, required=True)
    aadhar_back = fields.Binary(string="Aadhar Back", attachment=True, required=True)
    pan_front = fields.Binary(string="Pan Front", attachment=True, required=True)
    pan_back = fields.Binary(string="Pan Back", attachment=True, required=True)
    parent_aadhar_front = fields.Binary(string="Aadhar Front", attachment=True, required=True)
    parent_aadhar_back = fields.Binary(string="Aadhar Back", attachment=True, required=True)
    old_pan_front = fields.Binary(string="Old Pan Front", attachment=True, required=True)
    gst_fist = fields.Binary(string="GST First", attachment=True, required=True)
    gst_second = fields.Binary(string="GST Second", attachment=True, required=True)
    gst_third = fields.Binary(string="GST Third", attachment=True, required=True)
    kazhu_declaration_certificate_front = fields.Binary(string="Kazhu Certificate Front", attachment=True, required=True)
    kazhu_declaration_certificate_back = fields.Binary(string="Kazhu Certificate Back", attachment=True, required=True)
    writtern_form = fields.Binary(string="Form", attachment=True, required=True)


    # Ration Card
    family_head_aadhar_front = fields.Binary(string="Family Head Aadhar Front", attachment=True, required=True)
    family_head_aadhar_back = fields.Binary(string="Family Head Aadhar Back", attachment=True, required=True)
    candidate_ration_remove_proof_first = fields.Binary(string="Candidate Remove Proof First Page", attachment=True, required=True)
    candidate_ration_remove_proof_second = fields.Binary(string="Candidate Remove Proof First Page", attachment=True, required=True)
    ration_card_front = fields.Binary(string="Ration Card Xerox Front", attachment=True, required=True)
    ration_card_back = fields.Binary(string="Ration Card Xerox Back", attachment=True, required=True)
    old_ration_card_front = fields.Binary(string="Old Ration Card Xerox Front", attachment=True, required=True)
    old_ration_card_back = fields.Binary(string="Old Ration Card Xerox Back", attachment=True, required=True)

    payslip_front = fields.Binary(string="Payslip Front", attachment=True, required=True)
    payslip_back = fields.Binary(string="payslip Back", attachment=True, required=True)

    form_front = fields.Binary(string="Form Front", attachment=True, required=True)
    form_back = fields.Binary(string="Form Back", attachment=True, required=True)

    community_front = fields.Binary(string="Community Proof Front", attachment=True, required=True)
    community_back = fields.Binary(string="Community Proof Back", attachment=True, required=True)

    birth_certificate_front = fields.Binary(string="Birth Certificate Front", attachment=True, required=True)
    birth_certificate_back = fields.Binary(string="Birth Certificate Back", attachment=True, required=True)

    # certificate
    candidate_photo = fields.Binary(string="Photo", attachment=True, required=True)


    pan_type = fields.Selection([('major', 'major'), ('minor', 'minor'), ('minor_to_major', 'minor_to_major'),
                                 ('correction', 'correction'), ('company', 'company'), ('trust', 'trust'), ('kuzhu', 'kuzhu'),
                                 ('newrationcard', 'New Ration Card'), ('rationnameadd', 'Ration Name Add'), ('rationnameremove', 'Ration Name Remove'),
                                 ('rationheadchange', 'Ration Head Change'), ('rationduplicate', 'Ration Duplicate Apply'),
                                 ('incomecertificate', 'Income Certificate'),('residencecertificate', 'Residence Certificate'),
                                 ('nativitycertificate', 'Nativity Certificate')
                                 ], string='Pan Type', readonly=True, default=_default_pan_type)
    work_type = fields.Selection([('pan', 'Pan'), ('rationcard', 'Ration Card'), ('aadharcard', 'Aadhar Card'), ('certificates', 'Certificates'), ('oapandpension', 'OAP and Pension'), ('welfare_of_differently_abled_ersons', 'Welfare of Differently Abled Persons'), ('project_work', 'Project Work'), ('multiple_xerox', 'Multiple Xerox'), ('marriage_registration', 'Marriage  Registration'), ('pmfby', 'PMFBY'), ('employment', 'Employment'), ('birth_and_death_certificate', 'Birth and Death Certificate')], string='Pan Type', readonly=True, default=_default_work_type)

    state = fields.Selection([('draft', 'Draft'), ('processing', 'Processing'), ('done', 'Done'), ('verified', 'Verified')], string='Status', readonly=True, default='draft')

    user_logo = fields.Binary("Company Image", related='create_uid.image_1920')
    district_id = fields.Many2one('district.master', string='District', readonly=True, default=lambda self: self.env.user.district_id)
    village_id = fields.Many2one('village.master', string='Village', readonly=True, default=lambda self: self.env.user.village_id)

    @api.constrains('attachment')
    def _check_user_image(self):
        if not self.attachment:
            raise ValidationError(_("Please Attach the Details Image"))

    @api.model
    def create(self, vals):
        print(self.env.context)
        if self.env.context['work_type'] == 'pan':
            if vals.get('seq_no', _('New')) == _('New'):
                vals['seq_no'] = self.env['ir.sequence'].next_by_code('pan.form') or _('New')
        if self.env.context['work_type'] == 'rationcard':
            if vals.get('seq_no', _('New')) == _('New'):
                vals['seq_no'] = self.env['ir.sequence'].next_by_code('pan.form.ration') or _('New')
        return super(PanForm, self).create(vals)

    def action_process(self):
        self.write({'state': 'processing'})

    def action_verify(self):
        self.write({'state': 'verified'})

    def action_reset(self):
        self.write({'state': 'draft'})

    def action_done(self):
        if not self.mobile_no:
            raise UserError(_('Please enter the mobile Number.'))
        if len(self.mobile_no) != 10:
            raise UserError(_('Please enter the 10 Digit mobile Number.'))
        if not self.name:
            raise UserError(_('Please enter the PAN Number.'))
        self.write({'state': 'done'})

class ResUsers(models.Model):
    _inherit = 'res.users'

    mail_id = fields.Char(string='Mail ID', required=True)
    mobile_no = fields.Char(string='Mobile No', required=True)
    district_id = fields.Many2one('district.master', string='District')
    village_id = fields.Many2one('village.master', string='Village')
    user_type = fields.Selection(string='User type', selection=[('shop', 'shop'), ('employee', 'employee'), ('management', 'management')], required=True)

class DistrictMaster(models.Model):
    _name = 'district.master'
    _description = 'District Master'
    _order = "name asc"

    name = fields.Char('District Name', required=True)
    district_code = fields.Char('District Code')

class VillageMaster(models.Model):
    _name = 'village.master'
    _description = 'Village Master'
    _order = "name asc"

    name = fields.Char('Village Name', required=True)
    village_code = fields.Char('Village Code')

class AcknowledgementSlip(models.Model):
    _name = "acknowledgement.slip"
    _description = "Acknowledgement Slip"
    _order = 'id desc'

    name = fields.Char(string='Sequence No', size=18, readonly=True, default=lambda self: _('New'))
    party_name = fields.Char(string='Name')
    father_name = fields.Char(string='Father Name')
    mobile_no = fields.Char(string='Mobile No')
    address = fields.Text(string='Address')
    mail_id = fields.Char(string='Mail ID')
    dob = fields.Date(string='DOB')
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', readonly=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('acknowledgement.slip') or _('New')
        return super(AcknowledgementSlip, self).create(vals)
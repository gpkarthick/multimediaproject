from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
import qrcode
import base64
import io

class FarmerInsurance(models.Model):
    _name = "farmer.insurance"
    _description = "Farmer Insurance Bussiness Operation"
    _order = 'name desc'
    
    @api.depends('crop_line_ids')
    def _amount_all(self):           
        for order in self:
            total_area_insured = total_premium_paid = total_sum_insured = 0.000            
            for line in order.crop_line_ids:
                total_area_insured += line.area_insured
                total_sum_insured += line.sum_insured
                total_premium_paid += line.farmer_share
            order.update({
                'total_area_insured': total_area_insured,
                'total_sum_insured': total_sum_insured,
                'total_premium_paid': total_premium_paid
            })
        
    name = fields.Char(string='Receipt No', required=True)
    original_receipt_no = fields.Char(string='Original Receipt No')
    seq_no = fields.Char(string='Seq No', default=lambda self: self.env['ir.sequence'].next_by_code('farmer.insurance.seq'))    
    insurance_date = fields.Date(string='Date', required=True)    
    
    state_id = fields.Many2one('state.master', string='State', required=True)
    scheme_name = fields.Char(string='Scheme', required=True, default='PMFBY')
    year_val = fields.Char(string='Year', required=True, default='2021')
    application_type = fields.Char(string='Application Type', required=True, default='NON LOANEE')
    season_name = fields.Char(string='Season', required=True, default='RABI')
    created_by = fields.Char(string='Created By', required=True, default='CSC')
    create_at = fields.Date(string='Created At', default=fields.Datetime.now, required=True)
    
    farmer_name = fields.Char(string='Farmer Name', required=True)
    relative_name = fields.Char(string='Relative Name', required=True)
    relative_type = fields.Selection([('son_of', 'son_of'), ('daughter_of', 'daughter_of'), ('wife_of', 'wife_of')], string='Relation Type', required=True)  
    mobile_no = fields.Char(string='Mobile No', required=True)
    farmer_type = fields.Selection([('marginal', 'Marginal')], string='Farmer Type', default='marginal', required=True)  
    gender_type = fields.Selection([('Male', 'Male'),('Female', 'Female')], string='Gender', required=True)  
    account_type = fields.Char(string='Account Type', required=True, default='SAVING')
        
    ifsc_code = fields.Char('IFSC Code', size=32, track_visibility='always', required=True)
    bank_account_no = fields.Char('Account Number', size=32, track_visibility='always', required=True)
    branch_name = fields.Char('Branch Name', size=60, required=True)    
    bank_name = fields.Char('Bank Name', size=60, required=True)    
    
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    state = fields.Selection([('draft', 'Draft'),('pending', 'Pending'),('paid', 'Paid')], string='Status', readonly=True, default='draft')  
    
    crop_data = fields.Char('Crop', size=60, required=True, default='Paddy - II')
    
    crop_line_ids = fields.One2many('crop.data.line', 'crop_id', "Drop Data")
    
    total_area_insured = fields.Float(string='Total Area Insured', digits='Purchase Weight', compute='_amount_all', store=True, readonly=True)
    total_premium_paid = fields.Float(string='Total Premium Paid', digits='Product Price', compute='_amount_all', store=True, readonly=True)
    total_sum_insured = fields.Float(string='Total Sum Insured', digits='Product Price', compute='_amount_all', store=True, readonly=True)
    
    # ~ district_id = fields.Many2one('district.master', string='District')
    # ~ taluk_id = fields.Many2one('taluk.master', string='Taluk')
    # ~ village_id = fields.Many2one('village.master', string='Village')
    # ~ location_id = fields.Many2one('farm.supervisor.assign', string='Assign')
    
    qr_code = fields.Binary("QR Code", attachment=True) 
    
    village_id = fields.Many2one('village.master', string='Village', required=True)
    firka_id = fields.Many2one('firka.master', string='Firka', required=True)
    block_id = fields.Many2one('block.master', string='Block', required=True)
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state2_id = fields.Many2one('state.master', string='State', required=True)
        
    def action_reset(self): 
        self.write({'state':'draft'}) 
        
    def action_pending(self): 
        self.write({'state':'pending'}) 
        
    def action_complete(self): 
        self.write({'state':'paid'})
        
        
    
    @api.onchange('name','farmer_name','relative_name','crop_line_ids','district_id','total_area_insured','total_premium_paid','total_sum_insured')
    def generate_qr_code(self):
        from io import BytesIO
        qr = qrcode.QRCode(
            version=13,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        data = ''
        receipt_no = state_name = farmer_name = season_name = year_val = line_details = tsi = tai = tpp = ''
        if self.name:
            receipt_no = self.name+", "
        if self.farmer_name:
            farmer_name = self.farmer_name+", "
        if self.season_name:
            season_name = self.season_name+", "
        if self.year_val:
            year_val = self.year_val+", "
        if self.state_id:
            state_name = self.state_id.name+", "
        line_details = "No of Crop(s) Insured:"+str(len(self.crop_line_ids))+' Crop(District, Area, Sum Insured(Rs.)):'
        if self.crop_line_ids:
            for line in self.crop_line_ids:
                line_details += line.crop_data+"("+self.district_id.name+", "+str(round(line.area_insured,3))+"Hect ,Rs"+str(line.sum_insured)+")"
            
        line_details += ','
        if self.total_premium_paid:
            tpp = "Total Farmer Premium: Rs. "+str(self.total_premium_paid)+", "
        if self.total_area_insured:
            tai = "Total Area Insured "+str(self.total_area_insured)+ " Hect,"
        if self.total_sum_insured:
            tsi = "Total Sum Insured Rs. "+str(self.total_sum_insured)+', '
        
        data = "Content: Acknowledgement No:"+receipt_no+"Farmer Name:"+farmer_name+"Season: "+season_name+'Year: '+year_val+"State:"+state_name+line_details+tpp+tai+tsi+"Transaction Status: PAID, Application Source:CSC"
        
        qr.add_data(data)        
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
        
        qr = qrcode.QRCode(
        version=13,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
    
    @api.onchange('ifsc_code')
    def onchange_ifsc_code(self):
        import requests
        datas = {}
        if not self.ifsc_code:
            datas = {'branch_name':'',
                    'bank_name':''}
        if self.ifsc_code:
            datas = {}
            result = ''            
            url = "https://ifsc.razorpay.com/{0}".format(self.ifsc_code)
            try:
                result = requests.get(url).json()
            except Exception as e:
                raise UserError(_('Wrong IFSC Code, Please check it (%s).') % e)
            if result == 'Not Found':
                datas.update({
                    'branch': '',
                    'bank_address':'Wrong IFSC Code'
                })
            else:                
                datas.update({
                    'branch_name': result['BRANCH'].replace('?????', ''),
                    'bank_name':result['BANK'].replace('?????', ''),
                })
        return {'value': datas}
    
    @api.onchange('village_id')
    def onchange_village_id(self):
        if not self.village_id:
            self.firka_id = False
            self.block_id = False
            self.subdistrict_id = False
            self.district_id = False
            self.state_id = False
        if self.village_id:
            self.firka_id = self.village_id.firka_id.id
            self.block_id = self.village_id.block_id.id
            self.subdistrict_id = self.village_id.subdistrict_id.id
            self.district_id = self.village_id.district_id.id
            self.state2_id = self.village_id.state_id.id
    
    def insurance_bill_print(self):
        return self.env.ref('multimedia.action_report_insurance').report_action(self)     
        
class CropDataLine(models.Model):
    _name = 'crop.data.line'
    _description = 'Crop Data Line details'
    
    survey_no = fields.Char('Survey No', required=True)
    khasra_no = fields.Char('Khasra No', required=True)
    sum_insured = fields.Float(string='Sum Insured', required=True)
    area_insured = fields.Float(string='Area Insured', required=True, digits='Purchase Weight')
    gov_share = fields.Float(string='Gov Share', required=True)
    farmer_share = fields.Float(string='Farmer Share', required=True)
    crop_data = fields.Char('Crop', required=True, default='Paddy- II')
    crop_id = fields.Many2one('farmer.insurance', string='Insurance')
    
    @api.onchange('area_insured')
    def onchange_area_insured(self):
        base_insured_amt = 803.99000
        if self.area_insured*100 > 0:
            area_insured = self.area_insured*100
            self.farmer_share = round(((base_insured_amt*(1.5/100))*area_insured),2)
            self.gov_share = round(( (0.80399*335)*area_insured),2)
            self.sum_insured = round(base_insured_amt*area_insured,2)
            
        
class StateMaster(models.Model):
    _name = 'state.master'
    _description = 'State Master'
    _order = "name asc"
    
    name = fields.Char('State Name', required=True)
    state_code = fields.Char('State Code', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    district_ids = fields.One2many('district.master', 'state_id', "District Records")

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

class DistrictMaster(models.Model):
    _name = 'district.master'
    _description = 'District Master'
    _order = "name asc"

    name = fields.Char('District Name', required=True)
    district_code = fields.Char('District Code')
    state_id = fields.Many2one('state.master', string='State', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    subdistrict_ids = fields.One2many('subdistrict.master', 'district_id', "Dub District Records")    
    taluk_ids = fields.One2many('taluk.master', 'district_id', "Taluk Records")    

    @api.constrains('name', 'state_id')
    def _district_name_unique(self):
        lst = [x.name.lower().replace(" ", "") for x in
               self.search([('id', '!=', self.id), ('state_id', '=', self.state_id.id)])]
        if self.name.lower().replace(" ", "") in lst:
            raise ValidationError(_('The Same District Name is already available'))

    # ~ @api.constrains('district_code', 'state_id')
    # ~ def _district_code_unique(self):
        # ~ res = [x.district_code.lower().replace(" ", "") for x in
               # ~ self.search([('id', '!=', self.id), ('state_id', '=', self.state_id.id)])]
        # ~ if self.district_code.lower().replace(" ", "") in res:
            # ~ raise ValidationError(_('The same District Code is already available'))
    
    # ~ @api.depends('name', 'district_code')
    # ~ def name_get(self):
        # ~ result = []
        # ~ for record in self:
            # ~ name = '[' + record.district_code + '] ' + record.name
            # ~ result.append((record.id, name))
        # ~ return result        

class SubDistrictMaster(models.Model):
    _name = 'subdistrict.master'
    _description = 'Sub District Master'
    _order = "name asc"

    name = fields.Char('Sub District Name', required=True)
    subdistrict_code = fields.Char('Sub District Code')
    state_id = fields.Many2one('state.master', string='State', required=True) 
    district_id = fields.Many2one('district.master', string='District', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    block_ids = fields.One2many('block.master', 'subdistrict_id', "Block Records")    

    @api.constrains('name', 'district_id')
    def _subdistrict_name_unique(self):
        lst = [x.name.lower().replace(" ", "") for x in
               self.search([('id', '!=', self.id), ('district_id', '=', self.district_id.id)])]
        if self.name.lower().replace(" ", "") in lst:
            raise ValidationError(_('The Same Sub District Name is already available'))

    # ~ @api.constrains('subdistrict_code', 'district_id')
    # ~ def _subdistrict_code_unique(self):
        # ~ res = [x.subdistrict_code.lower().replace(" ", "") for x in
               # ~ self.search([('id', '!=', self.id), ('district_id', '=', self.district_id.id)])]
        # ~ if self.subdistrict_code.lower().replace(" ", "") in res:
            # ~ raise ValidationError(_('The same Sub District Code is already available'))
    
    # ~ @api.depends('name', 'subdistrict_code')
    # ~ def name_get(self):
        # ~ result = []
        # ~ for record in self:
            # ~ name = '[' + record.subdistrict_code + '] ' + record.name
            # ~ result.append((record.id, name))
        # ~ return result        

class BlockMaster(models.Model):
    _name = 'block.master'
    _description = 'Block Master'
    _order = "name asc"

    name = fields.Char('block Name', required=True)
    block_code = fields.Char('block Code')
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)    
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    firka_ids = fields.One2many('firka.master', 'block_id', "Firka Records")    
    
    # ~ @api.constrains('name', 'state_id', 'district_id', 'subdistrict_id', 'subdistrict_id')
    # ~ def _block_name_unique(self):
        # ~ lst = [x.name.lower().replace(" ", "") for x in self.search(
            # ~ [('id', '!=', self.id), ('state_id', '=', self.state_id.id), ('subdistrict_id', '=', self.subdistrict_id.id), ('district_id', '=', self.district_id.id)])]
        # ~ if self.name.lower().replace(" ", "") in lst:
            # ~ raise ValidationError(_('The Same Block Name is already available'))

    # ~ @api.constrains('block_code', 'state_id', 'district_id', 'subdistrict_id')
    # ~ def _block_code_unique(self):
        # ~ res = [x.block_code.lower().replace(" ", "") for x in self.search(
            # ~ [('id', '!=', self.id), ('state_id', '=', self.state_id.id), ('district_id', '=', self.district_id.id), ('subdistrict_id', '=', self.subdistrict_id.id)])]
        # ~ if self.block_code.lower().replace(" ", "") in res:
            # ~ raise ValidationError(_('The same Block Code is already available'))
    
    # ~ @api.depends('name', 'block_code')
    # ~ def name_get(self):
        # ~ result = []
        # ~ for record in self:
            # ~ name = '[' + record.block_code + '] ' + record.name
            # ~ result.append((record.id, name))
        # ~ return result
        
class FirkaMaster(models.Model):
    _name = 'firka.master'
    _description = 'Firka Master'
    _order = "name asc"

    name = fields.Char('Firka Name', required=True)
    firka_code = fields.Char('Firka Code')
    block_id = fields.Many2one('block.master', string='Block', required=True)
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)    
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    village_ids = fields.One2many('village.master', 'firka_id', "Village Records")
    
    # ~ @api.constrains('name', 'state_id', 'district_id', 'subdistrict_id', 'block_id')
    # ~ def _firka_name_unique(self):
        # ~ lst = [x.name.lower().replace(" ", "") for x in self.search(
            # ~ [('id', '!=', self.id), ('state_id', '=', self.state_id.id), ('subdistrict_id', '=', self.subdistrict_id.id), ('district_id', '=', self.district_id.id), ('block_id', '=', self.block_id.id)])]
        # ~ if self.name.lower().replace(" ", "") in lst:
            # ~ raise ValidationError(_('The Same Firka Name is already available'))

    # ~ @api.constrains('firka_code', 'state_id', 'district_id', 'subdistrict_id', 'block_id')
    # ~ def _firka_code_unique(self):
        # ~ res = [x.block_code.lower().replace(" ", "") for x in self.search(
            # ~ [('id', '!=', self.id), ('state_id', '=', self.state_id.id), ('district_id', '=', self.district_id.id), ('subdistrict_id', '=', self.subdistrict_id.id), ('block_id', '=', self.block_id.id)])]
        # ~ if self.firka_code.lower().replace(" ", "") in res:
            # ~ raise ValidationError(_('The same Firka Code is already available'))
    
    # ~ @api.depends('name', 'firka_code')
    # ~ def name_get(self):
        # ~ result = []
        # ~ for record in self:
            # ~ name = '[' + record.firka_code + '] ' + record.name
            # ~ result.append((record.id, name))
        # ~ return result
    

class VillageMaster(models.Model):
    _name = 'village.master'
    _description = 'Village Master'
    _order = "name asc"

    name = fields.Char('Village Name', required=True)
    village_code = fields.Char('Village Code', readonly =True, default = lambda self: _('New'))
    firka_id = fields.Many2one('firka.master', string='Firka', required=True)
    block_id = fields.Many2one('block.master', string='Block', required=True)
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, vals):
        if 'village_code' not in vals or vals['village_code'] == _('New'):
            vals['village_code'] = self.env['ir.sequence'].next_by_code('village.master') or _('New')
        return super(VillageMaster, self).create(vals)
    
    # ~ @api.depends('name', 'village_code')
    # ~ def name_get(self):
        # ~ result = []
        # ~ for record in self:
            # ~ name = '[' + record.village_code + '] ' + record.name
            # ~ result.append((record.id, name))
        # ~ return result

    @api.onchange('firka_id')
    def onchange_firka(self):
        if not self.firka_id:
            self.block_id = False
            self.subdistrict_id = False
            self.district_id = False
            self.state_id = False
        if self.firka_id:
            self.block_id = self.firka_id.block_id.id
            self.subdistrict_id = self.firka_id.subdistrict_id.id
            self.district_id = self.firka_id.district_id.id
            self.state_id = self.firka_id.state_id.id


class TalukMaster(models.Model):
    _name = 'taluk.master'
    _description = 'Taluk Master'
    _order = "name asc"

    name = fields.Char('Taluk Name', required=True)
    taluk_code = fields.Char('Taluk Code', readonly=True, default = lambda self: _('New'))
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)    
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    # ~ village_ids = fields.One2many('village.master', 'taluk_id', "Village Records")    
    
    @api.constrains('name', 'state_id', 'district_id')
    def _taluk_name_unique(self):
        lst = [x.name.lower().replace(" ", "") for x in self.search(
            [('id', '!=', self.id), ('state_id', '=', self.state_id.id), ('district_id', '=', self.district_id.id)])]
        if self.name.lower().replace(" ", "") in lst:
            raise ValidationError(_('The Same Taluk Name is already available'))

    @api.constrains('taluk_code', 'state_id', 'district_id')
    def _taluk_code_unique(self):
        res = [x.taluk_code.lower().replace(" ", "") for x in self.search(
            [('id', '!=', self.id), ('state_id', '=', self.state_id.id), ('district_id', '=', self.district_id.id)])]
        if self.taluk_code.lower().replace(" ", "") in res:
            raise ValidationError(_('The same Taluk Code is already available'))
    
    @api.depends('name', 'taluk_code')
    def name_get(self):
        result = []
        for record in self:
            name = '[' + record.taluk_code + '] ' + record.name
            result.append((record.id, name))
        return result
        

class ImportMaster(models.Model):
    _name = 'import.master'
    _description = 'import Master'

    import_file = fields.Binary('Import CSV File')
    name = fields.Char('District Name', required=True)

    def action_import(self):
        for order in self:
            count = 0
            import_file = str(base64.decodestring(order.import_file), 'windows-1252', 'strict').split('\n')
            count = name_count = 0
            district_id = subdistrict_id = block_id = 0
            taluk_id = 0
            village_count =0
            for line in import_file:
                row = line.split(',')
                # ~ print (row)
                if not row:
                    break
                count += 1
                if count > 3 and len(row) > 1:
                    print (row)
                    district_name = row[1]
                    subdistrict_name = row[2]
                    block_name = row[3]
                    firka_name = row[4]
                    village_name = row[5]
                    village_code = row[6]
                    print (district_name,subdistrict_name,block_name,firka_name,village_name,village_code)
                    if district_name:
                        district = self.env['district.master'].create({'name': district_name, 'state_id': 1})
                        district_id = district.id
                    if subdistrict_name:
                        subdistrict = self.env['subdistrict.master'].create({'name': subdistrict_name, 'state_id': 1, 'district_id': district_id})
                        subdistrict_id = subdistrict.id
                    if block_name:
                        block = self.env['block.master'].create({'name': block_name, 'state_id': 1, 'district_id': district_id, 'subdistrict_id': subdistrict_id})
                        block_id = block.id
                    if firka_name:
                        firka = self.env['firka.master'].create({'name': firka_name, 'state_id': 1, 'district_id': district_id, 'subdistrict_id': subdistrict_id, 'block_id': block_id})
                        firka_id = firka.id
                    if village_name:
                        village = self.env['village.master'].create({'name': village_name,'village_code': village_code, 'state_id': 1, 'district_id': district_id, 'subdistrict_id': subdistrict_id, 'block_id': block_id, 'firka_id': firka_id})
                        
                        
                        
                    
                    
                    # ~ if district_code and district_name:
                        # ~ district = self.env['district.master'].create({'name': district_name, 'district_code': district_code, 'state_id': 1})
                        # ~ district_id = district.id
                    # ~ if taluk_code and taluk_name:
                        # ~ taluk = self.env['taluk.master'].create({'name': taluk_name, 'taluk_code': taluk_code, 'district_id': district_id, 'state_id': 1})
                        # ~ taluk_id = taluk.id
                    # ~ if village_code and village_name:
                        # ~ village_count += 1
                        # ~ self.env['village.master'].create({'name': village_name, 'village_code': village_code, 'state_id': 1, 'district_id': district_id, 'taluk_id': taluk_id})


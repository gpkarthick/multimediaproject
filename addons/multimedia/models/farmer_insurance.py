from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError
import qrcode
import base64
import io
from googletrans import Translator, constants
from pprint import pprint

class FarmerInsurance(models.Model):
    _name = "farmer.insurance"
    _description = "Farmer Insurance Bussiness Operation"
    _order = 'id desc'

    @api.depends('crop_line_ids')
    def _amount_all(self):
        for order in self:
            total_area_insured = total_premium_paid = total_sum_insured = 0.000
            for line in order.crop_line_ids:
                total_area_insured += line.area_insured
                total_sum_insured += line.sum_insured
                total_premium_paid += line.farmer_share
            # print (total_area_insured)
            # print ( format(total_area_insured, '.3f'))
            order.update({
                'total_area_insured': total_area_insured,
                # 'total_area_insured': total_area_insured,
                # 'total_area_insured': format(total_area_insured, '.3f'),
                'total_sum_insured': total_sum_insured,
                'total_premium_paid': total_premium_paid
            })

    @api.depends('distributor_service_charge','distributor_received_amount')
    def _distributor_tracking(self):
        for order in self:
            distributor_total_amount = distributor_balance_amount = 0.000
            distributor_total_amount = order.premium_amount + order.distributor_service_charge
            distributor_balance_amount = order.distributor_received_amount - (order.premium_amount + order.distributor_service_charge)
            order.update({
                'distributor_total_amount': distributor_total_amount,
                'distributor_balance_amount': distributor_balance_amount,
            })

    def _default_service_charge(self):
        amount = 0
        if self.env.user.user_type == 'shop':
            amount = 150
        else:
            amount = 250
        return amount

    @api.depends('farmer_birth_year')
    def _age_calculation(self):
        """
        Compute the age calculation
        """
        get_age = datetime.now().year - self.farmer_birth_year
        self.update({
            'farmer_age': get_age
        })

    name = fields.Char(string='Duplicate Receipt No', size=18, readonly=True,  default=lambda self: _('New'))
    auto_serial_no = fields.Char(string='Serial No', size=18, readonly=True,  default=lambda self: _('New'))
    original_receipt_no = fields.Char(string='Original Receipt No')
    seq_no = fields.Char(string='Seq No',
                         default=lambda self: self.env['ir.sequence'].next_by_code('farmer.insurance.seq'))
    insurance_date = fields.Date(string='Date')
    sowing_date = fields.Date(string='Sowing Date')

    state_id = fields.Many2one('state.master', string='State', required=True,
                               default=lambda self: self.env['state.master'].search([('id', '=', 1)]))
    state_id_tamil = fields.Char(string='State in Tamil' , default='தமிழ்நாடு')
    scheme_name = fields.Char(string='Scheme' , default='PMFBY')
    year_val = fields.Char(string='Year', default='2023')
    application_type = fields.Char(string='Application Type', default='NON LOANEE')
    application_type_tamil = fields.Char(string='Application Type Tamil', default='கடன் பெறாதவர்')
    season_name = fields.Char(string='Season', default='RABI')
    season_name_tamil = fields.Char(string='Season in Tamil', default='ராபி')
    created_by = fields.Char(string='Created By', default='CSC')
    create_at = fields.Date(string='Created At', default=fields.Datetime.now)

    farmer_name = fields.Char(string='Farmer Name')
    relative_name = fields.Char(string='Relative Name')
    relative_type = fields.Selection([('son_of', 'son_of'), ('daughter_of', 'daughter_of'), ('wife_of', 'wife_of')],
                                     string='Relation Type')
    mobile_no = fields.Char(string='Mobile No')
    farmer_type = fields.Selection([('marginal', 'Marginal (0.01 - 1) Hectare'),('small', 'Small (1.01 - 2) Hectare'),('other', 'Other (above 2.01 Hectare)')], string='Farmer Type', default='marginal')
    gender_type = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')
    account_type = fields.Char(string='Account Type', default='SAVING')

    ifsc_code = fields.Char('IFSC Code', size=32, track_visibility='always')
    bank_account_no = fields.Char('Account Number', size=32, track_visibility='always')
    branch_name = fields.Char('Branch Name', size=60)
    bank_name = fields.Char('Bank Name', size=60)

    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    state = fields.Selection([('draft', 'Stage1'),('stage2', 'Stage2'),('stage3', 'Stage3'),('confirmed', 'Confirmed'),('verified', 'Verified'), ('printtaken', 'bill Taken'), ('done', 'Done')], string='Status',
                             readonly=True, default='draft')

    crop_data = fields.Char('Crop', size=60, default='Paddy - II')

    crop_line_ids = fields.One2many('crop.data.line', 'crop_id', "Drop Data")

    total_area_insured = fields.Float(string='Total Area Insured', compute='_amount_all',
                                      store=True, readonly=True, digits=(12,3))
    total_premium_paid = fields.Float(string='Total Premium Paid', digits='Product Price', compute='_amount_all',
                                      store=True, readonly=True)
    total_sum_insured = fields.Float(string='Total Sum Insured', digits='Product Price', compute='_amount_all',
                                     store=True, readonly=True)

    # ~ district_id = fields.Many2one('district.master', string='District')
    # ~ taluk_id = fields.Many2one('taluk.master', string='Taluk')
    # ~ village_id = fields.Many2one('village.master', string='Village')
    # ~ location_id = fields.Many2one('farm.supervisor.assign', string='Assign')

    qr_code = fields.Binary("QR Code", attachment=True)

    village_id = fields.Many2one('village.master', string='Village')
    firka_id = fields.Many2one('firka.master', string='Firka')
    block_id = fields.Many2one('block.master', string='Block')
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District')
    district_id = fields.Many2one('district.master', string='District')
    state2_id = fields.Many2one('state.master', string='State')

    village_tamil_name = fields.Char(string='Village Tamil Name')
    firka_tamil_name = fields.Char(string='Firka Tamil Name')
    block_tamil_name = fields.Char(string='Block Tamil Name')
    subdistrict_tamil_name = fields.Char(string='Subdistrict Tamil Name')
    district_tamil_name = fields.Char(string='District Tamil Name')
    state_tamil_name = fields.Char(string='State Tamil Name', default='தமிழ்நாடு')

    # Farmer Addr Detail
    farmer_village_id = fields.Many2one('farmer.village.master', string='Village')
    farmer_taluk_id = fields.Many2one('farmer.taluk.master', string='Taluk')
    farmer_district_id = fields.Many2one('farmer.district.master', string='District')
    farmer_state_id = fields.Many2one('farmer.state.master', string='State')
    bank_tamil_list_id = fields.Many2one('bank.tamil.list', string='Bank Tamil Name')

    # Tamil

    application_tamil_type = fields.Char(string='Application Type', default='கடன் பெறாதவர்')
    season_tamil_name = fields.Char(string='Season', default='ராபி')

    farmer_tamil_name = fields.Char(string='Farmer Name')
    relative_tamil_name = fields.Char(string='Relative Name')
    relative_tamil_type = fields.Selection([('son_of', 'மகன்'), ('daughter_of', 'மகள்'), ('wife_of', 'மனைவி')],
                                           string='Relation Type')
    farmer_tamil_type = fields.Char(string='Farmer Type', default='குறு')
    gender_tamil_type = fields.Selection([('Male', 'ஆண்'), ('Female', 'பெண்')], string='Gender')

    community_type = fields.Selection([('ST', 'ST'), ('SC', 'SC'),('OBC', 'OBC'), ('GENERAL', 'GENERAL')], string='Community')
    farmer_category_type = fields.Selection([('OWNER', 'OWNER'), ('TENANT', 'TENANT'),('SHARECROPPER', 'SHARECROPPER')], string='Farmer Category')

    form_serial_no = fields.Char(string='Serial Number', default='PMFBY2023FY1433')
    form_application_no = fields.Integer(string='Form Number')
    sheet_no = fields.Char(string='Form No')

    branch_tamil_name = fields.Char('Branch Name', size=60)
    bank_tamil_name = fields.Char('Bank Name', size=60)
    account_tamil_type = fields.Char(string='Account Type', default='சேமிப்பு')

    area = fields.Float(string='Area(Hectare)', required=True)
    premium_amount = fields.Float(string='Premium Amt (Rs)', required=True)
    service_charge = fields.Float(string='Service Amount', default=_default_service_charge)
    total_amount = fields.Float(string='Total Amount', required=True)
    received_amount = fields.Float(string='Farmer Paid Amount')
    balance_amount = fields.Float(string='Balance Amount')
    farmer_addr = fields.Text(string='Address')

    distributor_service_charge = fields.Float(string='Distributor Service Amt')
    distributor_total_amount = fields.Float(string='Distributor Total Amt', compute='_distributor_tracking',
                                      store=True, readonly=True)
    distributor_received_amount = fields.Float(string='Distributor Received Amt')
    distributor_balance_amount = fields.Float(string='Distributor Bal Amt', compute='_distributor_tracking',
                                      store=True, readonly=True)

    aadhar_name = fields.Char('Aadhar Name', size=60)
    aadhar_no = fields.Char('Aadhar No', size=60)
    csc_id = fields.Many2one('csc.login', string="CSC Login")
    # csc_id = fields.Char('CSC ID', size=60)
    pincode = fields.Char('Pincode', size=60)
    farmer_birth_year = fields.Integer('Birth Year')
    farmer_age = fields.Integer('Age', store=True, readonly=True, compute='_age_calculation')
    insurance_finished_date = fields.Date(string='Finished Date')

    pmfby_status = fields.Selection([('pmfbyPaid', 'PMFBY Paid'),('Paid', 'Paid'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Revert', 'Revert')], string='PMFBY Status')

    farmer_image = fields.Binary(string="Bill Farmer Image", attachment=True)
    licence_applicant_image = fields.Binary(string="Registration Farmer Image", attachment=True)
    allot_name = fields.Char('Allot Name', size=60)

    def capture_webcam_image(self):
        # Open the webcam
        import cv2
        import numpy as np
        from io import BytesIO
        import base64
        cap = cv2.VideoCapture(0)

        # Capture a frame from the webcam
        ret, frame = cap.read()

        if ret:
            # Encode the image as base64
            _, buffer = cv2.imencode('.png', frame)
            image_base64 = base64.b64encode(buffer)

            # Update the field with the captured image
            self.write({'farmer_image': image_base64})
        else:
            raise UserError("Unable to capture image from webcam.")

        # Release the webcam
        cap.release()

    def insurance_preview(self):
        return {'type': 'ir.actions.act_url',
                'url': '/multimedia/insurance_preview?id=' + str(self.id) + '&db=' + str(
                    self.env.cr.dbname) + '&uid=' + str(self.env.uid), 'nodestroy': True, 'target': 'new'}

    @api.onchange('farmer_type')
    def onchange_farmer_type(self):
        if self.farmer_type == 'marginal':
            self.farmer_tamil_type = 'சிறு'
        if self.farmer_type == 'small':
            self.farmer_tamil_type = 'குறு'
        if self.farmer_type == 'other':
            self.farmer_tamil_type = 'மற்ற'

    @api.onchange('form_application_no')
    def onchange_allot_num(self):
        if self.form_application_no:
            self.env.cr.execute('''SELECT shop_name
                               FROM allot_book_number_line
                               WHERE %s BETWEEN start_no AND end_no
                            ''', (self.form_application_no,))
            get_list = [x[0] for x in self.env.cr.fetchall()]
            if get_list:
                self.allot_name = get_list[0]          

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('farmer.insurance') or _('New')
            vals['sheet_no'] = 'PMFBY2022FY1432'+'-'+str(self.env.user.form_seqno)+'-'+str(vals['form_application_no'])
        if vals.get('auto_serial_no', _('New')) == _('New'):
            vals['auto_serial_no'] = self.env['ir.sequence'].next_by_code('farmer.insurance.serial') or _('New')
        return super(FarmerInsurance, self).create(vals)

    @api.constrains('form_application_no', 'original_receipt_no', 'sheet_no', 'distributor_received_amount', 'farmer_name','farmer_tamil_name')
    def _check_insurance_formno_receiptno(self):
        form_application_ids = self.env['farmer.insurance'].search([('id', '!=', self.id),('form_application_no', '=', self.form_application_no)])
        original_receipt_ids = self.env['farmer.insurance'].search([('id', '!=', self.id),('original_receipt_no', '=', self.original_receipt_no),('original_receipt_no', '!=', '')])
        sheet_no_ids = self.env['farmer.insurance'].search([('id', '!=', self.id),('sheet_no', '=', self.sheet_no)])
        if self.farmer_name:
            self.state = 'stage2'
        if self.farmer_tamil_name:
            self.state = 'stage3'
        # if form_application_ids.ids:
        #     raise ValidationError(_('Already Used this Form No, please check it'))
        if original_receipt_ids.ids:
            raise ValidationError(_('Already Used this Original Receipt No, please check it'))
        if sheet_no_ids.ids:
            raise ValidationError(_('Already Used this Form No, please check it'))
        if self.distributor_received_amount > self.distributor_total_amount:
            raise ValidationError(_('You enter the Received amount greater then total amount, please check it'))

    @api.onchange('area','received_amount', 'service_charge', 'district_id')
    def onchange_area_insured(self):
        # ~ base_insured_amt = 803.99000
        # base_insured_amt = 844.74000
        base_insured_amt = self.district_id.base_insured_amt
        # service_charge = 250
        if self.area * 100 > 0:
            area_insured = self.area * 100
            premium_amt = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
            self.premium_amount = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
            # self.service_charge = service_charge
            self.total_amount = premium_amt + self.service_charge
            tot = premium_amt + self.service_charge
            self.balance_amount = (premium_amt + self.service_charge) - self.received_amount

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_verified(self):
        self.write({'state': 'verified'})

    def action_reset(self):
        self.write({'state': 'draft'})

    def action_pending(self):
        self.write({'state': 'pending'})

    def action_done(self):
        if not self.original_receipt_no:
            raise ValidationError(_('Please Enter the Original Receipt No'))
        if self.distributor_balance_amount != 0:
            raise ValidationError(_('Please Complete the Distributer Balance'))
        self.write({'state': 'done'})

    @api.onchange('gender_type')
    def onchange_gender(self):
        if self.gender_type == 'Male':
            self.gender_tamil_type = 'Male'
        if self.gender_type == 'Female':
            self.gender_tamil_type = 'Female'

    @api.onchange('relative_type')
    def onchange_relative_type(self):
        if self.relative_type:
            self.relative_tamil_type = self.relative_type

    # @api.onchange('state_id')
    # def onchange_state_id(self):
    #     if self.state_id:
    #         self.state_id_tamil = self.state_id.tamil_name

    # @api.onchange('farmer_name', 'relative_name', 'branch_name')
    @api.onchange('branch_name')
    def onchange_tamil_translate(self):
    #     # if not self.farmer_name:
    #     #     self.farmer_name = ''
    #     # if not self.relative_name:
    #     #     self.relative_name = ''
        if not self.branch_name:
            self.branch_name = ''
        translator = Translator()
    #     # if self.farmer_name:
    #     #     translation_farmer = translator.translate(self.farmer_name, dest="ta")
    #     #     self.farmer_tamil_name = translation_farmer.text
    #     # if self.relative_name:
    #     #     translation_relation = translator.translate(self.relative_name, dest="ta")
    #     #     self.relative_tamil_name = translation_relation.text
        if self.branch_name:
            translation_branch_name = translator.translate(self.branch_name, dest="ta")
            self.branch_tamil_name = translation_branch_name.text

    @api.onchange('name', 'farmer_name', 'relative_name', 'crop_line_ids', 'district_id', 'total_area_insured',
                  'total_premium_paid', 'total_sum_insured')
    def generate_qr_code(self):
        from io import BytesIO
        qr = qrcode.QRCode(
            version=16,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        data = ''
        receipt_no = state_name = farmer_name = season_name = year_val = line_details = tsi = tai = tpp = ''
        if self.name:
            receipt_no = self.name + ", "
        if self.farmer_name:
            farmer_name = self.farmer_name + ", "
        if self.season_name:
            season_name = self.season_name + ", "
        if self.year_val:
            year_val = self.year_val + ", "
        if self.state_id:
            state_name = self.state_id.name + ", "
        line_details = "No of Crop(s) Insured:" + str(
            len(self.crop_line_ids)) + ' Crop(District, Area, Sum Insured(Rs.)):'
        if self.crop_line_ids:
            for line in self.crop_line_ids:
                line_details += line.crop_data + "(" + self.district_id.name + ", " + str(
                    round(line.area_insured, 3)) + "Hect ,Rs" + str(line.sum_insured) + ")"

        line_details += ','
        if self.total_premium_paid:
            tpp = "Total Farmer Premium: Rs. " + str(self.total_premium_paid) + ", "
        if self.total_area_insured:
            tai = "Total Area Insured " + str(self.total_area_insured) + " Hect,"
        if self.total_sum_insured:
            tsi = "Total Sum Insured Rs. " + str(self.total_sum_insured) + ', '

        data = "Content: Acknowledgement No:" + receipt_no + "Farmer Name:" + farmer_name + "Season: " + season_name + 'Year: ' + year_val + "State:" + state_name + line_details + tpp + tai + tsi + "Transaction Status: PAID, Application Source:CSC"

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
            datas = {'branch_name': '',
                     'bank_name': ''}
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
                    'bank_address': 'Wrong IFSC Code'
                })
            else:
                datas.update({
                    'branch_name': result['BRANCH'].replace('┬á', ''),
                    'bank_name': result['BANK'].replace('┬á', ''),
                    'ifsc_code':self.ifsc_code.upper()
                })
        return {'value': datas}

    @api.onchange('village_id')
    def onchange_village_id(self):
        if not self.village_id:
            self.firka_id = False
            self.block_id = False
            self.subdistrict_id = False
            self.district_id = False
            # self.state_id = False

            self.village_tamil_name = False
            self.firka_tamil_name = False
            self.block_tamil_name = False
            self.subdistrict_tamil_name = False
            self.district_tamil_name = False
            self.state_tamil_name = False

        if self.village_id:
            self.firka_id = self.village_id.firka_id.id
            self.block_id = self.village_id.block_id.id
            self.subdistrict_id = self.village_id.subdistrict_id.id
            self.district_id = self.village_id.district_id.id
            self.state2_id = self.village_id.state_id.id

            self.village_tamil_name = self.village_id.village_tamil_name
            self.firka_tamil_name = self.village_id.firka_id.firka_tamil_name
            self.block_tamil_name = self.village_id.block_id.block_tamil_name
            self.subdistrict_tamil_name = self.village_id.subdistrict_id.subdistrict_tamil_name
            self.district_tamil_name = self.village_id.district_id.district_tamil_name
            self.state_tamil_name = self.village_id.state_id.tamil_name

    @api.onchange('farmer_village_id')
    def onchange_farmer_addr(self):
        if not self.farmer_village_id:
            self.farmer_taluk_id = False
            self.farmer_district_id = False
            self.farmer_state_id = False

        if self.farmer_village_id:
            self.farmer_taluk_id = self.farmer_village_id.taluk_id.id
            self.farmer_district_id = self.farmer_village_id.district_id.id
            self.farmer_state_id = self.farmer_village_id.state_id.id

    def insurance_bill_print(self):
        self.write({'state': 'printtaken'})
        return self.env.ref('multimedia.action_report_insurance').report_action(self)

    def insurance_tamil_bill_print(self):
        self.write({'state': 'printtaken'})
        return self.env.ref('multimedia.action_report_tamil_insurance').report_action(self)

    def insurance_overall_print(self):
        self.write({'state': 'printtaken'})
        return self.env.ref('multimedia.action_report_overall_insurance').report_action(self)

    def insurance_fine_print(self):
        self.write({'state': 'printtaken'})
        return self.env.ref('multimedia.action_report_fine_insurance').report_action(self)
    
    def insurance_preview_print(self):
        self.write({'state': 'printtaken'})
        return self.env.ref('multimedia.action_report_insurance_preview_print').report_action(self)

class CropDataLine(models.Model):
    _name = 'crop.data.line'
    _description = 'Crop Data Line details'

    survey_no = fields.Char('Survey No', required=True)
    khasra_no = fields.Char('Khasra No', required=True)
    sum_insured = fields.Float(string='Sum Insured', required=True)
    area_insured = fields.Float(string='Area Insured', required=True, digits='Product Unit of Measure')
    gov_share = fields.Float(string='Gov Share', required=True)
    farmer_share = fields.Float(string='Farmer Share', required=True)
    crop_data = fields.Char('Crop', required=True, default='Paddy- II')
    crop_id = fields.Many2one('farmer.insurance', string='Insurance')
    doc_html = fields.Html('HTML Report')

    # @api.onchange('area_insured')
    # def onchange_area_insured(self):
    #     # base_insured_amt = 803.99000
    #     base_insured_amt = 844.74000
    #     if self.area_insured * 100 > 0:
    #         area_insured = self.area_insured * 100
    #         self.farmer_share = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
    #         self.gov_share = round((249.2 * area_insured), 2)
    #         # self.gov_share = round(((0.84474 * 338.9807383627608) * area_insured), 2)
    #         # self.gov_share = round(((0.80399 * 335) * area_insured), 2)
    #         self.sum_insured = round(base_insured_amt * area_insured, 2)    

    # @api.onchange('area_insured')
    # def onchange_area_insured(self):
    #     # base_insured_amt = 803.99000
    #     base_insured_amt = 870.68000
    #     if self.area_insured * 100 > 0:
    #         area_insured = self.area_insured * 100
    #         self.farmer_share = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
    #         self.gov_share = round((249.2 * area_insured), 2)
    #         # self.gov_share = round(((0.84474 * 338.9807383627608) * area_insured), 2)
    #         # self.gov_share = round(((0.80399 * 335) * area_insured), 2)
    #         self.sum_insured = round(base_insured_amt * area_insured, 2)

    @api.onchange('area_insured')
    def onchange_area_insured(self):
        if self.crop_id.district_id:
            base_insured_amt = self.crop_id.district_id.base_insured_amt
            if self.area_insured * 100 > 0:
                area_insured = self.area_insured * 100
                self.farmer_share = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
                self.gov_share = round((self.crop_id.district_id.government_share * area_insured), 2)
                self.sum_insured = round(base_insured_amt * area_insured, 2)


    @api.onchange('survey_no','khasra_no')
    def onchange_survey_no_details(self):
        html = ''
        html = """
                <html>
                    <body>
                """
        html += """
                <p style="font-size:145%;text-align:center;color: #1c3652;">Land Details</p>
                    <table style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;tr:nth-child(even) {background-color: #f2f2f2;">
                        <tr style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">
                            <th width="100"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Survey No Wise S.No</th>
                            <th width="100" style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Name Wise S.No</th>
                            <th width="100" style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Farmer Name</th>
                            <th width="200" style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Relative type</th>
                            <th width="250"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Reltive Name</th>
                            <th width="100"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Survey No</th>
                            <th width="100"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Sub div No</th>
                            <th width="100"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Hec</th>
                            <th width="100"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Patta No</th>
                            <th width="400"  style="background-color: #d4e6f1;border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">Land Type</th>
                        </tr>
                """
        if self.survey_no and self.khasra_no:
            count = 0
            land_data_ids = self.env['surveyno.wise.land.details'].search([('survey_no', '=', self.survey_no),('sub_div_no', '=', self.khasra_no)])
            if land_data_ids:
                for xx in land_data_ids:
                    print (xx.relative_name)
                    count += 1
                    bgc = ''
                    if (count % 2) == 0:
                        bgc = '#f2f4f2'
                    else:
                        bgc = '#F0FFF0'
                    html += """<tr style="background-color: """ + bgc + """">
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.surveyno_wise_serial_no + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.name_wise_serial_no + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.name + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.relation_type + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.relative_name + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.survey_no + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.sub_div_no + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.area_in_hec + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.patta_no + """</td>
                                        <td align='left' style="border-width:1px;border-color:#D3D3D3;border-style:solid;border-collapse: collapse;">""" + \
                            xx.land_type + """</td>
                                            </tr>
                                        """
            html += """
                           </table>
                           </body>
                          </html>
                               """
        self.doc_html =  html



class StateMaster(models.Model):
    _name = 'state.master'
    _description = 'State Master'
    _order = "name asc"

    name = fields.Char('State Name', required=True)
    state_code = fields.Char('State Code', required=True)
    tamil_name = fields.Char('State Tamil', required=True)
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
    district_tamil_name = fields.Char('District Tamil Name', required=True)
    district_code = fields.Char('District Code')
    insurance_company = fields.Char('Insurance Company')
    insurance_email = fields.Char('Insurance Email')
    insurance_addr1 = fields.Char('Insurance Addr')
    insurance_addr2 = fields.Char('Insurance street')

    insurance_tamil_company = fields.Char('Insurance Tamil Company')
    insurance_tamil_email = fields.Char('Insurance Tamil Email')
    insurance_tamil_addr1 = fields.Char('Insurance Tamil Addr')
    insurance_tamil_addr2 = fields.Char('Insurance Tamil street')
    
    base_insured_amt = fields.Float(string='Base Insured Amount', required=True)
    government_share = fields.Float(string='Government Share', required=True)    

    state_id = fields.Many2one('state.master', string='State', required=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated Date', readonly=True)
    write_uid = fields.Many2one('res.users', string='Last Modified by', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)
    active = fields.Boolean('Active', default=True)
    subdistrict_ids = fields.One2many('subdistrict.master', 'district_id', "Dub District Records")
    taluk_ids = fields.One2many('taluk.master', 'district_id', "Taluk Records")

    area_calculation = fields.Float(string='Area Base', required=True)



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
    subdistrict_tamil_name = fields.Char('Sub District Tamil Name', required=True)
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
    block_tamil_name = fields.Char('Block Tamil Name', required=True)
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
    firka_tamil_name = fields.Char('Firka Tamil Name', required=True)
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
    village_tamil_name = fields.Char('Village Tamil Name', required=True)
    village_code = fields.Char('Village Code', readonly=True, default=lambda self: _('New'))
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
    land_ids = fields.One2many('surveyno.wise.land.details', 'land_id', "Land Details Records")

    def name_get(self):
        res = []
        for order in self:
            name = order.name
            if order.firka_id and order.block_id and order.subdistrict_id and order.district_id:
                name = '%s / %s / %s / %s / %s' % (name, order.firka_id.name, order.block_id.name, order.subdistrict_id.name, order.district_id.name)
            res.append((order.id, name))
        return res

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
    taluk_code = fields.Char('Taluk Code', readonly=True, default=lambda self: _('New'))
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
    name = fields.Char('Name', required=True)

    def action_import_pmjay_village(self):
        import base64
        import csv
        import io
        for order in self:
            count = 0
            count = name_count = 0
            district_id = 0
            panchayat_id = 0
            block_id = 0
            village_count = 0

            decrypted = base64.b64decode(order.import_file).decode('utf-8')
            with io.StringIO(decrypted) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                for row in reader:
                    if not row:
                        break
                    count += 1
                    if count > 1 and len(row) > 2:
                        district_code = row[0]
                        district_name = row[1]
                        block_code = row[2]
                        block_name = row[3]
                        panchayat_code = row[4]
                        panchayat_name = row[5]
                        village_code = row[6]
                        village_name = row[7]
                        if district_code and district_name:
                            exist_district_ids = self.env['pmjay.district'].search([('name', '=', district_name)])
                            if not exist_district_ids:
                                district = self.env['pmjay.district'].create(
                                    {'name': district_name, 'district_code': district_code})
                                district_id = district.id
                        if block_code and block_name:
                            print (block_code,block_name,district_id)
                            exist_block_ids = self.env['pmjay.block'].search([('name', '=', block_name)])
                            if not exist_block_ids:
                                block = self.env['pmjay.block'].create(
                                    {'name': block_name, 'block_code': block_code, 'district_id': district_id})
                                block_id = block.id
                        if panchayat_code and panchayat_name:
                            print (panchayat_code,panchayat_code,district_id)
                            exist_block_ids = self.env['pmjay.panchayat'].search([('name', '=', panchayat_name)])
                            if not exist_block_ids:
                                panchayat = self.env['pmjay.panchayat'].create(
                                    {'name': panchayat_name, 'panchayat_code': panchayat_code, 'district_id': district_id, 'block_id': block_id})
                                panchayat_id = panchayat.id
                        if village_code and village_name:
                            exist_village_ids = self.env['pmjay.village'].search([('name', '=', village_name),('panchayat_id', '=', panchayat_id)])
                            if not exist_village_ids:
                                village = self.env['pmjay.village'].create(
                                    {'name': village_name, 'village_code': village_code, 'panchayat_id': panchayat_id, 'district_id': district_id, 'block_id': block_id})

    def action_import_land_details(self):
        import base64
        import csv
        import io
        for order in self:
            count = 0
            decrypted = base64.b64decode(order.import_file).decode('utf-8')
            with io.StringIO(decrypted) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                for row in reader:
                    if not row:
                        break
                    count += 1
                    if count > 1 and len(row) > 2:
                        print(row[10])
                        village_id = self.env['village.master'].search([('name', 'ilike', row[10])]).id
                        if not village_id:
                            raise ValidationError(_('Please check the village'))
                        print (village_id,"aaaaaaaaaaa")
                        surveyno_wise_serial_no = row[0]
                        name_wise_serial_no = row[1]
                        farmer_name = row[2]
                        relation_type = row[3]
                        relative_name = row[4]
                        survey_no = row[5]
                        sub_div_no = row[6]
                        area_in_hec = row[7]
                        patta_no = row[8]
                        land_type = row[9]
                        self.env['surveyno.wise.land.details'].create(
                            {'name': farmer_name,
                             'surveyno_wise_serial_no': surveyno_wise_serial_no,
                             'name_wise_serial_no': name_wise_serial_no,
                             'relation_type': relation_type,
                             'relative_name': relative_name,
                             'survey_no': survey_no,
                             'sub_div_no': sub_div_no,
                             'area_in_hec': area_in_hec,
                             'patta_no': patta_no,
                             'land_type': land_type,
                             'land_id': village_id,
                             })
    def action_import_pmjay(self):
        import base64
        import csv
        import io
        for order in self:
            count = 0
            decrypted = base64.b64decode(order.import_file).decode('utf-8')
            with io.StringIO(decrypted) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                parent_list = []
                child_list = []
                for row in reader:
                    # if not row:
                    #     break
                    count += 1
                    # print (count,len(row),"----------------")
                    if count > 1:
                        parent_data = {
                            'name': row[1],
                            'serial_no': row[0],
                        }
                        parent_list.append(parent_data)

                        if row[3] == 'Y':
                            val = True
                        if row[3] == 'N':
                            val = False

                        child_data = {
                            'name': row[2],
                            # 'parent_id': parent_record.id,
                            'kyc_update': val,
                        }
                        child_list.append(child_data)

                        if not row[0]:
                            print (parent_list,"ccccccccccccc")
                            print (parent_list[:-1][-1],child_list[:-1],"--------------------")
                            parent_list = parent_list[:-1][-1]
                            child_list = child_list[:-1]
                            result = []
                            print (parent_list,"ffffffffff")
                            if parent_list:
                                parent = self.env['pmjay.health.insurance'].create(parent_list)
                                print (parent,"xxxxxxxxxxxxxxx")
                                for line in child_list:
                                    result.append((0, 0, line))
                                    # line.update({'pmjay_id':parent.id})
                                parent.write({'pmjay_hi_members_ids':result})

                                    # self.env[self.child_model.model].create(child_data)
                            # parent_list = list(set(parent_list))
                            # child_list = list(set(child_list))
                            parent_list = []
                            child_list = []





                    # if count > 1 and len(row) > 2:
                    #
                    #     print(row[10])
                        # village_id = self.env['village.master'].search([('name', 'ilike', row[10])]).id
                        # if not village_id:
                        #     raise ValidationError(_('Please check the village'))
                        # print (village_id,"aaaaaaaaaaa")
                        # surveyno_wise_serial_no = row[0]
                        # name_wise_serial_no = row[1]
                        # farmer_name = row[2]
                        # relation_type = row[3]
                        # relative_name = row[4]
                        # survey_no = row[5]
                        # sub_div_no = row[6]
                        # area_in_hec = row[7]
                        # patta_no = row[8]
                        # land_type = row[9]
                        # self.env['surveyno.wise.land.details'].create(
                        #     {'name': farmer_name,
                        #      'surveyno_wise_serial_no': surveyno_wise_serial_no,
                        #      'name_wise_serial_no': name_wise_serial_no,
                        #      'relation_type': relation_type,
                        #      'relative_name': relative_name,
                        #      'survey_no': survey_no,
                        #      'sub_div_no': sub_div_no,
                        #      'area_in_hec': area_in_hec,
                        #      'patta_no': patta_no,
                        #      'land_type': land_type,
                        #      'land_id': village_id,
                        #      })

    # def action_import_land_details(self):
    #     import base64
    #     import csv
    #     import io
    #     for order in self:
    #         count = 0
    #         decrypted = base64.b64decode(order.import_file).decode('utf-8')
    #         with io.StringIO(decrypted) as fp:
    #             reader = csv.reader(fp, delimiter=",", quotechar='"')
    #             for row in reader:
    #                 if not row:
    #                     break
    #                 count += 1
    #                 if count > 1 and len(row) > 2:
    #                     print(row)
    #                     surveyno_wise_serial_no = row[0]
    #                     name_wise_serial_no = row[1]
    #                     farmer_name = row[2]
    #                     relation_type = row[3]
    #                     relative_name = row[4]
    #                     survey_no = row[5]
    #                     sub_div_no = row[6]
    #                     area_in_hec = row[7]
    #                     patta_no = row[8]
    #                     land_type = row[9]
    #                     self.env['surveyno.wise.land.details'].create(
    #                         {'name': farmer_name,
    #                          'surveyno_wise_serial_no': surveyno_wise_serial_no,
    #                          'name_wise_serial_no': name_wise_serial_no,
    #                          'relation_type': relation_type,
    #                          'relative_name': relative_name,
    #                          'survey_no': survey_no,
    #                          'sub_div_no': sub_div_no,
    #                          'area_in_hec': area_in_hec,
    #                          'patta_no': patta_no,
    #                          'land_type': land_type,
    #                          })

    def action_farmer_addr_import(self):
        import base64

        import csv
        import io
        for order in self:
            count = 0
            count = name_count = 0
            district_id = 0
            taluk_id = 0
            village_count = 0

            decrypted = base64.b64decode(order.import_file).decode('utf-8')
            with io.StringIO(decrypted) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                for row in reader:
                    if not row:
                        break
                    count += 1
                    if count > 1 and len(row) > 2:
                        # print(row)
                        district_code = row[0]
                        district_name = row[1]
                        taluk_code = row[2]
                        taluk_name = row[3]
                        village_code = row[4]
                        village_name = row[5]
                        if district_code and district_name:
                            district = self.env['farmer.district.master'].create(
                                {'name': district_name, 'district_code': district_code, 'state_id': 1})
                            district_id = district.id
                        if taluk_code and taluk_name:
                            taluk = self.env['farmer.taluk.master'].create(
                                {'name': taluk_name, 'taluk_code': taluk_code, 'district_id': district_id,
                                 'state_id': 1})
                            taluk_id = taluk.id
                        if village_code and village_name:
                            village_count += 1
                            self.env['farmer.village.master'].create(
                                {'name': village_name, 'village_code': village_code, 'state_id': 1,
                                 'district_id': district_id, 'taluk_id': taluk_id})

    def action_import(self):
        for order in self:
            from odoo import api, fields, models, _
            from datetime import datetime
            from odoo.exceptions import AccessError, UserError, ValidationError
            import base64

            import csv
            import io
            count = 0
            count = name_count = 0
            district_id = 0
            subdistrict_id = 0
            block_id = 0
            taluk_id = 0
            firka_id = 0
            village_count = 0

            decrypted = base64.b64decode(order.import_file).decode('utf-8')
            with io.StringIO(decrypted) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                for row in reader:
                    if not row:
                        break
                    count += 1
                    if count > 1 and len(row) > 2:
                        # print(row)
                        district_english = row[0]
                        district_tamil = row[1]
                        subdistrict_english = row[2]
                        subdistrict_tamil = row[3]
                        block_english = row[4]
                        block_tamil = row[5]
                        firka_english = row[6]
                        firka_tamil = row[7]
                        village_english = row[8]
                        village_tamil = row[9]
                        print (district_english,subdistrict_english,block_english,firka_english,village_tamil)
                        if district_english and district_tamil:
                            exist_district_ids = self.env['district.master'].search([('name', '=', district_english)])
                            if not exist_district_ids:
                                district = self.env['district.master'].create(
                                    {'name': district_english, 'district_tamil_name': district_tamil, 'state_id': 1})
                                district_id = district.id
                        if subdistrict_english and subdistrict_english:
                            exist_subdistrict_ids = self.env['subdistrict.master'].search([('name', '=', subdistrict_english),('district_id', '=', district_id),('id', '>', 15)])
                            if not exist_subdistrict_ids:
                                subdistrict = self.env['subdistrict.master'].create(
                                    {'name': subdistrict_english, 'subdistrict_tamil_name': subdistrict_tamil,
                                    'district_id': district_id, 'state_id': 1})
                                subdistrict_id = subdistrict.id
                        if block_english and block_tamil:
                            exist_block_ids = self.env['block.master'].search([('name', '=', block_english),('district_id', '=', district_id),('id', '>', 30)])
                            if not exist_block_ids:
                                block = self.env['block.master'].create(
                                    {'name': block_english, 'block_tamil_name': block_tamil,
                                    'subdistrict_id': subdistrict_id, 'district_id': district_id, 'state_id': 1})
                                block_id = block.id
                        if firka_english and firka_tamil:
                            exist_firka_ids = self.env['firka.master'].search([('name', '=', firka_english),('district_id', '=', district_id),('id', '>', 60)])
                            if not exist_firka_ids:
                                firka = self.env['firka.master'].create(
                                    {'name': firka_english, 'firka_tamil_name': firka_tamil, 'block_id': block_id,
                                    'subdistrict_id': subdistrict_id, 'district_id': district_id, 'state_id': 1})
                                firka_id = firka.id
                        if village_english and village_tamil:
                            village_count += 1
                            exist_village_ids = self.env['village.master'].search([('name', '=', village_english),('district_id', '=', district_id),('id', '=', 787)])
                            if not exist_village_ids:
                                print (district_id,subdistrict_id,block_id,firka_id)
                                self.env['village.master'].create(
                                    {'name': village_english, 'village_tamil_name': village_tamil,
                                    'village_code': village_count,
                                    'state_id': 1,
                                    'district_id': district_id,
                                    'subdistrict_id': subdistrict_id,
                                    'block_id': block_id,
                                    'firka_id': firka_id
                                    })

    def action_import232323(self):
        for order in self:
            count = 0
            import_file = str(base64.decodestring(order.import_file), 'windows-1252', 'strict').split('\n')
            count = name_count = 0
            district_id = subdistrict_id = block_id = 0
            taluk_id = 0
            village_count = 0
            for line in import_file:
                row = line.split(',')
                # ~ print (row)
                if not row:
                    break
                count += 1
                if count > 3 and len(row) > 1:
                    print(row)
                    district_name = row[1]
                    subdistrict_name = row[2]
                    block_name = row[3]
                    firka_name = row[4]
                    village_name = row[5]
                    village_code = row[6]
                    print(district_name, subdistrict_name, block_name, firka_name, village_name, village_code)
                    if district_name:
                        district = self.env['district.master'].create({'name': district_name, 'state_id': 1})
                        district_id = district.id
                    if subdistrict_name:
                        subdistrict = self.env['subdistrict.master'].create(
                            {'name': subdistrict_name, 'state_id': 1, 'district_id': district_id})
                        subdistrict_id = subdistrict.id
                    if block_name:
                        block = self.env['block.master'].create(
                            {'name': block_name, 'state_id': 1, 'district_id': district_id,
                             'subdistrict_id': subdistrict_id})
                        block_id = block.id
                    if firka_name:
                        firka = self.env['firka.master'].create(
                            {'name': firka_name, 'state_id': 1, 'district_id': district_id,
                             'subdistrict_id': subdistrict_id, 'block_id': block_id})
                        firka_id = firka.id
                    if village_name:
                        village = self.env['village.master'].create(
                            {'name': village_name, 'village_code': village_code, 'state_id': 1,
                             'district_id': district_id, 'subdistrict_id': subdistrict_id, 'block_id': block_id,
                             'firka_id': firka_id})

                    # ~ if district_code and district_name:
                    # ~ district = self.env['district.master'].create({'name': district_name, 'district_code': district_code, 'state_id': 1})
                    # ~ district_id = district.id
                    # ~ if taluk_code and taluk_name:
                    # ~ taluk = self.env['taluk.master'].create({'name': taluk_name, 'taluk_code': taluk_code, 'district_id': district_id, 'state_id': 1})
                    # ~ taluk_id = taluk.id
                    # ~ if village_code and village_name:
                    # ~ village_count += 1
                    # ~ self.env['village.master'].create({'name': village_name, 'village_code': village_code, 'state_id': 1, 'district_id': district_id, 'taluk_id': taluk_id})


class FarmerMaster(models.Model):
    _name = 'farmer.master'
    _description = 'Farmer details'

    @api.depends('premium_amount','received_amount')
    def amount_all(self):
        balance = 0
        if self.received_amount:
            balance = self.total_amount-self.received_amount
            self.update({"balance_amount": balance})

    name = fields.Char('Farmer Name')
    village_id = fields.Many2one('village.master', string='Village', required=True)
    firka_id = fields.Many2one('firka.master', string='Firka', required=True)
    block_id = fields.Many2one('block.master', string='Block', required=True)
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)
    mobile_no = fields.Char(string='Mobile No', required=True)
    area = fields.Float(string='Area(Hectare)', required=True)
    premium_amount = fields.Float(string='Premium Amt (Rs)', required=True)
    service_charge = fields.Float(string='Service Amount')
    total_amount = fields.Float(string='Total Amount')
    received_amount = fields.Float(string='Received Amount')
    balance_amount = fields.Float(string='Balance Amount',compute='amount_all',store=True)

    @api.onchange('village_id')
    def onchange_village_id(self):
        if not self.village_id:
            self.firka_id = False
            self.block_id = False
            self.subdistrict_id = False
            self.district_id = False
            # self.state_id = False

            self.village_tamil_name = False
            self.firka_tamil_name = False
            self.block_tamil_name = False
            self.subdistrict_tamil_name = False
            self.district_tamil_name = False
            self.state_tamil_name = False

        if self.village_id:
            self.firka_id = self.village_id.firka_id.id
            self.block_id = self.village_id.block_id.id
            self.subdistrict_id = self.village_id.subdistrict_id.id
            self.district_id = self.village_id.district_id.id
            self.state_id = self.village_id.state_id.id

            self.village_tamil_name = self.village_id.village_tamil_name
            self.firka_tamil_name = self.village_id.firka_id.firka_tamil_name
            self.block_tamil_name = self.village_id.block_id.block_tamil_name
            self.subdistrict_tamil_name = self.village_id.subdistrict_id.subdistrict_tamil_name
            self.district_tamil_name = self.village_id.district_id.district_tamil_name
            self.state_tamil_name = self.village_id.state_id.tamil_name

    @api.onchange('area')
    def onchange_area_insured(self):
        # ~ base_insured_amt = 803.99000
        base_insured_amt = 844.74000
        service_charge = 250
        if self.area * 100 > 0:
            area_insured = self.area * 100
            premium_amt = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
            self.premium_amount = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
            self.service_charge = service_charge
            self.total_amount = premium_amt + service_charge

    @api.onchange('service_charge')
    def onchange_service_charge(self):
        self.total_amount = self.premium_amount + self.service_charge


class SurveynoWiseLandDetails(models.Model):
    _name = 'surveyno.wise.land.details'
    _description = 'Surveyno Wise Land Details'

    name = fields.Char('Farmer Name')
    surveyno_wise_serial_no = fields.Char('Survey No Wise Serial No')
    name_wise_serial_no = fields.Char('Name Wise Serial No')
    relation_type = fields.Char('Relation Type')
    relative_name = fields.Char('Relative Name')
    survey_no = fields.Char('Survey No')
    sub_div_no = fields.Char('Sub Div No')
    area_in_hec = fields.Char('Hec')
    patta_no = fields.Char('Patta No')
    land_type = fields.Char('Land Type')
    land_id = fields.Many2one('village.master', string='Village', required=True)

class BankTamilList(models.Model):
    _name = 'bank.tamil.list'
    _description = 'Bank Tamil Name List Details'

    name = fields.Char('Farmer Name')

class CSCLogin(models.Model):
    _name = 'csc.login'
    _description = 'CSC Logins List Details'

    name = fields.Char('Login ID')

class VillageSearch(models.Model):
    _name = 'village.search'
    _description = 'Village Search List Details'

    village_id = fields.Many2one('village.master', string='Village', required=True)
    firka_id = fields.Many2one('firka.master', string='Firka', required=True)
    block_id = fields.Many2one('block.master', string='Block', required=True)
    subdistrict_id = fields.Many2one('subdistrict.master', string='Sub District', required=True)
    district_id = fields.Many2one('district.master', string='District', required=True)
    state_id = fields.Many2one('state.master', string='State', required=True)

    @api.onchange('village_id')
    def onchange_village_id(self):
        if self.village_id:
            self.firka_id = self.village_id.firka_id.id
            self.block_id = self.village_id.block_id.id
            self.subdistrict_id = self.village_id.subdistrict_id.id
            self.district_id = self.village_id.district_id.id
            self.state_id = self.village_id.state_id.id


class AllotBookNumber(models.Model):
    _name = 'allot.book.number'
    _description = 'Allot book Numbers Details'

    name = fields.Char('Year', required=True)
    allot_line_ids = fields.One2many('allot.book.number.line', 'allot_id', "Allot Number Data")


class AllotBookNumberLine(models.Model):
    _name = 'allot.book.number.line'
    _description = 'Allot book Numbers Line Details'

    allot_id = fields.Many2one('allot.book.number', string='Allot Number')
    start_no = fields.Integer('Start No')
    end_no = fields.Integer('End No')
    shop_name = fields.Char('Shop Name')



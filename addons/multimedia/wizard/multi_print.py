from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class MultiDeliveryPass(models.TransientModel):
    _name = "multi.bill.print"
    _description = "Multi Bill print"
    
    start_no = fields.Integer(string="Start No")
    end_no = fields.Integer(string="End No")
    insurance_numbers = fields.Text('Print Numbers')

    extra_area = fields.Float(string='Extra Area(Hectare)')

    extra_area_check = fields.Boolean('Extra Area')
    extra_area_amt_check = fields.Boolean('Extra Amount')
    
    def print_report(self):
        input_string = self.insurance_numbers
        integer_list = [int(x) for x in input_string.split(',')]
        insurance_ids = self.env['farmer.insurance'].search([('form_application_no', 'in', integer_list),('id', '>', 745)])
        

        # insurance_ids = self.env['farmer.insurance'].search([('form_application_no', '>=', self.start_no),('form_application_no', '<=', self.end_no)])
        return self.env.ref('multimedia.report_multi_insurance_pdf_print').report_action(insurance_ids)
    
    def multi_calculation(self):
        input_string = self.insurance_numbers
        integer_list = [int(x) for x in input_string.split(',')]        
        insurance_ids = self.env['farmer.insurance'].search([('form_application_no', 'in', integer_list),('id', '>', 745)])
        if insurance_ids:            
            for insurance in insurance_ids:
                valuedict = {}
                extra_area_amt = 0
                extra_area_check = False
                extra_area_amt_check = False
                if not insurance.district_id:
                    raise ValidationError(_('District is not available in form number %s') % insurance.form_application_no)
                base_insured_amt = insurance.district_id.base_insured_amt
                if self.extra_area * 100 > 0:
                    area_insured = self.extra_area * 100
                    extra_area_amt = round(((base_insured_amt * (1.5 / 100)) * area_insured), 2)
                    if self.extra_area_check == True:
                        extra_area_check = True
                    if self.extra_area_amt_check == True:
                        extra_area_amt_check = True
                    if self.extra_area_check == False:
                        extra_area_check = False
                    if self.extra_area_amt_check == False:
                        extra_area_amt_check = False
                    valuedict.update({'extra_area':self.extra_area,'extra_area_amt':extra_area_amt,'extra_area_check':extra_area_check,'extra_area_amt_check':extra_area_amt_check})                    
                    insurance.write(valuedict)

    def multi_attachment_download(self):
        return {'type': 'ir.actions.act_url',
                'url': '/multimedia/multi_attachment_download?id=' + str(self.id) + '&db=' + str(
                    self.env.cr.dbname)+ '&start_no=' + str(self.start_no)+ '&end_no=' + str(self.end_no)+ '&insurance_numbers=' + str(self.insurance_numbers) + '&uid=' + str(self.env.uid), 'nodestroy': True, 'target': 'new'}


from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class MultiDeliveryPass(models.TransientModel):
    _name = "multi.bill.print"
    _description = "Multi Bill print"
    
    start_no = fields.Integer(string="Start No")
    end_no = fields.Integer(string="End No")
    insurance_numbers = fields.Text('Print Numbers')
    
    def print_report(self):
        input_string = self.insurance_numbers
        integer_list = [int(x) for x in input_string.split(',')]
        print(integer_list)
        insurance_ids = self.env['farmer.insurance'].search([('form_application_no', 'in', integer_list)])

        # insurance_ids = self.env['farmer.insurance'].search([('form_application_no', '>=', self.start_no),('form_application_no', '<=', self.end_no)])
        return self.env.ref('multimedia.report_multi_insurance_pdf_print').report_action(insurance_ids)

    def multi_attachment_download(self):
        return {'type': 'ir.actions.act_url',
                'url': '/multimedia/multi_attachment_download?id=' + str(self.id) + '&db=' + str(
                    self.env.cr.dbname)+ '&start_no=' + str(self.start_no)+ '&end_no=' + str(self.end_no) + '&uid=' + str(self.env.uid), 'nodestroy': True, 'target': 'new'}


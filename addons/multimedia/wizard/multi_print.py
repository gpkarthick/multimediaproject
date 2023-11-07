from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class MultiDeliveryPass(models.TransientModel):
    _name = "multi.bill.print"
    _description = "Multi Bill print"
    
    start_no = fields.Integer(string="Start No")
    end_no = fields.Integer(string="End No")
    
    def print_report(self):
        insurance_ids = self.env['farmer.insurance'].search([('form_application_no', '>=', self.start_no),('form_application_no', '<=', self.end_no)])
        print (insurance_ids,">>>>>>>>>>>>>>>>>")
        # ~ return self.env['report'].get_action(insurance_ids, 'multimedia.farmer_insurance_fine_report_multimedia')
        
        # ~ return self.env.ref('multimedia.farmer_insurance_fine_report_multimedia').render(insurance_ids)
        pdf, _ = report_template.render(insurance_ids.ids)

        # Return the PDF report
        return pdf

    def multi_attachment_download(self):
        return {'type': 'ir.actions.act_url',
                'url': '/multimedia/multi_attachment_download?id=' + str(self.id) + '&db=' + str(
                    self.env.cr.dbname)+ '&start_no=' + str(self.start_no)+ '&end_no=' + str(self.end_no) + '&uid=' + str(self.env.uid), 'nodestroy': True, 'target': 'new'}


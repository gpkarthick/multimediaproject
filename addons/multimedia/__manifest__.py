{
    'name': 'Multi Meida',
    'version': '1.1',
    'category': 'General',
    'summary': 'Multi Meida Appliation',
    'description': """
		This module contains MultiMeida application...
    """,
    'depends': ['base','base_setup','mail','product'],
    'data': [
		'security/multimedia_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/import_master_view.xml',
        'views/corporate_master_view.xml',
        'views/multimedia_view.xml',
        'views/purchase_view.xml',
        'views/pan_view.xml',
        'views/account_verification_view.xml',
        'views/website_templates.xml',
        'views/site_access_view.xml',
        'views/farmer_insurance_view.xml',
        'views/prime_pmfby_view.xml',
        'views/pmjay_health_insurance_view.xml',
        'report/multimedia_report.xml',
        'report/farmer_insurance_report.xml',   
        'report/farmer_insurance_overall_report.xml',
        'report/farmer_insurance_fine_report.xml',
        'report/farmer_insurance_tamil_report.xml',
        'report/pmjay_kyc_report.xml',
        'report/multimedia_ebbill_report.xml',
        'report/account_verification_report.xml',
        'report/pan_acknowledgement_report.xml',
        'report/farmer_insurance_preview_print.xml',        
        'report/farmer_insurance_short_form.xml',        
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

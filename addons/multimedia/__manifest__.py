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
        'views/multimedia_view.xml',
        'views/purchase_view.xml',
        'views/pan_view.xml',
        'views/website_templates.xml',    
        'report/multimedia_report.xml',    
        'report/multimedia_ebbill_report.xml',    
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

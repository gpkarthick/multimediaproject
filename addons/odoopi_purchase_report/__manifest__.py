# -*- coding: utf-8 -*-
{
    'name': "Purchase Dashboard",

    'summary': """
    Purchase Dashboard With Graph
    """,

    'description': """
    ser can easy view user name, purchase request, purchase order, invoiced
                    purchase
                    order, locked
                    purchase order and cancelled order
    """,

    'author': "Sivasankar",
    'maintainer': "Karthick GP",
    'website': "",
    # 'price': 13,
    # 'currency': 'EUR',
    'license': 'OPL-1',
    'category': 'purchase',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'marine'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/sales_views.xml',
        'views/templates.xml',
    ],
    'images': ['static/description/screen_1.png', 'static/description/screen_2.png',
               'static/description/screen_3.png',
               'static/description/screen_3.png'],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

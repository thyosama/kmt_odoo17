# -*- coding: utf-8 -*-
{
    'name': "Custom PDF Quote",
    'summary': "Customized sales report for Sales Order",
    'description': """
     This module adds a custom sales Order report.
    """,
    'author': 'Abo Osama',
    'email': 'aboosama.odoodev@gmail.com',
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'sale', 'custom_so_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/custom_pdf_quote_report_layout.xml',
        'reports/custom_pdf_quote_report.xml',
        'reports/custom_pdf_quote_template.xml',
        'reports/inherit_report_saleorder.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}


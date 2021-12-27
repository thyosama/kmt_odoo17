# -*- coding: utf-8 -*-
{
    'name': "kmt_adjustment",
    'summary': """KMT Adjustment""",
    'description': """KMT Adjustment""",
    'author': "Almoasher",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'stock', 'purchase', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock.xml',
        # 'views/invoice.xml',
        'views/sale.xml',
        'views/purchase.xml',
        'report/purchase.xml',
        'report/sale.xml',
    ],
}

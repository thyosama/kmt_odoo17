# -*- coding: utf-8 -*-
{
    'name': "UC Guarantee Letters",
    'summary': """UC Guarantee letters""",
    'description': """ Guarantee letters""",
    'author': "UC",
    'website': "http://www.UC.co",
    'version': '15.0.0.1',
    'category': 'Accounting',
    'depends': ['account'],

    'data': [
        'security/ir.model.access.csv',
        'views/guarantee_letter.xml',
        'views/setting.xml',
        'views/guarantee_increase.xml',
        'views/guarantee_extension.xml',
        'views/guarantee_reduction.xml',
        'views/gurantee_completion.xml',
        'views/guarantee_send.xml',
        'views/guarantee_recieve.xml',
    ],

    'application': True,
    'installable': True,
}
# -*- coding: utf-8 -*-
{
    'name': "Account Access Rights",

    'summary': """Access for show Account""",

    'description': """""",

    'author': "Ali",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '17.0',
    'depends': ['account','base','account_accountant','web'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/access_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'access_right_account/static/src/components/**/*',
        ],
    }
}

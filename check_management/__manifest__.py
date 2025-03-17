# -*- coding: utf-8 -*-
{
    'name': "cheques Management",

    'summary': """
        Checque managment Cycle""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Mohamed AbdElrhman",
    'website': "http://www.yourcompany.com",
    'category': 'account',
    'version': '17.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group_user.xml',
        'data/hr_notify_cron.xml',
        'data/ir_sequence.xml',

        'views/cheque_recieve_view.xml',
        'views/views.xml',
        'views/config.xml',
        'views/payment_actions.xml',
        'views/cheque_send_view.xml',
        'views/cheque_document.xml',
        'views/treasury.xml',
        'views/account_transfer.xml',
        'reports/payment_voucher.xml',
        'reports/receipt_voucher.xml',
        'reports/invoices.xml',

    ],

}

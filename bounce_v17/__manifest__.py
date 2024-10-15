# -*- coding: utf-8 -*-
{
    'name': "Bounce 17",
    'summary': """Bounce V17""",
    'description': """Bounce""",
    'author': "Abdulrhman Mohammed",
    'maintainers': ['mashendi'],
    'website': "http://www.almoasherbiz.com",
    'category': 'HR',
    'version': '17.0',
    'depends': ['base', 'hr','hr_payroll'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/bounce.xml',
        'views/bounce_type.xml',
        'views/contract.xml',
    ],
}

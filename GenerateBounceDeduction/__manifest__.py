{
    'name': "Generate Bounce & Deduction",
    'summary': """ Bounce Deduction """,
    'description': """Generate Bounce Deduction""",
    'author': "Marwa Abouzaid",
    'website': "http://almoasherbiz.com/",
    'category': 'Uncategorized',
    'version': '17.0',
    'depends': ['base','hr','hr_payroll','bounce_v17','deduction_v17'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/generatebounce_view.xml',
        'views/generatededuction_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
{
    'name': "salary_report_xlsx",
    'summary': "Salary Report in Details",
    'category': 'Reporting',
    'version': '17.0',
    'license': 'AGPL-3',
    'external_dependencies': {'python': ['xlsxwriter', 'xlrd']},
    'depends': [
        'hr_payroll',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/report_wizard.xml',
    ],
}

# -*- coding: utf-8 -*-
{
    'name': "Tender",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohamed Abd Elrhman",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '15',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'product', 'stock', 'sale', 'account', 'purchase', 'account_accountant', 'web',
                'master_data_construction'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        # 'views/ab_stock_picking.xml',
        'views/project.xml',
        # 'views/item.xml',
        'views/sale_order.xml',
        # 'views/job_cost.xml',

        'views/actions.xml',
        'views/menus.xml',

        'views/views.xml',
        'views/config.xml',
        'views/project_stock.xml',
        'views/top_sheet.xml',
        'views/indirect_cost.xml',
        'reports/report_tender_financial.xml',
        'reports/report_tender_technical.xml',
        'reports/report_tender_cover.xml',
        'reports/report_estimation.xml',
        'reports/tender_quotation_report.xml',
        'views/template_print.xml',
        'wizard/upload.xml',
        # 'views/product_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

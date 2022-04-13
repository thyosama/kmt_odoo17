# -*- coding: utf-8 -*-
{
    'name': "construction",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Mohamed Abd Elrhman",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'product', 'stock', 'sale', 'account', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ab_account_payment.xml',
        'views/ab_stock_picking.xml',

        'views/project.xml',
        'views/deduction_allowance.xml',
        'views/item.xml',
        'views/wbs_view.xml',
        'views/sale_order.xml',
        'views/job_cost.xml',
        'views/estimate.xml',
        'views/contract.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/contract_user.xml',
        'views/contract.xml',
        'views/views.xml',
        'views/invoice.xml',
        'views/config.xml',
        #
        'wizard/wizard.xml',
        'wizard/wizard_invoice.xml',
        'wizard/time_variance.xml',
        'wizard/cost_comparison.xml',
        'wizard/invoice_payment.xml',
        'wizard/cost_analysis.xml',
        #
        'views/project_stock.xml',
        'views/quantity_survey.xml',
        'views/bank_statement.xml',
        'views/purchase_order.xml',
        # 'views/new_invoice.xml',
        # 'views/move.xml',

        # reports
        'reports/deduction_additional_report.xml',
        'reports/profit_project.xml',
        'reports/cost_analysis_view.xml',
        'reports/construction_reports_menus.xml',
        'reports/print_actions.xml',
        'reports/project_template.xml',
        'reports/sales_order_template.xml',
        'reports/job_cost_template.xml',
        'reports/invoice_template.xml',
        'reports/contract_tem.xml',
        'reports/cost_compersion.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

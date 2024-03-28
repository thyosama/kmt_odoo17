# -*- coding: utf-8 -*-
{
    'name': "tender_contract",

    'summary': """
        this module is get relation between tender and construction 
        when create contract related at project which display only related tender and items
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "MOHAMED ABDELRHMAN",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','new_construction','tender'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

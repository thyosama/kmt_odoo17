{
    "name": "ALM Self Serive Customization",
    "version": "1.0",
    "description": "ALM Self Serive Customization",
    "summary": "ALM Self Serive Customization",
    "author": "Muhammed Shendi",
    "license": "LGPL-3",
    "depends": [
        "portal",
        "self_service_module",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
        "views/timesheet_templates.xml",
        "views/thank_you_template.xml",
        "views/employee_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "alm_self_service/static/src/js/timesheet_portal.js",
            "alm_self_service/static/src/css/style.css",
        ]
    },
}

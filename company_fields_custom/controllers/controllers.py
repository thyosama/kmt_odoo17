# -*- coding: utf-8 -*-
# from odoo import http


# class CompanyFieldsCustom(http.Controller):
#     @http.route('/company_fields_custom/company_fields_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/company_fields_custom/company_fields_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('company_fields_custom.listing', {
#             'root': '/company_fields_custom/company_fields_custom',
#             'objects': http.request.env['company_fields_custom.company_fields_custom'].search([]),
#         })

#     @http.route('/company_fields_custom/company_fields_custom/objects/<model("company_fields_custom.company_fields_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('company_fields_custom.object', {
#             'object': obj
#         })

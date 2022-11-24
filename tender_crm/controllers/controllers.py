# -*- coding: utf-8 -*-
# from odoo import http


# class TenderCrm(http.Controller):
#     @http.route('/tender_crm/tender_crm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tender_crm/tender_crm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tender_crm.listing', {
#             'root': '/tender_crm/tender_crm',
#             'objects': http.request.env['tender_crm.tender_crm'].search([]),
#         })

#     @http.route('/tender_crm/tender_crm/objects/<model("tender_crm.tender_crm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tender_crm.object', {
#             'object': obj
#         })

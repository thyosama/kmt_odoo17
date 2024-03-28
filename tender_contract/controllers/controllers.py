# -*- coding: utf-8 -*-
# from odoo import http


# class TenderContract(http.Controller):
#     @http.route('/tender_contract/tender_contract', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tender_contract/tender_contract/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tender_contract.listing', {
#             'root': '/tender_contract/tender_contract',
#             'objects': http.request.env['tender_contract.tender_contract'].search([]),
#         })

#     @http.route('/tender_contract/tender_contract/objects/<model("tender_contract.tender_contract"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tender_contract.object', {
#             'object': obj
#         })

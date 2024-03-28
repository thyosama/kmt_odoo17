# -*- coding: utf-8 -*-
# from odoo import http


# class MasterDataConstruction(http.Controller):
#     @http.route('/master_data_construction/master_data_construction', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/master_data_construction/master_data_construction/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('master_data_construction.listing', {
#             'root': '/master_data_construction/master_data_construction',
#             'objects': http.request.env['master_data_construction.master_data_construction'].search([]),
#         })

#     @http.route('/master_data_construction/master_data_construction/objects/<model("master_data_construction.master_data_construction"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('master_data_construction.object', {
#             'object': obj
#         })

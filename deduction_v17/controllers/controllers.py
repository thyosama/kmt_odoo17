# -*- coding: utf-8 -*-
from odoo import http

# class DeductionMojuev12(http.Controller):
#     @http.route('/deduction_mojuev12/deduction_mojuev12/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/deduction_mojuev12/deduction_mojuev12/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('deduction_mojuev12.listing', {
#             'root': '/deduction_mojuev12/deduction_mojuev12',
#             'objects': http.request.env['deduction_mojuev12.deduction_mojuev12'].search([]),
#         })

#     @http.route('/deduction_mojuev12/deduction_mojuev12/objects/<model("deduction_mojuev12.deduction_mojuev12"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('deduction_mojuev12.object', {
#             'object': obj
#         })
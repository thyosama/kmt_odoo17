# -*- coding: utf-8 -*-
# from odoo import http


# class GizaMasrCustom(http.Controller):
#     @http.route('/giza_masr_custom/giza_masr_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/giza_masr_custom/giza_masr_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('giza_masr_custom.listing', {
#             'root': '/giza_masr_custom/giza_masr_custom',
#             'objects': http.request.env['giza_masr_custom.giza_masr_custom'].search([]),
#         })

#     @http.route('/giza_masr_custom/giza_masr_custom/objects/<model("giza_masr_custom.giza_masr_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('giza_masr_custom.object', {
#             'object': obj
#         })

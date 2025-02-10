# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPdfQuote(http.Controller):
#     @http.route('/custom_pdf_quote/custom_pdf_quote', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_pdf_quote/custom_pdf_quote/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_pdf_quote.listing', {
#             'root': '/custom_pdf_quote/custom_pdf_quote',
#             'objects': http.request.env['custom_pdf_quote.custom_pdf_quote'].search([]),
#         })

#     @http.route('/custom_pdf_quote/custom_pdf_quote/objects/<model("custom_pdf_quote.custom_pdf_quote"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_pdf_quote.object', {
#             'object': obj
#         })


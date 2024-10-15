# -*- coding: utf-8 -*-
# from odoo import http


# class AttendanceSheetBatch(http.Controller):
#     @http.route('/attendance_sheet_batch/attendance_sheet_batch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/attendance_sheet_batch/attendance_sheet_batch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('attendance_sheet_batch.listing', {
#             'root': '/attendance_sheet_batch/attendance_sheet_batch',
#             'objects': http.request.env['attendance_sheet_batch.attendance_sheet_batch'].search([]),
#         })

#     @http.route('/attendance_sheet_batch/attendance_sheet_batch/objects/<model("attendance_sheet_batch.attendance_sheet_batch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('attendance_sheet_batch.object', {
#             'object': obj
#         })

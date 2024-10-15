from odoo import fields, models, api


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'
    _description = 'Description'

    attendance_rule = fields.Boolean(string='Attendance Rule', default=True)

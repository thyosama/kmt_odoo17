# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2020.
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#    website': https://www.linkedin.com/in/ramadan-khalil-a7088164
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    state = fields.Selection(
        selection=[('fixin', 'Fix In'), ('fixout', 'Fix Out'),
                   ('right', 'Right')],
        default='right')

    def fix_attendance(self):
        self.write({'state': 'right'})

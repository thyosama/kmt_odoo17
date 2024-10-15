from odoo import models, fields, api, _


class HRJob(models.Model):
    _inherit = "hr.job"

    is_confidential = fields.Boolean(string="Confidential?")

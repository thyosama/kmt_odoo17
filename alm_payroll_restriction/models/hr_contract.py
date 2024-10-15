from odoo import models, fields, api, _


class HRContract(models.Model):
    _inherit = "hr.contract"

    is_confidential = fields.Boolean(string="Confidential?", related="job_id.is_confidential", store=True)

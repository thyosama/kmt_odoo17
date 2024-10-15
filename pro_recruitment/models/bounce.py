from odoo import fields, models, api


class Bounce(models.Model):
    _inherit = 'bounce'

    appraisal_id = fields.Many2one('hr.appraisal')
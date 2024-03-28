from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_taxes = fields.Boolean(related='company_id.show_taxes', readonly=False)
    show_cost_per_unit = fields.Boolean(related='company_id.show_cost_per_unit', readonly=False)

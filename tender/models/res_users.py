from odoo import fields, models, api


class Users(models.Model):
    _inherit = 'res.users'
    related_ids = fields.Many2many(
        comodel_name='tender.related.job',
        string='Related_ids')
    @api.onchange("related_ids")
    def _onchange_related_ids(self):
        self.clear_caches()

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_middle_journal_owner = fields.Many2one('account.journal', string="Middle account Recieve ")
    ks_middle_account_sup = fields.Many2one('account.journal', string="Middle account send")



class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_middle_journal_owner = fields.Many2one('account.journal', string="Owner Journal",
                                        related='company_id.ks_middle_journal_owner', readonly=False)
    ks_middle_account_sup = fields.Many2one('account.journal', string="sub contractor",
                                             related='company_id.ks_middle_account_sup', readonly=False)

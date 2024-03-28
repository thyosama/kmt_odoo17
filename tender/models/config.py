from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_middle_journal_owner = fields.Many2one('account.journal', string="Middle account Recieve ")
    ks_middle_account_sup = fields.Many2one('account.journal', string="Middle account send")
    crm= fields.Boolean(string="Crm")

    def write(self,vals):
        res=super(Company, self).write(vals)
        if 'crm' in vals:
            if vals['crm'] ==True:
                xml_records = self.env['ir.model.data']._xmlid_to_res_id('base.module_tender_crm')

                if xml_records:
                    res_id = xml_records
                    app_id  =  self.env['ir.module.module'].search([('id','=',res_id)])
                    app_id.button_immediate_install()
        return res




class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    crm = fields.Boolean(string="Crm",related='company_id.crm', readonly=False)
    ks_middle_journal_owner = fields.Many2one('account.journal', string="Owner Journal",
                                        related='company_id.ks_middle_journal_owner', readonly=False)
    ks_middle_account_sup = fields.Many2one('account.journal', string="sub contractor",
                                             related='company_id.ks_middle_account_sup', readonly=False)

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    show_contract = fields.Boolean("Show Contract", compute="_compute_show_contract")

    def _compute_show_contract(self):
        for record in self:
            record.show_contract = True
            if (
                record.job_id
                and record.job_id.is_confidential
                and not self.user_has_groups(
                    "alm_payroll_restriction.group_payroll_confidential_position"
                )
            ):
                record.show_contract = False

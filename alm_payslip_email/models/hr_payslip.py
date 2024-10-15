from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_send_payslip_by_email(self):
        template_id = self.env.ref("alm_payslip_email.email_template_payslip").id
        template = self.env["mail.template"].browse(template_id)

        ctx = {
            "default_model": "hr.payslip",
            "default_res_ids": self.ids,
            "default_template_id": template.id,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "default_email_layout_xmlid": "mail.mail_notification_light",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

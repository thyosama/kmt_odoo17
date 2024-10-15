import base64
from odoo import api, fields, models
from odoo.modules.module import get_module_resource


class HrEmployeeSkill(models.Model):
    _inherit = "hr.employee.skill"
    skill_desc = fields.Text(related="skill_id.description")
    skill_level_id = fields.Many2one("hr.skill.level", required=False)

    @api.constrains("skill_type_id", "skill_level_id")
    def _check_skill_level(self):
        for record in self:
            pass


class HrSkill(models.Model):
    _inherit = "hr.skill"

    description = fields.Text("Description")

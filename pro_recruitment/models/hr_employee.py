import base64
from odoo import api, fields, models, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError, UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    skill_rate_ids = fields.One2many(
        comodel_name="hr.skill.rate",
        inverse_name="employee_id",
        related="emp_job_title_id.skill_rate_ids",
    )
    job_description = fields.Html(
        string=" Job Description",
        related="emp_job_title_id.job_description",
        store=True,
    )
    job_specification = fields.Html(
        string=" Job Specification",
        related="emp_job_title_id.job_specification",
        store=True,
    )
    max_bounce_percentage = fields.Float(string="Max Bonus")
    max_bonuce = fields.Float(string="Max Bonus")
    minimum2deserve = fields.Float(string="minimum score ")
    disability = fields.Boolean("Disability")
    disability_type = fields.Char("Disability Type")
    is_social_insurance = fields.Boolean("Social Insurance")
    have_income_taxes = fields.Boolean("have income taxes")
    social_insurance = fields.Float(string="Social Insurance Amount")
    is_private_insurance = fields.Boolean("Medical Insurance")
    private_insurance = fields.Float(string="Medical Insurance")
    is_tax_card = fields.Boolean(string="Tax Card")
    tax_card = fields.Char(string="Tax Card")
    extension_code = fields.Char(string="Extension Code")
    is_tax_info = fields.Boolean(string="Tax Exemption")
    tax_info = fields.Char(string="Tax Exemption")
    tax_card_expire = fields.Date(string="Tax Card Expiration Date")
    emp_job_title_id = fields.Many2one("emp.job.title", string="Job Title")
    target_ids = fields.Many2many(
        "target.goal", string="EMP Target", compute="get_target_ids"
    )
    target_line_ids = fields.One2many(
        comodel_name="target.goal.line",
        inverse_name="employee_id",
        compute="get_target_ids",
    )
    target_count = fields.Integer(compute="get_target_ids")
    objective_ids = fields.One2many(
        comodel_name="hr.department.obj",
        inverse_name="employee_id",
        related="department_id.objective_ids",
    )
    goal = fields.Text("Firm Goal", related="department_id.goal")

    @api.depends("name")
    def get_target_ids(self):
        for rec in self:
            target_list = []
            target_ids = self.env["target.goal"].search(
                [("employee_ids", "in", rec.id)]
            )
            rec.target_count = len(target_ids.ids)
            rec.target_ids = [(6, 0, target_ids.ids)]
            for target in target_ids:
                for line in target.line_ids:
                    target_list.append(line.id)
            rec.target_line_ids = [(6, 0, target_list)]

    def action_view_targets(self):
        action = self.env.ref("pro_recruitment.target_goal_action").read()[0]
        action["domain"] = [("id", "in", self.target_ids.ids)]
        return action

    def get_all_emp_job_title(self):
        for rec in self:
            rec.change_emp_job_title_id()

    @api.onchange("emp_job_title_id")
    def change_emp_job_title_id(self):
        for rec in self.env["hr.employee"].search([]):
            rec.job_title = rec.emp_job_title_id.name
            rec.job_description = rec.emp_job_title_id.job_specification
            rec.job_specification = rec.emp_job_title_id.job_specification
            rec.max_bonuce = rec.emp_job_title_id.max_bonuce
            # rec.max_bounce_percentage = rec.emp_job_title_id.max_bonuce
            rec.skill_rate_ids = [(6, 0, rec.emp_job_title_id.skill_rate_ids.ids)]

    @api.constrains("minimum2deserve")
    def constrains_minimum2deserve(self):
        if 0 > self.minimum2deserve or 100 < self.minimum2deserve:
            raise ValidationError(
                _(
                    "Minimum score to Deserve Bonus Must be less than 100 and greater than 0 "
                )
            )
        # if self.minimum2deserve > self.max_bounce_percentage:
        #     raise ValidationError(_("Minimum score to Deserve Bounce Must be less than Max Bounce"))

    @api.constrains("max_bonuce")
    def constrains_max_bonuce(self):
        if 0 > self.max_bonuce or 100 < self.max_bonuce:
            raise ValidationError(
                _("Max Bonus Must be less than 100 and greater than 0 ")
            )


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    job_description = fields.Html(string="Job Description")
    job_specification = fields.Html(string="Job Specification")
    max_bounce_percentage = fields.Float(string="Max Bonus")
    max_bonuce = fields.Float(string="Max Bonus")
    minimum2deserve = fields.Float(string="Minimum score to Deserve Bonus")
    disability = fields.Boolean("Disability")
    disability_type = fields.Char("Disability Type")
    is_social_insurance = fields.Boolean("Social Insurance")
    have_income_taxes = fields.Boolean("have income taxes")
    social_insurance = fields.Float(string="Social Insurance Amount")
    is_private_insurance = fields.Boolean("Medical Insurance")
    private_insurance = fields.Float(string="Medical Insurance")
    is_tax_card = fields.Boolean(string="Tax Card")
    tax_card = fields.Char(string="Tax Card")
    is_tax_info = fields.Boolean(string="Tax Exemption")
    tax_info = fields.Char(string="Tax Exemption")
    tax_card_expire = fields.Date(string="Tax Card Expiration Date")
    extension_code = fields.Char(string="Extension Code")
    emp_job_title_id = fields.Many2one("emp.job.title", string="Job Title")


class HREmployeeSkill(models.Model):
    _name = "hr.skill.rate"

    skill_score = fields.Selection(
        string="Score",
        required=True,
        selection=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")],
    )
    skill_id = fields.Many2one("hr.skill", required=True)
    employee_id = fields.Many2one(
        "hr.employee",
    )
    emp_job_title_id = fields.Many2one(
        "emp.job.title",
    )

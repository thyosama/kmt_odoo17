from odoo import fields, models, api


class TargetGoal(models.Model):
    _name = "target.goal"
    name = fields.Char("Name")
    note = fields.Text("Note")
    employee_ids = fields.Many2many('hr.employee')
    line_ids = fields.One2many(comodel_name='target.goal.line', inverse_name='target_id')
    # target_weight = fields.Selection(string='Target Weight',  selection=[
    #     ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    target_weight_float = fields.Float(string='Target Weight')


class TargetGoalLine(models.Model):
    _name = "target.goal.line"
    target_id = fields.Many2one(comodel_name='target.goal', string='Target')
    skill_id = fields.Many2one(comodel_name='hr.skill', string='Skill', required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    name = fields.Char("Name")
    note = fields.Text("Note")
    description = fields.Text("description")
    level_progress = fields.Integer(string="Progress", related='level')
    level = fields.Integer(string="Progress", help="Progress from zero knowledge (0%) to fully mastered (100%).")
    skill_score = fields.Selection( string='Skill Score', selection=[('1', '1'),('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])

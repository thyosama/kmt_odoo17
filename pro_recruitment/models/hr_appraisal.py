from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import *
import datetime
import dateutil

SCORE = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ]

class HrEmployeeSkills(models.Model):
    _inherit = "hr.employee.skill"

    # @api.constrains('skill_type_id', 'skill_level_id')
    # def _check_skill_level(self):
    #     for record in self:
    #         pass
    #         if record.skill_level_id not in record.skill_type_id.skill_level_ids:
    #             raise ValidationError(_("The skill level %(level)s is not valid for sssssskill type: %(type)s", level=record.skill_level_id.name, type=record.skill_type_id.name))


class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"
    score = fields.Float(compute='compute_performance_over_all', string="competencies achievement")
    competencies_ratio = fields.Float(compute='compute_competencies_ratio',store=1, string="competencies Ratio")
    final_score = fields.Float(compute='compute_competencies_ratio',store=1, string="Final Score")
    total_reserved_value = fields.Float(compute='compute_competencies_ratio', store=1, string="Total Deserved Value")
    performance_over_all = fields.Many2one('performance.level', string='Performance Level', compute='compute_performance_over_all',)
    # performance_over_all = fields.Selection(string='Performance Level', selection=[
    #     ('0', 'Not Applicable'),
    #     ('1', '50% - 64%'),
    #     ('2', '65% - 74%'),
    #     ('3', '75% - 84%'),
    #     ('4', '85% - 95%'),
    # ], compute='compute_performance_over_all', store=True)
    job_description = fields.Html(related="employee_id.job_description", string=' Job Description')
    job_specification = fields.Html(related="employee_id.job_specification", string=' Job Specification')
    bounce_id = fields.Many2one('bounce',string='Bonus')
    goals_weight = fields.Float(string="Goals Weight", compute="get_goals_weight")
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    date_str = fields.Char('Period', compute="get_period_str")
    month_count = fields.Integer(string="Months", compute="get_period_str")

    @api.depends('employee_id', 'skill_ids')
    def compute_competencies_ratio(self):
        for rec in self:
            rec.competencies_ratio = rec.employee_id.emp_job_title_id.competencies_ratio
            rec.final_score = (rec.employee_id.emp_job_title_id.competencies_ratio)* rec.score /100
            appraisal_goal_id = self.env['hr.appraisal.goal'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('deadline', '>=', rec.date_from),
                ('deadline', '<=', rec.date_to),
            ], order="id desc", limit=1)
            rec.total_reserved_value = (rec.final_score + appraisal_goal_id.final_score) if appraisal_goal_id else 0



    def _copy_skills_when_confirmed(self):
        for appraisal in self:
            employee_skills = appraisal.employee_id.skill_rate_ids
            for skill in employee_skills:
                skill_level_id = self.env['hr.skill.level'].search([
                    ('name', '=', int(skill.skill_score)),
                    ('skill_type_id', '=', skill.skill_id.skill_type_id.id),
                ], limit=1)
                # in case the employee confirms its appraisal
                self.env['hr.appraisal.skill'].sudo().create({
                    'appraisal_id': appraisal.id,
                    'skill_id': skill.skill_id.id,
                    'skill_score': skill.skill_score,
                    'skill_level_id': skill_level_id.id,
                    # 'skill_level_id': skill.skill_level_id.id,
                    # 'skill_type_id': skill.skill_type_id.id,
                    # 'employee_skill_id': skill.id,
                })


    @api.depends('date_from', 'date_to')
    def get_period_str(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                time = dateutil.relativedelta.relativedelta(rec.date_to, rec.date_from)
                rec.date_str = str(time.years) + " years " + str(time.months) + ' Month ' + str(time.days) + " Days "
                rec.month_count = time.months
            else:
                rec.date_str = ""
                rec.month_count = 0

    @api.depends('employee_id')
    def get_goals_weight(self):
        for rec in self:
            appraisal_goal_ids = self.env['hr.appraisal.goal'].search([('employee_id', '=', rec.employee_id.id)])
            rec.goals_weight = sum(line.goal_weight for line in appraisal_goal_ids)
            # / len(appraisal_goal_ids.ids) if len(appraisal_goal_ids.ids) > 0 else 0

    def action_done(self):
        res = super(HrAppraisal, self).action_done()
        bounce_type_id = self.env['bounce.type'].search([('code', '=', 'Appraisals')])
        if not bounce_type_id:
            raise ValidationError(_("Please Create Bounce Type with code [Appraisals]"))
        if self.employee_id.max_bonuce > 0 and self.score >= self.employee_id.minimum2deserve:
            bounce_id = self.env['bounce'].create({
                'appraisal_id': self.id,
                'employee_id': self.employee_id.id,
                'contract_id': self.employee_id.contract_id.id,
                'type': 'fixed',
                'bounce_value': self.month_count * (self.employee_id.contract_id.wage + self.employee_id.contract_id.x_variable_salary) * \
                                (((self.employee_id.max_bonuce /100) * self.total_reserved_value) / 100),
                'value': self.month_count * (self.employee_id.contract_id.wage + self.employee_id.contract_id.x_variable_salary) * \
                                (((self.employee_id.max_bonuce /100) * self.total_reserved_value) / 100),
                'type_id': bounce_type_id.id,
            })

            self.bounce_id = bounce_id.id
        return res

    def unlink(self):
        self.bounce_id.unlink()
        return super(HrAppraisal, self).unlink()

    # todo :remove performance_level
    performance_level = fields.Selection(string='Performance Level', selection=[
        ('0', 'Not Applicable'),
        ('1', '50% - 64%'),
        ('2', '65% - 74%'),
        ('3', '75% - 84%'),
        ('4', '85% - 95%'),
    ], compute='compute_performance_over_all', store=True)

    @api.depends('skill_ids')
    def compute_performance_over_all(self):
        for rec in self:
            rec.performance_over_all = '0'
            rec.score = 0
            total = 0
            if len(rec.skill_ids.ids) > 0:
                for line in rec.skill_ids:
                    total += int(line.score)
                sc = total / (len(rec.skill_ids.ids) * 10) * 100
                rec.score = sc
                performance_id = self.env['performance.level'].search([('form_per', '<=', sc), ('to_per', '>=', sc)], limit=1)
                rec.performance_over_all = performance_id.id if performance_id else False
    #
    # @api.depends('skill_ids')
    # def compute_performance_over_all(self):
    #     for rec in self:
    #         rec.performance_over_all = '0'
    #         rec.score = 0
    #         total = 0
    #         if len(rec.skill_ids.ids) > 0:
    #             for line in rec.skill_ids:
    #                 total += int(line.score)
    #             if 50 <= (total / (len(rec.skill_ids.ids)) * 10) <= 64:
    #                 rec.performance_over_all = '1'
    #             elif 65 <= (total / (len(rec.skill_ids.ids)) * 10) <= 74:
    #                 rec.performance_over_all = '2'
    #             elif 75 <= (total / (len(rec.skill_ids.ids)) * 10) <= 84:
    #                 rec.performance_over_all = '3'
    #             elif 85 <= (total / (len(rec.skill_ids.ids)) * 10) <= 95:
    #                 rec.performance_over_all = '4'
    #             rec.score = (total / (len(rec.skill_ids.ids)) * 10)

    @api.constrains('skill_ids')
    def constrains_skill_ids(self):
        for rec in self:
            self.assessment_note = False
            if rec.score:
                evaluation_id = self.env['hr.appraisal.note'].search([
                    ('score_from', '<=', float(rec.score) / 10),
                    ('score_to', '>=', float(rec.score) / 10),
                ], limit=1)
                self.assessment_note = evaluation_id.id


class HrAppraisalSkill(models.Model):
    _inherit = "hr.appraisal.skill"

    appraisal_note_id = fields.Many2one('hr.appraisal.note', string="Evaluation Skills",
                                        compute='compute_evaluation_skill')

    skill_level_id = fields.Many2one('hr.skill.level', required=False)
    score = fields.Selection(string='Employee Score', selection=SCORE)
    skill_score = fields.Selection(string='Competence Level', selection=SCORE, store=1)
    description = fields.Text(related="skill_id.description")
    @api.onchange('skill_score')
    def _onchange_score(self):
        for rec in self:
            skill_level_id = self.env['hr.skill.level'].search([
                ('name', '=',  int(rec.skill_score)*10),
                ('skill_type_id', '=',  rec.skill_id.skill_type_id.id),
            ], limit=1)
            rec.skill_level_id = skill_level_id

    @api.depends('score')
    def compute_evaluation_skill(self):
        for rec in self:
            evaluation_id = self.env['hr.appraisal.note'].search([
                ('score_from', '<=', int(rec.score)),
                ('score_to', '>=', int(rec.score)),
            ], limit=1)
            rec.appraisal_note_id = evaluation_id.id if evaluation_id else False


class HrAppraisalNote(models.Model):
    _inherit = "hr.appraisal.note"

    score_from = fields.Integer(string='from')
    score_to = fields.Integer(string='to')

    @api.constrains('score_from', 'score_to')
    def constrains_score(self):
        for rec in self:
            if rec.score_to <= rec.score_from:
                raise ValidationError(_("Score To Must Bigger than Score From."))


class EmployeeMinimumSkills(models.Model):
    _name = "emp.min.skill"
    appraisal_id = fields.Many2one(comodel_name='hr.appraisal.goal', string='Appraisal')
    skill_id = fields.Many2one(comodel_name='hr.skill', string='Skill', store=1)
    target_goal_id = fields.Many2one(comodel_name='target.goal', string='Skill', store=1)
    target_line_id = fields.Many2one(comodel_name='target.goal.line', string='Target')
    name = fields.Char("Name")
    description = fields.Text("Description")
    note = fields.Text("Note")
    level_progress = fields.Integer(string="Progress", related='level')
    target_level = fields.Integer(string="Target Level", related='target_line_id.level')
    level = fields.Integer(string="Progress", help="Progress from zero knowledge (0%) to fully mastered (100%).")
    # not_skilled = fields.Boolean(string='Not Skilled EMP', compute="get_emp_skill")
    skill_type = fields.Selection(string='Skill Type', selection=[
        ('skill', 'skill'), ('not_skill', 'Not skill'), ('not', 'Not found')
    ], compute="get_emp_skill", store=1)
    # skill_score = fields.Selection(string='Skill Score',  selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    skill_score_float = fields.Float(string='Skill Score')
    # target_weight = fields.Selection(string='Skill Score',  selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    target_weight_float = fields.Float(string='Skill Score')
    skill_score_weight = fields.Float(compute="compute_weight_widget", string="Target Weight")
    target_score_weight = fields.Float(compute="compute_weight_widget", string="Target  Score")



    @api.depends('skill_score_float', 'target_weight_float')
    def compute_weight_widget(self):
        for rec in self:
            if (rec.skill_score_float >-1 and rec.target_weight_float<=100) and (rec.target_weight_float >-1 and rec.target_weight_float<=100):
                rec.skill_score_weight = rec.skill_score_float
                rec.target_score_weight = rec.target_weight_float
            else:
                raise ValidationError("Target Score and Target weight must be from 0 and 100 ")

    # target_skill_score = fields.Selection(string='Target Score', related='target_line_id.skill_score_float')

    @api.depends('skill_score_float', 'skill_id')
    def get_emp_skill(self):
        for line in self:
            if line.skill_score_float < line.target_line_id.skill_score:
                line.skill_type = 'not_skill'
            else:
                line.skill_type = 'skill'


class HrAppraisalGoal(models.Model):
    _inherit = "hr.appraisal.goal"

    target_goal_ids = fields.Many2many(comodel_name='target.goal', string='Objective To Do', domain="[('employee_ids','in',employee_id)]")
    # emp_min_skills_ids = fields.Many2many( comodel_name='emp.min.skill', string='EMP Minimum Skills')
    emp_min_skills_ids = fields.One2many(comodel_name='emp.min.skill', inverse_name='appraisal_id',
                                         string='EMP Minimum Skills')
    not_skilled = fields.Boolean(string='Not Skilled EMP', compute="get_emp_skill")
    goal_progress = fields.Float('Progress')
    goal_weight = fields.Float('Weight', compute="get_goal_weight")
    target_ratio = fields.Float("Target Ratio", store=1)
    target_achieve = fields.Float("Target Achievement", compute="compute_target_achieve")
    final_score = fields.Float("Final Score", compute="compute_final_score")

    @api.depends('emp_min_skills_ids')
    def get_goal_weight(self):
        for rec in self:
            rec.goal_weight = (sum(line.target_weight_float for line in rec.emp_min_skills_ids)/(len(rec.emp_min_skills_ids.ids)*10) *100) if rec.emp_min_skills_ids else 0
    @api.depends('target_achieve', 'target_ratio')
    def compute_final_score(self):
        for rec in self:
            rec.final_score = rec.target_achieve * rec.target_ratio / 100
            # if rec.target_ratio>0:
            #     rec.final_score = (rec.target_achieve rec.target_ratio )* 100
            # else:
            #     rec.final_score=0

    @api.depends('emp_min_skills_ids')
    def compute_target_achieve(self):
        for rec in self:
            total = 0
            for line in rec.emp_min_skills_ids:
                if line.target_weight_float>0:
                    total += (line.skill_score_float/line.target_weight_float)*100
            rec.target_achieve = (total / (len(rec.emp_min_skills_ids.ids)*100) )*100 if len(rec.emp_min_skills_ids.ids) > 0 else 0

    @api.onchange('employee_id')
    def _onchange_target_goal_ids(self):
        if self.employee_id:
            self.target_ratio = self.employee_id.emp_job_title_id.target_ratio
        else:
            self.target_ratio = 0

    @api.depends('emp_min_skills_ids')
    def get_emp_skill(self):
        for rec in self:
            rec.not_skilled = True
            if len(rec.emp_min_skills_ids.ids) == len(
                    rec.emp_min_skills_ids.filtered(lambda m: m.skill_type == 'skill').ids):
                rec.not_skilled = False

    @api.onchange('employee_id', 'target_goal_ids')
    def change_emp_target(self):
        for rec in self:
            target = []
            emp_min_skill_ids = []
            for targets in rec.target_goal_ids:
                target.append(targets._origin.id)
                # for l in targets.line_ids:
                #     target.append(l._origin.id)
            for targ in target:
                line = self.env['emp.min.skill'].create({
                    'appraisal_id': rec.id,
                    # 'target_line_id': targ,
                    'target_goal_id': self.env['target.goal'].browse(targ).id,
                    'target_weight_float': self.env['target.goal'].browse(targ).target_weight_float,
                    # 'skill_id': self.env['target.goal.line'].browse(targ).skill_id.id,
                })
                emp_min_skill_ids.append(line.id)
            rec.emp_min_skills_ids = [(6, 0, emp_min_skill_ids)]
            for emp_skill in rec.employee_id.skill_rate_ids:
                if rec.emp_min_skills_ids.filtered(lambda m: m.skill_id == emp_skill.skill_id):
                    rec.emp_min_skills_ids.filtered(lambda m: m.skill_id == emp_skill.skill_id).skill_score = emp_skill.skill_score


class PerformanceLevel(models.Model):
    _name = "performance.level"

    name = fields.Char('Name', required=True)
    form_per = fields.Float("From", required=True)
    to_per = fields.Float("From", required=True)

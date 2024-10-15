from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class TechCriteria(models.Model):
    _name = 'tech.criteria'
    _description = 'name'

    name = fields.Many2one('hr.job',string='Job Position',required=True)
    question_and_page_ids = fields.One2many(comodel_name='survey.question', inverse_name='tech_criteria_id')
    questions_selection = fields.Selection([
        ('all', 'All questions'),
        ('random', 'Randomized per section')],
        string="Selection", required=True, default='all',
        help="If randomized is selected, you can configure the number of random questions by section. This mode is ignored in live session.")


class SurveyQuse(models.Model):
    _inherit = 'survey.question'

    tech_criteria_id = fields.Many2one('tech.criteria')
    hr_applicant_id = fields.Many2one('hr.applicant')


class TechnicalEvaluation(models.Model):
    _name = 'technical.evaluation'

    name = fields.Char('Evaluation')
    from_score = fields.Float('From')
    to_score = fields.Float('To')

    @api.constrains('from_score','to_score')
    def constrains_range(self):
        from_rec = self.env['technical.evaluation'].search(['|','|','|',('from_score','=',self.from_score),('from_score', '=', self.to_score),('to_score', '=', self.to_score),('to_score', '=', self.from_score)])
        print('from_rec',from_rec)
        if len(from_rec)>1 :
            raise ValidationError('Please check for Duplicate Evaluation range')


class SurveyQuse(models.Model):
    _name = 'technical.question.ans'

    tech_criteria_id = fields.Many2one('tech.criteria')
    hr_applicant_id = fields.Many2one('hr.applicant')
    applicant_answer_choice = fields.Many2one('survey.question.answer',domain="[('question_id', '=', question)]",string='Choice Answer')
    applicant_answer_text_score = fields.Char('Text/Numerical Answer')
    applicant_answer_date = fields.Date('Date Answer')
    question = fields.Many2one('survey.question')
    question_type = fields.Selection(related='question.question_type')
    score = fields.Float('Score')
    # to solve error only
    applicant_answer_choice_2 = fields.Many2one('survey.question.answer', domain="[('question_id', '=', question)]")
    title = fields.Char('Score')
    is_page = fields.Char('Score')
    questions_selection = fields.Char('Score')

    @api.onchange('applicant_answer_choice','applicant_answer_text_score','applicant_answer_date')
    def get_score(self):
        if self.question_type == 'simple_choice':
            self.score = self.applicant_answer_choice.answer_score

        elif self.question_type in ['numerical_box']:
            if float(self.applicant_answer_text_score) == self.question.answer_numerical_box:
                print('-------------------------')
                self.score = self.question.answer_score
            else:
                self.score=0
        elif self.question_type in ['date']:
            if self.applicant_answer_date == self.question.answer_date:
                self.score = self.question.answer_score
            else:
                self.score = 0


class Stages(models.Model):
    _inherit = 'hr.recruitment.stage'

    tech_criteria = fields.Boolean('Technical Criteria')


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    question_and_page_ids =  fields.One2many(comodel_name='technical.question.ans', inverse_name='hr_applicant_id')
    technical_evaluation =  fields.Many2one('technical.evaluation',string="Tech. Evaluation", compute='get_evaluation', store='True')
    tech_criteria = fields.Boolean('Technical Criteria', related='stage_id.tech_criteria')
    total_technical_score = fields.Float("Total Score")

    @api.onchange('job_id')
    def get_question_interview(self):
        if self.stage_id and self.job_id:
            if self.stage_id.tech_criteria:
                tech= self.env['tech.criteria'].search([('name','=',self.job_id.id)],limit=1)
                # ques=[]
                # for t in tech:
                #     ques+=t.question_and_page_ids.mapped('id')
                #     print('----',ques,t.question_and_page_ids)
                # self.question_and_page_ids = [(6, 0, ques)]
                # for s in self.question_and_page_ids:
                #     s.set_question_domain()
                ques=[]
                for q in tech.question_and_page_ids:
                        nq = self.env['technical.question.ans'].create({
                            'question':q.id,
                            'tech_criteria_id':q.tech_criteria_id.id,
                            'hr_applicant_id':self.id,
                        })
                        ques.append(nq.id)

                self.question_and_page_ids = [(6, 0, ques)]

    @api.onchange('question_and_page_ids')
    def get_total_technical_score(self):
        if self.question_and_page_ids:
            ques_degree= 100/len(self.question_and_page_ids)
            total=0
            for i in self.question_and_page_ids:
                if i.score !=0 and i.question_type in ['numerical_box','date','simple_choice']:
                   total+=ques_degree
                elif i.score !=0 and i.question_type =='text_box':
                    if i.score >100 or i.score <0:
                        raise ValidationError('The Score of Text question from 0 to 100, Please Recheck the Score')
                    else:
                        total+=(i.score * ques_degree)/100
            self.total_technical_score =total
            self.get_evaluation()


    def get_evaluation(self):
        for i in self:
            print('kkkk', i.total_technical_score)
            technical_evaluation = self.env['technical.evaluation'].search([('from_score','<=',i.total_technical_score),('to_score','>=',i.total_technical_score)])
            print('kkkk',technical_evaluation.name)
            if technical_evaluation:
                print('kkkk', technical_evaluation.name)
                i.technical_evaluation = technical_evaluation
            else:
                i.technical_evaluation = False



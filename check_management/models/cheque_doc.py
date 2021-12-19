from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError




class AccountCheque(models.Model):
    _name = 'account.cheque'

    _order ='name asc'

    name = fields.Char()

    document_id = fields.Many2one(comodel_name="cheque.document", string="", required=False, )
    is_select_ed = fields.Boolean()


class ChequesDocs(models.Model):
    _name = "cheque.document"
    _rec_name='bank_name'

    name = fields.Integer(string="Document Number", required=False, )
    num_cheque = fields.Integer(string="Number of Cheques", required=True, )
    journal_id  = fields.Many2one('account.journal',string='Journal',domain=[('type','=','bank')])
    num_first_cheque = fields.Char(string="First Number of Check", required=True, )
    bank_name = fields.Many2one('res.bank',string="Bank Name", required=True, )
    cheques_ids = fields.One2many(comodel_name="account.cheque", inverse_name="document_id")
    is_created = fields.Boolean(string="",)
    active = fields.Boolean(default=True)
    gap  = fields.Boolean("Gap")
    account_id= fields.Many2one(
        comodel_name='account.account',
        string='Account Number',  domain="[('user_type_id.type','=','liquidity')]",
        required=False)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)



    @api.constrains('name')
    def unique_name(self):
        res = self.env['cheque.document'].search([("name", "=", self.name)])
        if len(res) > 1:
            raise ValidationError("This Document Number is Already Exists .")


    # 
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active

    # 
    def generate_cheques(self):
        if not self.num_cheque:
            raise ValidationError('Please Enter Number of Cheques')
        if not self.num_first_cheque:
            raise ValidationError('Please Enter Number of First Cheque')
        if self.num_cheque and self.num_first_cheque:
            cheques_lst = []
            for x in range(int(self.num_first_cheque), (int(self.num_first_cheque) + self.num_cheque )):

                cheques_lst.append({'name': x})
                self.cheques_ids = [(0,0,{'name': x})]
            self.is_created = True
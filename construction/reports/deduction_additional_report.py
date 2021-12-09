from odoo import models, fields, api
from odoo import tools

class x(models.Model):
    _name = 'deduction.aditional.report'

class Deduction_report(models.Model):
    _name = 'deduction.aditional.report.owner'
    _description = 'Deduction Additional  Report'
    _auto = False
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'sub contractor')], string="Type")
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    contract_type_id = fields.Many2one("contract.deduction.allowance", string="Name")

    value = fields.Float('deduction / additional value')
    account_id = fields.Many2one('account.account',string="deduction / additional Account")
    value_contract = fields.Float('deduction / additional contract value')
    project_id  = fields.Many2one("project.project",string="Project")
    contract_id = fields.Many2one("construction.contract", string="Contract")
    partner_id = fields.Many2one("res.partner",string="Customer")
    contract_date = fields.Date(related='contract_id.date',string="Contract Date",store=True,index=True)
    remaining_value = fields.Float(compute='get_remaining_value',string="Remaining value")
    # invoice_id = fields.Many2one('account.invoice')
    def get_invoice(self):
        item_id, ids = [], []
        if self.sub_type == 'owner':
            item_id = self.env['contract.deduction.lines.invoice'].search([('contract_id', '=', self.contract_id.id)])
            for rec in item_id:
                ids.append(rec.id)
        elif self.sub_type == 'supconstractor':
            item_id = self.env['contract.addition.lines.invoice'].search([('contract_id', '=', self.contract_id.id)])
            for rec in item_id:
                ids.append(rec.invoice_id.id)
        view_form = self.env.ref('construction.view_contract_dudection_report_invoice')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree',
            'views': [(view_form.id, 'tree')],
            'res_model': 'account.invoice',
            'domain': [('id', 'in', ids)],
            'target': 'current',

        }
    @api.depends('value','value_contract')
    def get_remaining_value(self):
        for rec in self:
            rec.remaining_value = rec.value_contract-rec.value
    def _query(self):

        query =""" 
        select min(inv.id) as id,
        inv.contract_id as contract_id,inv.project_id as project_id, inv.name as contract_type_id,
        inv.partner_id as partner_id,sum(inv.current_value) as value,inv.contract_date as contract_date,
        max(inv.value_contract) as value_contract,inv.account_id as account_id,min(inv.type) as type,min(inv.sub_type )as sub_type
        from contract_deduction_lines_invoice as inv 
        where inv.sub_type='owner' 
        group by inv.name,inv.contract_id ,inv.project_id,inv.partner_id,inv.account_id,inv.contract_date
        
        UNION
        select min(inv.id) as id,
        inv.contract_id as contract_id,inv.project_id as project_id, inv.name as contract_type_id,
        inv.partner_id as partner_id,sum(inv.current_value) as value,inv.contract_date as contract_date,
        max(inv.value_contract) as value_contract,inv.account_id as account_id,min(inv.type) as type,min(inv.sub_type )as sub_type
        from contract_addition_lines_invoice as inv 
        where inv.sub_type='owner' 
        group by inv.name,inv.contract_id ,inv.project_id,inv.partner_id,inv.account_id,inv.contract_date
                
        """

        return query

    def init(self):
        # self._table = sale_report

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
class Deduction_reportsup(models.Model):
    _name = 'deduction.aditional.report.supconstractor'
    _description = 'Deduction Additional  Report'
    _auto = False
    sub_type = fields.Selection([('owner', 'Owner'), ('supconstractor', 'supconstractor')], string="Type")
    type = fields.Selection([('deduction', 'Deduction'), ('addition', 'Additional')], string="Type")
    contract_type_id = fields.Many2one("contract.deduction.allowance", string="Name")

    value = fields.Float('deduction / additional value')
    account_id = fields.Many2one('account.account',string="deduction / additional Account")
    value_contract = fields.Float('deduction / additional contract value')
    project_id  = fields.Many2one("project.project",string="Project")
    contract_id = fields.Many2one("construction.contract", string="Contract")
    partner_id = fields.Many2one("res.partner",string="Customer")
    contract_date = fields.Date(related='contract_id.date',string="Contract Date",store=True,index=True)
    remaining_value = fields.Float(compute='get_remaining_value',string="Remaining value")
    # invoice_id = fields.Many2one('account.invoice')
    def get_invoice(self):
        item_id,ids=[],[]
        if self.sub_type=='owner':
            item_id = self.env['contract.deduction.lines.invoice'].search([('contract_id','=',self.contract_id.id)])
            for rec in item_id:
                ids.append(rec.id)
        elif self.sub_type=='supconstractor':
            item_id = self.env['contract.addition.lines.invoice'].search([('contract_id','=',self.contract_id.id)])
            for rec in item_id:
                ids.append(rec.invoice_id.id)
        view_form = self.env.ref('construction.view_contract_dudection_report_invoice')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree',
            'views': [(view_form.id, 'tree')],
            'res_model': 'account.invoice',
            'domain': [('id', 'in', ids)],
            'target': 'current',

        }
    @api.depends('value','value_contract')
    def get_remaining_value(self):
        for rec in self:
            rec.remaining_value = rec.value_contract-rec.value
    def _query(self):

        query =""" 
        select min(inv.id) as id,
        inv.contract_id as contract_id,inv.project_id as project_id, inv.name as contract_type_id,
        inv.partner_id as partner_id,sum(inv.current_value) as value,inv.contract_date as contract_date,
        max(inv.value_contract) as value_contract,inv.account_id as account_id,min(inv.type) as type,min(inv.sub_type )as sub_type
        from contract_deduction_lines_invoice as inv 
        where inv.sub_type='supconstractor' 
        group by inv.name,inv.contract_id ,inv.project_id,inv.partner_id,inv.account_id,inv.contract_date
        
        UNION
        select min(inv.id) as id,
        inv.contract_id as contract_id,inv.project_id as project_id, inv.name as contract_type_id,
        inv.partner_id as partner_id,sum(inv.current_value) as value,inv.contract_date as contract_date,
        max(inv.value_contract) as value_contract,inv.account_id as account_id,min(inv.type) as type,min(inv.sub_type )as sub_type
        from contract_addition_lines_invoice as inv 
        where inv.sub_type='supconstractor' 
        group by inv.name,inv.contract_id ,inv.project_id,inv.partner_id,inv.account_id,inv.contract_date
                
        """

        return query

    def init(self):
        # self._table = sale_report

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))


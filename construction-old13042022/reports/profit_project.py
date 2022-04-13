from odoo import tools
from odoo import api, fields, models


class project_profit(models.Model):
    _name = 'project.profit.report'
    _description = "Project Profit  Report"
    _auto = False


    contract_id = fields.Many2one("construction.contract", string="Contract")
    project_id = fields.Many2one("project.project", string="Project")
    partner_id = fields.Many2one('res.partner', string="Customer",)
    contract_value = fields.Float(string="Owner Contract value")
    estimate_cost_value = fields.Float(string="Estimat Cost Value")
    estimate_sales_value = fields.Float(string="Estimat Sales Value")
    owner_invoice = fields.Float("Owner Ivoice")
    cost_value = fields.Float("Cost")
    profit = fields.Float("Profit")
    profit_prec = fields.Float("profit Percent")
    revenue_variance = fields.Float("revenue variance")
    cost_variance = fields.Float("cost variance")


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        query = """
              
             select invoice_qs.id as id,invoice_qs.contract_id as contract_id
             ,invoice_qs.project_id as project_id ,invoice_qs.partner_id as partner_id,
            invoice_qs.contract_value as contract_value,
            invoice_qs.owner_invoice as owner_invoice ,invoice_qs.estimate_cost_value,invoice_qs.estimate_sales_value,
            move.debit as cost_value ,(invoice_qs.owner_invoice-move.debit) as profit ,(invoice_qs.estimate_sales_value-invoice_qs.owner_invoice) as revenue_variance,
            ((invoice_qs.owner_invoice-move.debit)/move.debit)as profit_prec ,(invoice_qs.estimate_cost_value-move.debit) as cost_variance
            
            
             from 
            (select  invoice.id as id,invoice.contract_id as contract_id
             ,invoice.project_id as project_id ,invoice.partner_id as partner_id,
            invoice.contract_value as contract_value,
            invoice.owner_invoice as owner_invoice ,qss.estimate_cost_value,qss.estimate_sales_value
            
            from (select  min(inv.id) as id,inv.contract_id as contract_id,inv.project_id as project_id ,inv.partner_id as partner_id,
            inv.contract_value as contract_value,sum(inv.amount_price_total) as owner_invoice 
            from account_invoice as inv 
            where inv.type='owner'
            group by inv.contract_id,inv.project_id,inv.partner_id,inv.contract_value)as invoice

            join
            (  select sum(qs.estimate_cost_value) as estimate_cost_value,sum(qs.estimate_sales_value)as estimate_sales_value,
            qs.project_id
                from quantity_survey as qs
                group by qs.project_id

            ) as qss
            on qss.project_id=invoice.project_id) as invoice_qs
            join 
            (select line.project_id,sum(line.debit)as debit
            from account_move_line as line
            where line.type_invoice!='owner' or line.type_invoice IS NULL
            group by line.project_id) as move
            on invoice_qs.project_id=move.project_id
        
        """
        return query




    def init(self):
        # self._table = "profit_project"
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

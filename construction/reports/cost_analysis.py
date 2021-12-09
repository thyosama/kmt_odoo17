from odoo import tools
from odoo import api, fields, models


class project_profit(models.Model):
    _name = 'cost.analysis.report'
    _description = "Cost Analysis  Report"
    _auto = False

    project_id = fields.Many2one("project.project", string="Project")
    product_id = fields.Many2one("product.product", string="Product")
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    qty = fields.Float("Quantity")
    value = fields.Float("Value")
    item = fields.Many2one('product.item', string='Item')
    date = fields.Date("Date")
    #journal_id = fields.Many2one("account.journal", string="Journal")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        query="""
        
            select move.id as id,stm.product_id as product_id,stm.product_uom as product_uom,
                stm.product_uom_qty as qty,stm.item as item,move.project_id as project_id,move.date as date 
                ,ABS(move.amount_total_signed) as value

                from account_move as move join stock_move as stm on move.stock_move_id=stm.id
                where move.project_id is not NULL
                UNION ALL
                select stm.id as id,stm.product_id as product_id,stm.uom_id as product_uom,0 as qty
               ,stm.item as item,stm.project_id as project_id,stm_id.date as date
                        ,ABS(stm.amount) as value

                from account_bank_statement_line as stm join account_bank_statement as stm_id on stm.statement_id=stm_id.id
                where stm.product_id is NOT NULL and stm.item is NOT NULL
                UNION ALL


                select inv.id as id,sub.product_id as product_id,inv.uom_id as product_uom,inv.current_qty as qty
               ,inv.item as item,inv.project_id as project_id,inv.date as date,abs(inv.total_value) as value

                from account_invoice_line as inv  join construction_subconstractor as sub on sub.id=inv.sub_contarctor_item
                where inv.sub_contarctor_item is NOT NULL
                
                 UNION ALL


                select inv.id as id,inv.product_id as product_id,inv.product_uom_id as product_uom,inv.quantity as qty
               ,inv.item as item,inv.project_id as project_id,move.date as date,ABS(inv.price_subtotal) as value
               from account_move_line as inv join account_move as move on move.id=inv.move_id
               where move.move_type='in_invoice' and move.state='posted' 
  
        
        """

        return query

    def init(self):
        # self._table = "profit_project"
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

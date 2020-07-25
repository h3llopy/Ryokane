from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError


# Add tag validation in sale order


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['analytic.dimension.line', 'sale.order.line']
    _analytic_tag_field_name = 'analytic_tag_ids'


# Add validation in purchase order

class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['analytic.dimension.line', 'purchase.order.line']
    _analytic_tag_field_name = 'analytic_tag_ids'


# Add permitted analytic dimensions for account

class InvoiceAccount(models.Model):
    _inherit = 'account.account'

    analytic_dimension_ids = fields.One2many('analytic.account.dimension',
                                       'analytic_dimension_id_link', string='Analytic Dimensions')

#  Add fields to tree view analytic dimensions in chart of accounts


class AnalyticTagInvoice(models.Model):
    _name = 'analytic.account.dimension'

    analytic_dimension_id = fields.Many2one('account.analytic.dimension', String='Dimension')
    analytic_dimension_id_link = fields.Many2one('account.account', String='Dimension')
    available = fields.Boolean(String='Available')
    default_value = fields.Many2one('account.analytic.tag', String='Default value')

    @api.onchange('analytic_dimension_id')
    def _check_dimension(self):
        account_id = self.analytic_dimension_id_link
        dimensions_analytic_ids = [dimension.analytic_dimension_id.id for dimension in account_id.analytic_dimension_ids]
        return {
            'domain': {'analytic_dimension_id': [('id', 'not in', dimensions_analytic_ids)]},
        }

    @api.onchange('analytic_dimension_id', 'available')
    def _onchange_dimension_ids(self):
        tag_name = 0
        if self.available == True:
            for tags in self.analytic_dimension_id.analytic_tag_ids:
                tag_name = tags.id
            self.default_value = tag_name

    @api.onchange('analytic_dimension_id')
    def _onchange_dimension_ids(self):
        dimension_ids = [self.analytic_dimension_id.id]
        return {'domain': {
            'default_value': [('analytic_dimension_id', 'in', dimension_ids)],
        }}


# Analytic tag in Delivery


class StockPickingDelivery(models.Model):
    _inherit = 'stock.move'

    analytic_tag_ids = fields.Many2many('account.analytic.tag', String='Analytic Tag')

    @api.model
    def create(self, vals):
        res = super(StockPickingDelivery, self).create(vals)
        if res.sale_line_id:
            res.update({
                'analytic_tag_ids': res.sale_line_id.analytic_tag_ids.ids
                        })
        if res.purchase_line_id:
            res.update({
                'analytic_tag_ids': res.purchase_line_id.analytic_tag_ids.ids
            })

        if self.env.context.get('pos_analytic_tag_ids'):
              res.update({
                'analytic_tag_ids': self.env.context.get('pos_analytic_tag_ids')
            })

        # if not (res.purchase_line_id or res.sale_line_id or res.inventory_id or res.production_id or res.raw_material_production_id):
        #     config = self.env['pos.config'].search([])
        #     res.update({
        #         'analytic_tag_ids': config.analytic_tag_ids.ids
        #     })
        return res


class StockPickingReturn(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    analytic_tag_id = fields.Many2many('account.analytic.tag', String='Analytic Account')


class ReturnStockPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        res = super(ReturnStockPicking, self).default_get(fields)
        move_dest_exists = False
        product_return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking:
            res.update({'picking_id': picking.id})
            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings."))
            for move in picking.move_lines:
                if move.scrapped:
                    continue
                if move.move_dest_ids:
                    move_dest_exists = True
                quantity = move.product_qty - sum(
                    move.move_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']). \
                    mapped('move_line_ids').mapped('product_qty'))
                quantity = float_round(quantity, precision_rounding=move.product_uom.rounding)
                product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity,
                                                    'move_id': move.id, 'uom_id': move.product_id.uom_id.id,
                                                    'analytic_tag_id': move.analytic_tag_ids.ids
                                                    }))

            if not product_return_moves:
                raise UserError(
                    _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': product_return_moves})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest_exists})
            if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
                res.update({
                            'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
            if 'original_location_id' in fields:
                res.update({'original_location_id': picking.location_id.id})
            if 'location_id' in fields:
                location_id = picking.location_id.id
                if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                    location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                res['location_id'] = location_id
        return res



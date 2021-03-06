# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_pos_lot = fields.Boolean('Allow POS Lot', default=True)
    lot_expire_days = fields.Integer('Product Lot expire days.', default=1)
    pos_lot_receipt = fields.Boolean('Print lot Number on receipt',default=1)

class stock_production_lot(models.Model):
    _inherit = "stock.production.lot"

    total_qty = fields.Float("Total Qty", compute="_computeTotalQty")
    
    @api.multi
    def _computeTotalQty(self):
        pos_config = self.env['pos.config'].search([], limit=1)
        pos_location_id = self.env['stock.location'].search([('id','=',pos_config.stock_location_id.id)])
        for record in self:
            move_line = self.env['stock.move.line'].search([('lot_id','=',record.id)])
            record.total_qty = 0.0
            for rec in move_line:
                #if rec.location_dest_id.usage in ['internal', 'transit']:
                #    record.total_qty += rec.qty_done
                #else:
                #    record.total_qty -= rec.qty_done
                if rec.location_dest_id == pos_location_id:
                    record.total_qty += rec.qty_done
                elif rec.location_id == pos_location_id:
                    record.total_qty -= rec.qty_done
                else:
                    continue 


class PosOrder(models.Model):
    _inherit = "pos.order"

    def set_pack_operation_lot(self, picking=None):
        """Set Serial/Lot number in pack operations to mark the pack operation done."""

        StockProductionLot = self.env['stock.production.lot']
        PosPackOperationLot = self.env['pos.pack.operation.lot']
        has_wrong_lots = False
        for order in self:
            for move in (picking or self.picking_id).move_lines:
                picking_type = (picking or self.picking_id).picking_type_id
                lots_necessary = True
                if picking_type:
                    lots_necessary = picking_type and picking_type.use_existing_lots
                qty = 0
                qty_done = 0
                pack_lots = []
                pos_pack_lots = PosPackOperationLot.search([('order_id', '=', order.id), ('product_id', '=', move.product_id.id)])
                pack_lot_names = [pos_pack.lot_name for pos_pack in pos_pack_lots]
                if pack_lot_names and lots_necessary:
                    for lot_name in list(set(pack_lot_names)):
                        stock_production_lot = StockProductionLot.search([('name', '=', lot_name), ('product_id', '=', move.product_id.id)])
                        if stock_production_lot:
                            if stock_production_lot.product_id.tracking == 'lot':
                                tt = 0
                                for ll in pack_lot_names:
                                    if ll == lot_name:
                                        tt += 1

                                # if a lot nr is set through the frontend it will refer to the full quantity
                                qty = tt
                            else: # serial numbers
                                qty = 1.0
                            qty_done += qty
                            pack_lots.append({'lot_id': stock_production_lot.id, 'qty': qty})
                        else:
                            has_wrong_lots = True
                elif move.product_id.tracking == 'none' or not lots_necessary:
                    qty_done = move.product_uom_qty
                else:
                    has_wrong_lots = True
                for pack_lot in pack_lots:
                    lot_id, qty = pack_lot['lot_id'], pack_lot['qty']
                    self.env['stock.move.line'].create({
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'qty_done': qty,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id': lot_id,
                    })
                if not pack_lots:
                    move.quantity_done = qty_done
        return has_wrong_lots

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        result = super(PosOrder, self)._action_create_invoice_line(line, invoice_id)
        for pro_lot in line.pack_lot_ids:
            pro_lot.account_invoice_line_id = result.id
        return result

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    pack_lot_ids = fields.One2many('pos.pack.operation.lot', 'account_invoice_line_id', string='Lot/serial Number')


class PosOrderLineLot(models.Model):
    _inherit = "pos.pack.operation.lot"

    account_invoice_line_id = fields.Many2one('account.invoice.line')
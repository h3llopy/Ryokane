from dateutil import parser
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PromoClass(models.Model):
    _inherit = 'website_sale_coupon'
    _name= 'website_sale_coupon'


    def _filter_not_ordered_reward_programs(self, order):
        """
        Returns the programs when the reward is actually in the order lines
        """
        raise UserError(_('Malek in F1'))
        programs = self.env['sale.coupon.program']
        for program in self:
            if program.reward_type == 'product' and \
               not order.order_line.filtered(lambda line: line.product_id == program.reward_product_id):
                order.write({'order_line': [(0, False, value) for value in order._put_reward_values_product(program)]})
            elif program.reward_type == 'discount' and program.discount_apply_on == 'specific_product' and \
               not order.order_line.filtered(lambda line: line.product_id == program.discount_specific_product_id):
                continue
            programs |= program
        return programs

class SalesClass(models.Model):
    _inherit = 'sale.order'
    _name= 'sale_order'

    def _put_reward_values_product(self, program):
        raise UserError(_('Malek in F2'))
        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_unit

        order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._is_valid_product(x.product_id))
        reward_qty= program.reward_product_quantity
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.reward_product_id.id,
            'product_uom_qty': reward_qty,
            'name': program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }
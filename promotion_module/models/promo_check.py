from odoo import api, fields, models, _


class PromoClass(models.Model):
   
    _inherit = "sale.coupon.program"


def _filter_not_ordered_reward_programs(self, order):
        """
        Returns the programs when the reward is actually in the order lines
        """
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


def _put_reward_values_product(self, program):
        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_unit

        order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._is_valid_product(x.product_id))
        # max_product_qty = sum(order_lines.mapped('product_uom_qty')) or 1
        # Remove needed quantity from reward quantity if same reward and rule product
        #if program._is_valid_product(program.reward_product_id):
         #   reward_product_qty = max_product_qty // (program.rule_min_quantity + program.reward_product_quantity)
       # else:
        #    reward_product_qty = min(max_product_qty, self.order_line.filtered(lambda x: x.product_id == program.reward_product_id).product_uom_qty)

      #  reward_qty = min(int(int(max_product_qty / program.rule_min_quantity) * program.reward_product_quantity), reward_product_qty)
        reward_qty= program.reward_product_quantity
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.reward_product_id.id,
           # 'price_unit': - price_unit,
            'product_uom_qty': reward_qty,
          #  'is_reward_line': True,
            'name': program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }
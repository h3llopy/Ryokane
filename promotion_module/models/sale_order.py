from dateutil import parser
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SalesClass(models.Model):
    _inherit = 'sale.order'


    def _create_new_no_code_promo_reward_lines(self):
        '''Apply new programs that are applicable'''
        self.ensure_one()
        order = self
        programs = order._get_applicable_no_code_promo_program()
        programs = programs._keep_only_most_interesting_auto_applied_global_discount_program()
        for program in programs:
            error_status = program._check_promo_code(order, False)
            if not error_status.get('error'):
                if program.promo_applicability == 'on_next_order':
                    order._create_reward_coupon(program)
                elif program.discount_line_product_id.id not in self.order_line.mapped('product_id').ids:
                    if program.reward_type == 'product':
                        self.write({'order_line': [(0, False, self._put_reward_values_product(program)]})
                    self.write({'order_line': [(0, False, value) for value in self._get_reward_line_values(program)]})
                order.no_code_promo_program_ids |= program

    def _put_reward_values_product(self, program):

        order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._is_valid_product(x.product_id))
        max_product_qty = sum(order_lines.mapped('product_uom_qty')) or 1
        # Remove needed quantity from reward quantity if same reward and rule product
        if program._is_valid_product(program.reward_product_id):
            #reward_product_qty = max_product_qty // (program.rule_min_quantity + program.reward_product_quantity)
            reward_product_qty = max_product_qty // (program.rule_min_quantity)
        else:
            reward_product_qty = min(max_product_qty, self.order_line.filtered(lambda x: x.product_id == program.reward_product_id).product_uom_qty)

        reward_qty = min(int(int(max_product_qty / program.rule_min_quantity) * program.reward_product_quantity), reward_product_qty)

        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)

         return {
            'product_id': program.reward_product_id.id,
            'product_uom_qty': reward_qty,
            'is_reward_line': True, 
            'name': program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }

    def _get_reward_values_product(self, program):

        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_reduce

        order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._is_valid_product(x.product_id))
        max_product_qty = sum(order_lines.mapped('product_uom_qty')) or 1
        # Remove needed quantity from reward quantity if same reward and rule product
        if program._is_valid_product(program.reward_product_id):
            #reward_product_qty = max_product_qty // (program.rule_min_quantity + program.reward_product_quantity)
            reward_product_qty = max_product_qty // (program.rule_min_quantity)
        else:
            reward_product_qty = min(max_product_qty, self.order_line.filtered(lambda x: x.product_id == program.reward_product_id).product_uom_qty)

        reward_qty = min(int(int(max_product_qty / program.rule_min_quantity) * program.reward_product_quantity), reward_product_qty)

        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.discount_line_product_id.id,
            'price_unit': - price_unit,
            'product_uom_qty': reward_qty,
            'is_reward_line': True,
            'name': _("Free Product") + " - " + program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }


    def _remove_invalid_reward_lines(self):
        """ Find programs & coupons that are not applicable anymore.
            It will then unlink the related reward order lines.
            It will also unset the order's fields that are storing
            the applied coupons & programs.
            Note: It will also remove a reward line coming from an archive program.
        """
        self.ensure_one()
        order = self

        applicable_programs = order._get_applicable_no_code_promo_program() + order._get_applicable_programs() + order._get_valid_applied_coupon_program()
        applicable_programs = applicable_programs._keep_only_most_interesting_auto_applied_global_discount_program()
        applied_programs = order._get_applied_programs_with_rewards_on_current_order() + order._get_applied_programs_with_rewards_on_next_order()
        programs_to_remove = applied_programs - applicable_programs
        products_to_remove = programs_to_remove.mapped('discount_line_product_id')
        rewards_to_remove = programs_to_remove.mapped('reward_product_id')

        # delete reward line coming from an archived coupon (it will never be updated/removed when recomputing the order)
        invalid_lines = order.order_line.filtered(lambda line: line.is_reward_line and line.product_id.id not in (applied_programs).mapped('discount_line_product_id').ids)

        # Invalid generated coupon for which we are not eligible anymore ('expired' since it is specific to this SO and we may again met the requirements)
        self.generated_coupon_ids.filtered(lambda coupon: coupon.program_id.discount_line_product_id.id in products_to_remove.ids).write({'state': 'expired'})
        # Reset applied coupons for which we are not eligible anymore ('valid' so it can be use on another )
        coupons_to_remove = order.applied_coupon_ids.filtered(lambda coupon: coupon.program_id in programs_to_remove)
        coupons_to_remove.write({'state': 'new'})

        # Unbind promotion and coupon programs which requirements are not met anymore
        order.no_code_promo_program_ids -= programs_to_remove
        order.code_promo_program_id -= programs_to_remove
        order.applied_coupon_ids -= coupons_to_remove

        # Remove their reward lines
        invalid_lines |= order.order_line.filtered(lambda line: line.product_id.id in products_to_remove.ids)
        invalid_lines |= order.order_line.filtered(lambda line: line.product_id.id in rewards_remove.ids and line.is_reward_line)
        invalid_lines.unlink()


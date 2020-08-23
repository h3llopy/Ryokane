from dateutil import parser
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PromoClass(models.Model):
    _inherit = 'sale.coupon.program'

    def _filter_programs_on_products(self, order):
        """
        To get valid programs according to product list.
        i.e Buy 1 imac + get 1 ipad mini free then check 1 imac is on cart or not
        or  Buy 1 coke + get 1 coke free then check 1 coke is on cart or not
        """
        order_lines = order.order_line.filtered(lambda line: line.product_id) - order._get_reward_lines()
        products = order_lines.mapped('product_id')
        products_qties = dict.fromkeys(products, 0)
        for line in order_lines:
            products_qties[line.product_id] += line.product_uom_qty
        valid_programs = self.filtered(lambda program: not program.rule_products_domain)
        for program in self - valid_programs:
            valid_products = program._get_valid_products(products)
            _logger.info('WAFI: filter_programs_on_products:')
            _logger.info(valid_products)
            ordered_rule_products_qty = sum(products_qties[product] for product in valid_products)
            _logger.info(ordered_rule_products_qty)
            # Avoid program if 1 ordered foo on a program '1 foo, 1 free foo'
            #if program.promo_applicability == 'on_current_order' and \
            #   program._is_valid_product(program.reward_product_id) and program.reward_type == 'product':
            #    ordered_rule_products_qty -= program.reward_product_quantity
            if ordered_rule_products_qty >= program.rule_min_quantity:
                valid_programs |= program
        return valid_programs

    def _filter_not_ordered_reward_programs(self, order):
        """
        Returns the programs when the reward is actually in the order lines
        If not, add reward product into order lines
        """
        _logger.info('WAFI: not ordered reward program')
        programs = self.env['sale.coupon.program']
        _logger.info(programs)
        for program in self:
            if program.reward_type == 'product' and \
               not order.order_line.filtered(lambda line: line.product_id == program.reward_product_id):
                _logger.info(program)
                _logger.info(order._put_reward_values_product(program))
                order.write({'order_line': [(0, False, order._put_reward_values_product(program))]})
            elif program.reward_type == 'discount' and program.discount_apply_on == 'specific_product' and \
               not order.order_line.filtered(lambda line: line.product_id == program.discount_specific_product_id):
                continue
            programs |= program
        return programs


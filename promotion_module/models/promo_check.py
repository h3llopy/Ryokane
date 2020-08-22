from dateutil import parser
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PromoClass(models.Model):
    _inherit = 'sale.coupon.program'
    _name= 'sale.coupon.program'


    def _filter_not_ordered_reward_programs(self, order):
        """
        Returns the programs when the reward is actually in the order lines
        """
        _logger.info('WAFI: not ordered reward program')
        programs = self.env['sale.coupon.program']
        for program in self:
            if program.reward_type == 'product' and \
               not order.order_line.filtered(lambda line: line.product_id == program.reward_product_id):
                order.write({'order_line': [(0, value) for value in order._put_reward_values_product(program)]})
            elif program.reward_type == 'discount' and program.discount_apply_on == 'specific_product' and \
               not order.order_line.filtered(lambda line: line.product_id == program.discount_specific_product_id):
                continue
            programs |= program
        return programs


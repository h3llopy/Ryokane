# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import simplejson
from datetime import datetime
import base64
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode


class WebsiteSale(WebsiteSale):
    @http.route(['/gift_card'], type='http', auth="public", website=True)
    def gift_card_page(self, **post):
        values = {'page': 1}
        if request.session.get('gift_card_error'):
            values = request.session.get('gift_card_error')
            request.session['gift_card_error'] = False
        return request.render("aspl_website_gift_card_ee.gift_card", values)

    @http.route(['/buy_gift_card'], type='http', csrf=False, method=['post'], auth="public", website=True)
    def buy_gift_card_page(self, **kw):
        gift_card_value = request.env['gift.card.value'].sudo().search([('id', '=', int(kw.get('gift_card_value')))])
        if gift_card_value:
            gift_card_id = request.env['product.product'].sudo().search([('is_gift_card', '=', True)])
            gift_card_id.write({
                'lst_price': gift_card_value.amount
            })
   
            order_id = request.website.sale_get_order(force_create=1)
            order_id.write({
                'receiver_email': kw.get('receiver_email'),
                'receiver_name': kw.get('receiver_name'),
                'receiver_msg': kw.get('receiver_msg'),
            })
            order_id._cart_update(
                product_id=int(gift_card_id),
                add_qty=float(kw.get('gift_qty') or 1),
            )
            return request.redirect("/shop/cart")
        request.session['gift_card_error'] = {'error_gift': "Invalid Gift Card Amount", 'page': 1}
        return request.redirect('/gift_card')

    @http.route(['/check_gift_card_details'], type='http', auth="public", website=True)
    def check_gift_card_details(self, card_number=False, pin=False, **kw):
        error_msg = "Please Provide Card Number and PIN"
        if card_number and pin:
            gift_card_id = request.env['aspl.gift.card'].search([('card_no', '=', int(card_number)),
                                                                    ('pin_no', '=', int(pin))])
            if not gift_card_id:
                error_msg = "Invalid Card Number or PIN"
            else:
                value = {
                    'gift_card': gift_card_id,
                }
                return request.render('aspl_website_gift_card_ee.gift_card_details', value)
        request.session['gift_card_error'] = {'error_gift': error_msg, 'page': 2}
        return request.redirect('/gift_card')

    @http.route(['/shop/set_pin'], type='http', auth="public", website=True)
    def gift_card_set_pin(self, value='', **post):
        MASTER_KEY = "Some-long-base-key-to-use-as-encyrption-key"
        value = value.replace(' ', '+')
        cipher = b64decode(value)
        clear_val = decrypt(MASTER_KEY, cipher)
        gift_card_id = request.env['aspl.gift.card'].search([('id', '=', int(clear_val))])
        value = {
            'gift_card_id': gift_card_id
        }
        return request.render("aspl_website_gift_card_ee.gift_card_set_pin", value)

    @http.route(['/shop/set/pin'], type='json', auth="public", website=True)
    def gift_card_pin(self, card_id=0, pin=0, **kw):
        gift_card_id = request.env['aspl.gift.card'].search([('id', '=', int(card_id))])
        gift_card_id.write({
            'pin_no': int(pin)
        })

        return True

    @http.route(['/set/pin'], type='http', auth="public", website=True)
    def gift_set_pin(self, card_id=0, pin=0, **kw):
        gift_card_id = request.env['aspl.gift.card'].search([('id', '=', int(kw.get('id')))])
        gift_card_id.write({
            'pin_no': int(pin)
        })

        return request.redirect('/gift_card')

    @http.route(['/card_details'], type='json', auth="public", csrf=False, method=['post'], website=True)
    def gift_card_details(self, id=0, card_number=0, pin=0, **kw):
        gift_card_id = request.env['aspl.gift.card'].search([('card_no', '=', int(card_number)),
                                                                ('pin_no', '=', int(pin))])
        if gift_card_id:
            usage_history_list = []
            recharge_history_list = []
            gift_card_usage_ids = request.env['gift.card.use'].search([('card_id', '=', gift_card_id.id)])
            gift_card_recharge_ids = request.env['gift.card.recharge'].search([('card_id', '=', gift_card_id.id)])
            for gift_card_usage_id in gift_card_usage_ids:
                usage_history_list.append(
                    {
                        'order_date': str(gift_card_usage_id.order_date),
                        'order_name': gift_card_usage_id.order_id.name,
                        'amount': gift_card_usage_id.amount
                    }
                )

            for gift_card_recharge_id in gift_card_recharge_ids:
                recharge_date = str(
                    datetime.strptime(datetime.strftime(gift_card_recharge_id.create_date, '%Y-%m-%d %H:%M:%S'),
                                      '%Y-%m-%d %H:%M:%S').date())
                recharge_history_list.append(
                    {
                        'recharge_date': recharge_date,
                        'amount': gift_card_recharge_id.amount,
                    }
                )
            value = {
                'id': gift_card_id.id,
                'balance': gift_card_id.card_value,
                'usage_history': usage_history_list,
                'recharge_history': recharge_history_list,
                'symbol': request.env.user.company_id.currency_id.symbol,
            }
            return simplejson.dumps(value)
        else:
            return False

    @http.route(['/apply_gift_card'], type='json', auth="public", csrf=False, method=['post'], website=True)
    def apply_gift_card(self, id=0, amount=0, **kw):
        gift_card_id = request.env['aspl.gift.card'].search([('id', '=', int(id))])
        gift_card_session_id = request.session.get('gift_card_id')
        amount = float(amount)
        if gift_card_id.card_value >= amount:
            if not gift_card_session_id:
                sale_order_id = request.session.get('sale_last_order_id')
                sale_order = request.env['sale.order'].search([('id', '=', sale_order_id)])
                if sale_order.amount_total >= amount:
                    card_value = gift_card_id.card_value - amount
                    gift_card_id.write({
                        'card_value': card_value
                    })
                    amount_total = sale_order.amount_total - amount
                    sale_order.write({
                        'gift_card_value': amount,
                        'amount_total': amount_total
                    })
                    request.env['gift.card.use'].create({
                        'card_id': gift_card_id.id,
                        'order_id': sale_order_id,
                        'amount': amount,
                        'order_date': datetime.now()
                    })
                    request.session['gift_card_id'] = id
                    return simplejson.dumps({'success': True})
                else:
                    return simplejson.dumps({'error': True})
            else:
                sale_order_id = request.session.get('sale_last_order_id')
                sale_order = request.env['sale.order'].search([('id', '=', sale_order_id)])
                if sale_order.amount_total >= amount:
                    card_value = gift_card_id.card_value - amount
                    gift_card_id.write({
                        'card_value': card_value
                    })
                    amount_total = sale_order.amount_total - amount
                    sale_order.write({
                        'gift_card_value': sale_order.gift_card_value + amount,
                        'amount_total': amount_total
                    })
                    request.env['gift.card.use'].create({
                        'card_id': gift_card_id.id,
                        'order_id': sale_order_id,
                        'amount': amount,
                        'order_date': datetime.now()
                    })
                    request.session['gift_card_id'] = id
                    return simplejson.dumps({'success': True})
                else:
                    return simplejson.dumps({'error': True})
        else:
            return False

    @http.route(['/cancel_gift_card'], type='http', auth="public", csrf=False, method=['post'], website=True)
    def cancel_gift_card(self, card_id=0, amount=0, **kw):
        gift_card_id = int(card_id)
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order = request.env['sale.order'].search([('id', '=', sale_order_id)])
        gift_card = request.env['aspl.gift.card'].search([('id', '=', gift_card_id)])
        gift_card_use_id = request.env['gift.card.use'].search([('card_id', '=', gift_card_id),
                                                                ('amount', '=', float(amount))], limit=1)
        gift_card.write({
            'card_value': gift_card.card_value + gift_card_use_id.amount
        })
        sale_order.write({
            'gift_card_value': sale_order.gift_card_value - gift_card_use_id.amount,
            'amount_total': sale_order.amount_total + gift_card_use_id.amount
        })
        gift_card_use_id.unlink()
        return request.redirect('/shop/payment')

    @http.route(['/recharge_gift_card'], type='json', csrf=False, method=['post'], auth="public", website=True)
    def recharge_gift_card(self, id=0, amount=0, **kw):
        id = int(id)
        amount = int(amount)
        gift_card_id = request.env['product.product'].search([('is_gift_card', '=', True)])
        gift_card_id.write({
            'lst_price': amount
        })
        res = request.website.sale_get_order(force_create=1)
        res._cart_update(
            product_id=int(gift_card_id.id),
            add_qty=1,
        )
        res.write({
            'gift_card_id': id
        })
        return True

    # @http.route(['/change_pin'], type='json', auth="public", website=True)
    # def change_pin(self, id=0, current_pin=0, pin=0, **kw):
    #     gift_card_id = request.env['website.gift.card'].search(
    #         [('id', '=', int(id)), ('pin_no', '=', int(current_pin))])
    #     if gift_card_id:
    #         gift_card_id.write({
    #             'pin_no': int(pin)
    #         })
    #         return True
    #     else:
    #         return False

    @http.route(['/shop/applied_card'], type='http', auth="public", website=True)
    def view_applied_card(self, **post):
        if post.get('type') == 'popover':
            sale_order_id = request.session.get('sale_last_order_id')
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            gift_card_use_ids = request.env['gift.card.use'].search([('order_id', '=', order.id)])
            confirm_order = False
            if order.state == 'done' or order.state == 'sale':
                confirm_order = True
            return request.render("aspl_website_gift_card_ee.view_applied_card",
                                  {'gift_card_use_ids': gift_card_use_ids, 'confirm_order': confirm_order})

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        gift_card_session_id = request.session.get('gift_card_id')
        if gift_card_session_id:
            request.session['gift_card_id'] = None
        res = super(WebsiteSale, self).payment_confirmation(**post)
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            line = order.order_line.filtered(lambda r: r.product_id.is_gift_card)
            if line:
                return request.render("website_sale.confirmation", {'order': order, 'gift': line})
            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        res = super(WebsiteSale, self).payment(**post)
        sale_order_id = request.session.get('sale_last_order_id')
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        line = order.order_line.filtered(lambda r: r.product_id.is_gift_card)
        if line:
            res.qcontext['gift_card'] = line
        return res

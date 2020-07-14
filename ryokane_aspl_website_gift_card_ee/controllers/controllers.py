import simplejson
from datetime import datetime
import base64
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode

from odoo.addons.aspl_website_gift_card_ee.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
 

    @http.route(['/buy_gift_card'], type='http', csrf=False, method=['post'], auth="public", website=True)
    def buy_gift_card_page(self, **kw):
        gift_card_value = request.env['gift.card.value'].sudo().search([('id', '=', int(kw.get('gift_card_value')))])
        if gift_card_value:
            gift_card_id = request.env['product.product'].sudo().search([('is_gift_card', '=', True)], limit=1)
            gift_card_id.write({
                'lst_price': gift_card_value.amount
            })
            order_id = request.website.sale_get_order(force_create=1)
            order_id.write({
                'receiver_email': kw.get('receiver_email'),
                'receiver_name': kw.get('receiver_name'),
            })
            order_id._cart_update(
                product_id=int(gift_card_id),
                add_qty=float(kw.get('gift_qty') or 1),
            )
            return request.redirect("/shop/cart")
        request.session['gift_card_error'] = {'error_gift': "Invalid Gift Card Amount", 'page': 1}
        return request.redirect('/gift_card')

    @http.route(["/check_gift_card_details"], type="http", auth="public", website=True)
    def check_gift_card_details(self, card_number=False, pin=False, **kw):
        error_msg = "Please Provide Card Number and PIN"
        if card_number:
            gift_card_id = request.env["aspl.gift.card"].search(
                [("card_no", "=", int(card_number))], limit=1
            )
            if not gift_card_id:
                error_msg = "Invalid Card Number or PIN"
            else:
                value = {
                    "gift_card": gift_card_id,
                }
                return request.render("aspl_website_gift_card_ee.gift_card_details", value)
        request.session["gift_card_error"] = {"error_gift": error_msg, "page": 2}
        return request.redirect("/gift_card")



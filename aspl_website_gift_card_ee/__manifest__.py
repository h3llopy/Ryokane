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

{
    'name': 'Odoo Website Gift Card (Enterprise)',
    'summary': 'This module allows user to purchase giftcard,use giftcard and also recharge giftcard.',
    'version': '1.2',
    'description' :"""This module allows user to purchase giftcard,use giftcard and also recharge giftcard.""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Website',
    'website': "http://www.acespritech.com",
    'price': 35,
    'currency': 'EUR',
    'depends' : ['base', 'website_sale', 'sale', 'website', 'aspl_gift_card'],
    'data' : [
        # 'security/ir.model.access.csv',
        'views/gift_card.xml',
        'views/gift_card_mail_template.xml',
        'views/gift_card_backend_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

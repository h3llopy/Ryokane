# -*- coding: utf-8 -*-

{
    'name': 'Pos Lot/Serial Number(s)',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'This module allows you to search products by Lot/Serial Number(s).',
    'description': """

=======================

This module allows you to search products by Lot/Serial Number(s).

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/pos.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 59,
    'currency': 'EUR',
}

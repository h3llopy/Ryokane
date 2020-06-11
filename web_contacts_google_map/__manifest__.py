# -*- coding: utf-8 -*-
{
    'name': "Web Contact Google Map",

    'summary': """
        this module allow to show google of contacts.""",

    'description': """
        Web Contact Google Map
        this module allow to show google of contacts.
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_geolocalize',
	'website',],

    # always loaded
   'data': [
		'views/res_partner_view.xml',
		'views/templates.xml',
	],
}
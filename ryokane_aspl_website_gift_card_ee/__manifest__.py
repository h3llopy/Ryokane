# -*- coding: utf-8 -*-
{
    "name": "Ryokane Aspl Website Gift Card",
    "summary": """Ryokane Aspl Website Gift Card""",
    "description": """
        Ryokane Aspl Website Gift Card
    """,
    "author": "Babatope Ajepe",
    "website": "http://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.3",
    # any module necessary for this one to work correctly
    "depends": ["base", "aspl_website_gift_card_ee"],
    # always loaded
    "data": [
        'security/ir.model.access.csv',
        "views/views.xml",
        "views/templates.xml",
    ],
    # only loaded in demonstration mode
    "demo": ["demo/demo.xml",],
}

{
    'name': "Ryokane Aspl Gift Card",

    'summary': """Ryokane Aspl Gift Card """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Babatope Ajepe",
    'website': "http://blog.galago.com.ng",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'aspl_gift_card'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
}
{
    'name': "Sale Promotion",
    'version': '12.0.1.0.3',
    'summary': """Create Promotion Offers For Sales""",
    'description': """This Module Allows to Set  Promotion Offers On Products And Product Categories.""",
    'author': "BAS",
    'category': 'Sales',
    'depends': ['sale_management', 'sale_coupon','account'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}



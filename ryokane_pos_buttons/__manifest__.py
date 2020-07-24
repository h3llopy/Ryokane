{
    "name": "Ryokane POS Buttons",
    "version": "12.0.1.2.3",
    "category": "Point of Sale",
    "author": "Babatope Ajepe",
    "website": "https://ajepe.github.io",
    "license": "LGPL-3",
    "depends": ["point_of_sale", "hr"],
    "data": ["security/ir.model.access.csv","views/assets.xml", "views/pos_order.xml",],
    "qweb": ["static/src/xml/pos.xml"],
    "application": False,
    "installable": True,
}

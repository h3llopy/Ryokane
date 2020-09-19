# -*- coding: utf-8 -*-
{
    'name': 'Website Language Flag',
    'version': '1.0',
    'category': 'Website',
    'author': 'FreelancerApps',
    'summary': 'Website Language Flag translate flag language translate multi language website flag localization',
    'description': '''
Website Language Flag
=====================
You Can Set Flag To Selected Language And this flag will visible to website(Website Language Flag)

To set flag image for particular language go to settings --> Translations --> Languages --> Select Language --> Upload Image For Flag Image field.

You will get all images inside Static --> src --> all_flag directory or you can upload any other png image as a language flag.
<keyword>
translate flag language translate multi language website flag localization
    ''',
    'depends': ['website'],
    'data': [
        'views/res_lang_view.xml',
        'views/assets.xml',
        'views/website_lang_template.xml',
    ],
    'images': ['static/description/website_language_flag_odoo_banner.png'],
    'price': 4.99,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False
}

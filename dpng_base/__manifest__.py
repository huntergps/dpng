# -*- coding: utf-8 -*-
{
    'name': "dpng_base",

    'summary': """
        Modulo base para la DPNG""",

    'description': """
        Modulo base para la DPNG
    """,

    'author': "Elmer Salazar A",
    'website': "https://galapagos.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'E-Commerce',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','product','l10n_ec_invoice'],

    # always loaded
    'data': [
        # 'data/l10n_latam_identification_type_data.xml',
        # 'data/res_partner.xml',
        'report/report_templates.xml',
        'data/company.xml',
        'views/product_category.xml',
        'views/res_company.xml',
    ],
    'demo': [

    ],
    'license': 'LGPL-3',

}

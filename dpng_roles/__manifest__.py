# -*- coding: utf-8 -*-
{
    'name': "dpng_roles",

    'summary': """
        Modulo para el envio de Roles de Pagos - DPNG""",

    'description': """
        Modulo para el envio de Roles de Pagos para la DPNG
    """,

    'author': "Elmer Salazar A",
    'website': "https://galapagos.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
            'base','dpng_base'
            ],

    # always loaded
    'data': [
        'security/dpng_roles_security.xml',
        'security/ir.model.access.csv',
        'views/roles_statment_views_form.xml',
        'views/roles_statment_views.xml',
        'views/roles_pagos_views.xml',
        'views/roles_pagos_det_views.xml',
        'report/rol_paperformat.xml',
        'report/rol_individual_report_templates.xml',
        'report/roles_report.xml',
        'views/menu.xml',
    ],
    'qweb': [],
    'demo': [],
    'application': True,
    'license': 'LGPL-3',

}

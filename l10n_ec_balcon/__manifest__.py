# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Balcon de Servicios',
    'version': '1.2',
    'category': 'Sales/Sales',
    'summary': 'Balcon de Servicios',
    'description': """
This module contains all the common features of Balcon de Servicios.
    """,
    'depends': ['base','mail', 'payment', 'portal', 'utm','l10n_ec_invoice'],
    'data': [
        'security/balcon_security.xml',
        'security/ir.model.access.csv',
        'report/balcon_report.xml',
        'report/balcon_report_views.xml',
        'report/balcon_report_templates.xml',
        # 'report/invoice_report_templates.xml',
        'report/report_all_channels_balcon_views.xml',
        'data/ir_sequence_data.xml',
        'data/mail_data_various.xml',
        'data/mail_template_data.xml',
        'data/mail_templates.xml',
        'data/balcon_data.xml',
        'wizard/balcon_make_invoice_advance_views.xml',
        'views/balcon_views.xml',
        'views/res_partner_views.xml',
        'views/mail_activity_views.xml',
        'views/variant_templates.xml',
        'views/balcon_portal_templates.xml',
        'views/balcon_onboarding_views.xml',
        'views/res_config_settings_views.xml',
        'views/payment_templates.xml',
        'views/payment_views.xml',
        'views/product_views.xml',
        'views/product_packaging_views.xml',
        'wizard/balcon_order_cancel_views.xml',
        'wizard/balcon_payment_link_views.xml',
        'wizard/balcon_order_cancel_views.xml',
        'wizard/balcon_order_bank_payment.xml'
    ],
    'demo': [
        'data/product_product_demo.xml',
        'data/balcon_demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'l10n_ec_balcon/static/src/scss/balcon_onboarding.scss',
            'l10n_ec_balcon/static/src/scss/product_configurator.scss',
            'l10n_ec_balcon/static/src/js/balcon.js',
            'l10n_ec_balcon/static/src/js/tours/balcon.js',
            'l10n_ec_balcon/static/src/js/product_configurator_widget.js',
            'l10n_ec_balcon/static/src/js/balcon_order_view.js',
            'l10n_ec_balcon/static/src/js/product_discount_widget.js',
        ],
        'web.report_assets_common': [
            'l10n_ec_balcon/static/src/scss/balcon_report.scss',
        ],
        'web.assets_frontend': [
            'l10n_ec_balcon/static/src/scss/balcon_portal.scss',
            'l10n_ec_balcon/static/src/js/balcon_portal_sidebar.js',
            'l10n_ec_balcon/static/src/js/payment_form.js',
        ],
        'web.assets_tests': [
            'l10n_ec_balcon/static/tests/tours/**/*',
        ],
        'web.qunit_suite_tests': [
            'l10n_ec_balcon/static/tests/product_configurator_tests.js',
            'l10n_ec_balcon/static/tests/balcon_team_dashboard_tests.js',
        ],
    },
    'license': 'LGPL-3',
}

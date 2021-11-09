# -*- coding: utf-8 -*-
{
    'name': "l10n_ec_invoice",

    'summary': """
        Ecuadorian Location for Invoice""",

    'description': """
        Ecuadorian Location for Invoice
    """,

    'author': "Elmer Salazar A.",
    'website': "https://www.galapagos.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Ecuador',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','base_iban','account_debit_note',
                'l10n_latam_invoice_document','l10n_latam_base','l10n_ec',
                'product_sequence','awesome_theme'],

    # always loaded
    'data': [
        # 'static/src/xml/assets.xml',
        'security/ir.model.access.csv',
        'data/l10n_ec_invoice_autorizacion.xml',
        'data/l10n_ec_electronic_document_env.xml',
        'data/l10n_ec_electronic_document_sing.xml',
        'data/l10n_latam_identification_type_data.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_template_vat_data.xml',
        'data/company.xml',
        'data/l10n_ec_electronic_document_queue.xml',
        'data/product_data.xml',
        'data/res_partner_data.xml',
        'views/res_company_view.xml',
        'views/partner_view.xml',
        'views/account_tax_view.xml',
        'views/account_journal_view.xml',
        'views/account_payment_term_views.xml',
        'views/account_move_view.xml',
        'views/account_move_view_lines.xml',
        'views/l10n_ec_invoice_autorizacion.xml',
        'views/l10n_ec_electronic_document.xml',
        'views/l10n_ec_electronic_document_queue.xml',
        'views/l10n_ec_electronic_document_env.xml',
        'views/l10n_latam_identification_type.xml',
        'views/res_config_settings_view.xml',
        'views/sri_menu.xml',
        'reports/report_invoice.xml',
        'reports/report_paper_format.xml',
    ],
    'application': True,
    'assets': {
            # 'web._assets_primary_variables': [
            #     'l10n_ec_invoice/static/src/scss/variables.scss',
            # ],
            'web.assets_backend': [
                'l10n_ec_invoice/static/src/scss/style.scss',
            ],
        },
    'license': 'LGPL-3',

    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

}

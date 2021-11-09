# -*- coding: utf-8 -*-
{
    'name': "anita_theme_setting",

    'summary': """
        Theme Setting For Themes
    """,

    'description': """
        anita theme setting for odoo, it support theme setting for odoo
    """,

    'author': "Anita Odoo",
    'website': "https://www.anitaodoo.com",

    'category': 'Theme/Backend',
    'version': '15.0.0.0.5',

    'images': ['static/description/screen_shot.png',
               'static/description/banner.png',
               'static/description/banner.png2'],
    'live_test_url': 'https://www.anitaodoo.com',
    'license': 'OPL-1',

    'price': 15,
    'license': 'OPL-1',
    'depends': ['base', 'web', 'anita_theme_base'],

    'data': [
        'security/ir.model.access.csv',
        'views/anita_pwa.xml',
        'views/anita_res_setting.xml',
        'views/anita_theme_mode.xml',
        'views/anita_theme_style.xml',
        'views/anita_theme_style_group.xml',
        'views/anita_theme_style_item.xml',
        'views/anita_theme_style_item_sub_group.xml',
        'views/anita_theme_var.xml',
        'views/anita_user_view.xml',
        'views/anita_import_theme_style.xml',
        'views/anita_web.xml',

        'wizard/anita_theme_mode_wizard.xml'
    ],

    'assets': {
        'web.assets_backend': [
            'anita_theme_setting/static/lib/bootstrap_color_picker/css/bootstrap-colorpicker.min.css',
            'anita_theme_setting/static/lib/bootstrap_color_picker/js/bootstrap-colorpicker.min.js',

            'anita_theme_setting/static/css/customizer.scss',
            'anita_theme_setting/static/js/anita_customizer.js',

            'anita_theme_setting/static/src/webclient.js',
        ],

        'web.assets_qweb': [
            'anita_theme_setting/static/xml/customizer.xml'
        ]
    }
}

# -*- coding: utf-8 -*-
{
    'name': "awesome_theme",

    'summary': """
        awesome theme for odoo15
    """,

    'description': """
        Awesome theme
        Mordern theme
        muliti mode theme
        multi style theme
        multi purpose theme
        color theme
        popular theme
        community theme
        enterprose theme
        odoo15 theme
        backend theme
        odoo 15 backend theme
        anita theme
        multi tab theme
    """,

    'author': "awesome theme",
    'website': "http://www.anitaodoo.com",
    'live_test_url': 'https://awesometheme15.anitaodoo.com/',

    'category': 'Theme/backend',
    'version': '15.0.0.2',

    'images': ['static/description/awesome_description.gif', 'static/description/awesome_screenshot.gif'],

    'price': 88,
    'license': 'OPL-1',
    'depends': ['base', 'web', 'base_setup', 'anita_theme_base', 'anita_theme_setting'],

    'data': [
        'data/default_mode_datas.xml',
        'data/mode_templates.xml'
    ],

    'assets': {
        'web.assets_backend': [

            'awesome_theme/static/css/awesome_common.scss',
            'awesome_theme/static/css/awesome_action_manager.scss',
            'awesome_theme/static/css/awesome_sidebar.scss',
            'awesome_theme/static/css/awesome_button.scss',
            'awesome_theme/static/css/awesome_header.scss',
            'awesome_theme/static/css/awesome_discuss.scss',
            'awesome_theme/static/css/awesome_chat.scss',
            'awesome_theme/static/css/awesome_overlay.scss',
            'awesome_theme/static/css/perfect_scrollbar.css',
            'awesome_theme/static/css/awesome_board.scss',
            'awesome_theme/static/css/awesome_scrollbar.scss',
            'awesome_theme/static/css/awesome_datetime_picker.scss',
            'awesome_theme/static/css/awesome_select2.scss',
            'awesome_theme/static/css/awesome_company.scss',
            'awesome_theme/static/css/awesome_pager.scss',
            'awesome_theme/static/css/awesome_control_panel.scss',
            'awesome_theme/static/css/awesome_footer.scss',
            'awesome_theme/static/css/awesome_kanban.scss',
            'awesome_theme/static/css/awesome_setting.scss',
            'awesome_theme/static/css/awesome_search_panel.scss',
            'awesome_theme/static/css/awesome_misc.scss',
            'awesome_theme/static/css/awesome_accordion.scss',
            'awesome_theme/static/css/awesome_rtl.scss',
            'awesome_theme/static/css/awesome_dialog_effect.scss',
            'awesome_theme/static/css/awesome_owl_dialog_effect.scss',
            'awesome_theme/static/css/awesome_search_view.scss',

            'awesome_theme/static/lib/jquery.fullscreen.js',
            'awesome_theme/static/lib/perfect-scrollbar.min.js',

            'awesome_theme/static/src/components/overlay/awesome_overlay.js',
            'awesome_theme/static/src/components/overlay/awesome_overlay_service.js',
            'awesome_theme/static/src/components/sidebar_menu/awesome_sidebar_app_item.js',
            'awesome_theme/static/src/components/sidebar_menu/awesome_sidebar_tab_pane.js',
            'awesome_theme/static/src/components/sidebar_menu/awesome_sidebar_menu.js',
            'awesome_theme/static/src/components/header/awesome_header.js',
            'awesome_theme/static/src/components/user_profile/user_profile.js',
            'awesome_theme/static/src/components/app_board/awesome_app_board.js',
            'awesome_theme/static/src/components/app_board/awesome_app_board_service.js',
            'awesome_theme/static/src/components/full_screen/awesome_full_screen.js',
            'awesome_theme/static/src/components/footer/awesome_footer.js',
            'awesome_theme/static/src/components/accordion/awesome_accordion.js',

            'awesome_theme/static/src/awesome_search_panel.js',
            'awesome_theme/static/src/awesome_action_container.js',
            'awesome_theme/static/src/awesome_switch_company.js',
            'awesome_theme/static/src/awesome_list_controller.js',
            'awesome_theme/static/src/awesome_owl_dialog.js',
            'awesome_theme/static/src/awesome_list_render.js',
            'awesome_theme/static/src/awesome_abstract_view.js',
            'awesome_theme/static/src/awesome_view_dialog.js',
            'awesome_theme/static/src/awesome_abstract_controller.js',

            'awesome_theme/static/js/awesome_many2one.js',
            'awesome_theme/static/js/awesome_datetime_picker.js',
            'awesome_theme/static/js/awesome_selection.js',
            'awesome_theme/static/js/awesome_legacy_control_panel.js',
            'awesome_theme/static/js/awesome_basic_controller.js',
            'awesome_theme/static/js/awesome_search_options.js',
            'awesome_theme/static/js/awesome_relation_fields.js',
            'awesome_theme/static/js/awesome_form_render.js',
            'awesome_theme/static/js/awesome_action_menu.js',
            'awesome_theme/static/js/awesome_dialog_extend.js',

            'awesome_theme/static/src/webclient.js'
        ],

        'web.assets_qweb': [

            'awesome_theme/static/xml/awesome_webclient.xml',
            'awesome_theme/static/xml/awesome_many2one.xml',
            'awesome_theme/static/xml/awesome_selection.xml',
            'awesome_theme/static/xml/awesome_control_pannel.xml',
            'awesome_theme/static/xml/awesome_legacy_control_panel.xml',
            'awesome_theme/static/xml/awesome_pager.xml',
            'awesome_theme/static/xml/awesome_search_panel.xml',
            'awesome_theme/static/xml/awesome_custom_filter_item.xml',
            'awesome_theme/static/xml/awesome_custom_group_by_item.xml',
            'awesome_theme/static/xml/awesome_custom_favorite_item.xml',
            'awesome_theme/static/xml/awesome_misc.xml',
            'awesome_theme/static/xml/awsome_status_button.xml',
            'awesome_theme/static/xml/awesome_action_menu.xml',
            'awesome_theme/static/xml/awesome_owl_dialog.xml',

            'awesome_theme/static/xml/awesome_groupby_menu.xml',
            'awesome_theme/static/xml/awesome_filter_menu.xml',
            'awesome_theme/static/xml/awesome_comparision_menu.xml',
            'awesome_theme/static/xml/awesome_favorite_menu.xml',

            'awesome_theme/static/src/components/sidebar_menu/awesome_sidebar_menu.xml',
            'awesome_theme/static/src/components/header/awesome_header.xml',
            'awesome_theme/static/src/components/app_board/awesome_app_board.xml',
            'awesome_theme/static/src/components/full_screen/awesome_full_screen.xml',
            'awesome_theme/static/src/components/footer/awesome_footer.xml',
            'awesome_theme/static/src/components/accordion/awesome_accordion.xml'
        ],

        'web.assets_backend_prod_only': [
            ('replace', 'web/static/src/main.js', 'awesome_theme/static/src/main.js'),
        ]
    }
}

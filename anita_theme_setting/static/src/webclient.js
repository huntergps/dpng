/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from '@web/webclient/webclient';
import ThemeSetting from 'anita_theme_setting.theme_setting';


patch(WebClient.prototype, "anita_theme_setting_webclient", {

    mounted() {
        this._super.apply(this, arguments);
        this.update_setting();
    },

    /**
     * set the user setting
     */
    update_setting: function () {

        // update the style txt 
        this._update_style();

        // set the app nme
        var settings = ThemeSetting.settings
        if (!settings.show_app_name) {
            $('body').addClass('hide_awesome_app_name')
        }

        // set the layout mode
        var layout_mode = settings.layout_mode
        if (layout_mode) {
            $('body').addClass(layout_mode)
        }

        // set the button style
        var button_style = settings.button_style
        if (button_style) {
            $('body').addClass(button_style)
        }

        // set theme menu mode from local storage
        var awesome_menu_mode = localStorage.getItem('awesome_menu_mode')
        if (awesome_menu_mode) {
            $('body').removeClass('navigation-toggle-two');
            $('body').removeClass('navigation-toggle-one');
            $('body').removeClass('navigation-toggle-none');
            $('body').addClass(awesome_menu_mode);
        }

        //  set current theme mode
        if (ThemeSetting) {
            var cur_mode_id = ThemeSetting.cur_mode_id
            var theme_modes = ThemeSetting.theme_modes
            var cur_mode = _.find(theme_modes, function (theme_mode) {
                return theme_mode.id == cur_mode_id;
            })
            _.each(theme_modes, function (tmp_mode) {
                $('body').removeClass(tmp_mode.name)
            })
            $('body').addClass(cur_mode.name)
        }

        // set the rtl mode
        if (settings.rtl_mode) {
            $('body').addClass('rtl_mode')
        }
    },

    /**
     * update the style txt
     */
    _update_style: function () {
        var $body = $('body')
        if (ThemeSetting.style_txt) {
            var style_id = 'anita_style_id';
            var styleText =ThemeSetting.style_txt
            var style = document.getElementById(style_id);
            if (style.styleSheet) {
                style.setAttribute('type', 'text/css');
                style.styleSheet.cssText = styleText;
            } else {
                style.innerHTML = styleText;
            }
            style && $body[0].removeChild(style);
            $body[0].appendChild(style);
        }

        if (ThemeSetting.mode_style_css) {
            var style_id = 'anita_mode_style_id';
            var styleText = ThemeSetting.mode_style_css
            var style = document.getElementById(style_id);
            if (style.styleSheet) {
                style.setAttribute('type', 'text/css');
                style.styleSheet.cssText = styleText;
            } else {
                style.innerHTML = styleText;
            }
            style && $body[0].removeChild(style);
            $body[0].appendChild(style);
        }
    }
});

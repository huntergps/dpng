
odoo.define('awesome_theme.form_render', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var FormRenderer = require('web.FormRenderer')

    // form header button
    FormRenderer.include({
        _renderHeaderButtons: function () {
            const $buttons = this._super.apply(this, arguments);
            if (!config.device.isMobile ||
                !$buttons.is(":has(>:not(.o_invisible_modifier))")
            ) {
                return $buttons;
            }

            $buttons.addClass("dropdown-menu");
            const $dropdown = $(core.qweb.render("awesome_theme.MenuStatusbarButtons"));
            $buttons.addClass("dropdown-menu").appendTo($dropdown);
            return $dropdown;
        }
    });
})

odoo.define('awesome_theme.ActionMenus', function (require) {
    "use strict";

    const ActionMenu = require('web.ActionMenus')
    var config = require('web.config')

    const { hooks} = owl;
    const { useState } = hooks;
    const { patch } = require("web.utils");
    

    patch(ActionMenu.prototype, "awesome_theme_action_menu", {
        setup() {
            this._super.apply(this, arguments);

            this.state = useState({
                "isMobile": config.device.isMobile,
            })
    
            config.device.bus.on('size_changed', this, () => {
                if (config.device.isMobile) {
                    this.state.isMobile = true;
                } else {
                    this.state.isMobile = false;
                }
            });
        }
    })
})
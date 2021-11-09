odoo.define('awesome_theme.BasicController', function (require) {
    "use strict";

    var core = require('web.core');
    var BasicController = require('web.BasicController')

    var _t = core._t;

    BasicController.include({

        start: async function () {
            await this._super(...arguments);
            core.bus.on("ACTION_MANAGER:UPDATE", this, (info) => {
                if (this.withControlPanel) {
                    var props = this._controlPanelWrapper.props;
                    props.isActive = false
                    this._controlPanelWrapper.update(props)
                }
            });
        },


        /**
         * @override
         */
        on_attach_callback: function () {
            if (this.withControlPanel) {
                var props = this._controlPanelWrapper.props;
                props.isActive = true
                this._controlPanelWrapper.update(props)
            }
            this._super(...arguments);
        },

        /**
         * @override
         */
        on_detach_callback: function () {
            this._super(...arguments);
        }
    })
});

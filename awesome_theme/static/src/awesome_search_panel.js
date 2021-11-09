/** @odoo-module **/

import SearchPanel from "@web/legacy/js/views/search_panel";
import {patch} from "@web/core/utils/patch";
import config from 'web.config';


patch(SearchPanel.prototype, "awesome_theme_search_panel", {

    setup() {
        this._super.apply(this, arguments);

        // check if it is mobile device
        if (config.device.isMobile) {
            this.state.isMobile = true;
            this.state.pannel_expanded = false;
        } else {
            this.state.isMobile = false;
            this.state.pannel_expanded = true;
        }

        config.device.bus.on('size_changed', this, () => {
            if (config.device.isMobile) {
                this.state.isMobile = true;
                // close autoly
                this.state.pannel_expanded = false;
            } else {
                this.state.isMobile = false;
            }
        });
    },
    
    on_toggler_click() {
        this.state.pannel_expanded = !this.state.pannel_expanded;
    }
});


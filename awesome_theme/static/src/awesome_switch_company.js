/** @odoo-module **/

import {SwitchCompanyMenu} from "@web/webclient/switch_company_menu/switch_company_menu";
import {patch} from "@web/core/utils/patch";
import config from 'web.config';


patch(SwitchCompanyMenu.prototype, "awesome_theme_swtich_compnay", {

    setup() {
        this._super.apply(this, arguments);
        
        config.device.bus.on('size_changed', this, () => {
            this.render()
        });
    }
});

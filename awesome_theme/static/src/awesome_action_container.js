/** @odoo-module **/

import {ActionContainer} from "@web/webclient/actions/action_container";
import {patch} from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import core from "web.core";


patch(ActionContainer.prototype, "awesome_theme_action_container", {
    setup() {
        this.info = {};
        this.action_service = useService('action')
        this.env.bus.on("ACTION_MANAGER:UPDATE", this, (info) => {
            core.bus.trigger('ACTION_MANAGER:UPDATE');
            this.info = info;
            this.render();
        });
    }
});


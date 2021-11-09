/** @odoo-module **/

const { Component, hooks} = owl;
const { useState } = hooks;
import { useService } from "@web/core/utils/hooks";


export class SideBarAppItem extends Component {

    setup() {
        this.menuService = useService("menu");
        this.state = useState({
            active: false
        })
    }

    mounted() {
        this.env.bus.on("MENUS:APP-CHANGED", this, this.on_app_changed);
    }

    willUnmount() {
        this.env.bus.off("MENUS:APP-CHANGED", this);
    }

    on_app_changed() {
        
        // current app
        var current_app = this.menuService.getCurrentApp();

        // get the first app
        var first_app = current_app;
        while (first_app.parent) {
            first_app = first_app.parent;
            first_app.open = true
        }

        if (first_app.id == this.app.id) {
            this.state.active = true;
        } else {
            this.state.active = false;
        }
    }

    getMenuItemHref() {
        const parts = [`menu_id=${this.app.id}`];
        if (this.app.action) {
            parts.push(`action=${this.app.action.split(",")[1]}`);
        }
        return "#" + parts.join("&");
    }

    get app() {
        return this.props.app;
    }

    click_app_item(event) {
        this.state.active = true;
        let $target = $(event.currentTarget);
        let $slibings = $target.siblings();
        $slibings.removeClass('active');
        this.menuService.selectMenu(this.app);
    }
}

SideBarAppItem.props = {
    app: {
        type: Object
    }
};

SideBarAppItem.template = "awesome_theme.sidebar_app_item";

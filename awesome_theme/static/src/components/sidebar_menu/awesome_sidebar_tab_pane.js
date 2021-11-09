/** @odoo-module **/

const { Component, hooks } = owl;
import { useService, useEffect } from "@web/core/utils/hooks";
const { useState } = hooks;


export class AppTabPane extends Component {

    setup() {
        this.menuService = useService("menu");
        this.router = useService("router");
        this.state = useState({ active: false, current_action: false });
        this.action_data = {}

        useEffect(
            () => {
                Promise.resolve().then(() => {
                    let menu_container =  this.el.querySelector('.menu_container')
                    let ps = new PerfectScrollbar(menu_container);
                    return () => {
                        ps.destroy();
                        ps = null;
                    }
                });
            },
            () => []
        );


        let self = this;
        function post_deal_app_data(app) {
            if (app.actionID) {
                self.action_data[app.actionID] = app
            }
            if (app.childrenTree) {
                _.each(app.childrenTree, (child) => {
                    if (child.childrenTree) {
                        post_deal_app_data(child)
                    } else {
                        if (child.actionID) {
                            self.action_data[child.actionID] = child
                        }
                    }
                })
            }
        }
        post_deal_app_data(this.props.app);
    }
    

    mounted() {
        this.env.bus.on("MENUS:APP-CHANGED", this, this.on_app_changed);
    }

    willUnmount() {
        this.env.bus.off("MENUS:APP-CHANGED", this);
    }

    get app() {
        return this.props.app;
    }

    on_app_changed() {

        // current app
        var current_app = this.menuService.getCurrentApp();

        if (!current_app.childrenTree || current_app.childrenTree.length == 0) {
            $('body').addClass('not_have_child');
            return
        } else {
            $('body').removeClass('not_have_child');
        }

        // get the first app
        var first_app = current_app;
        while (first_app.parent) {
            first_app = first_app.parent;
            first_app.open = true;
        }

        if (first_app.id == this.app.id) {
            this.state.active = true;
        } else {
            this.state.active = false;
        }

        // select the sub menu
        let actionId = Number(this.router.current.hash.action || undefined);
        if (this.action_data[actionId]) {
            this.state.current_action = actionId;
            let menu_data = this.action_data[actionId]
            let parent = menu_data.parent
            while (parent) {
                parent.open = true;
                parent = parent.parent;
            }
        } else {
            this.state.current_action = false;
        }
    }

    get app() {
        return this.props.app;
    }

    get children() {
        return this.app.childrenTree;
    }

    getMenuItemHref(app) {
        const parts = [`menu_id=${app.id}`];
        if (app.action) {
            parts.push(`action=${app.action.split(",")[1]}`);
        }
        return "#" + parts.join("&");
    }

    click_menu_item(menu) {
        if (!menu.childrenTree || menu.childrenTree.length == 0) {
            this.state.current_action = menu.actionID
        }
        this.menuService.selectMenu(menu);
    }

    toggle_sub_menu(menu, event) {
        // inverse the state
        let $target = $(event.currentTarget)
        let $ul = $target.next("ul").toggle(200)
        if ($ul.length) {
            let $arrow = $target.find('.sub-menu-arrow')
            if (menu.open) {
                $arrow.addClass('rotate-in')
            } else {
                $arrow.removeClass('rotate-in')
            }
        }
        menu.open = !menu.open
    }
}

AppTabPane.props = {
    app: {
        type: Object
    }
};

AppTabPane.template = "awesome_theme.app_tab_pane";

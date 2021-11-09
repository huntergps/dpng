/** @odoo-module **/

const { Component, hooks } = owl;
const { useExternalListener, useState, useRef } = hooks;

import { SideBarAppItem } from "./awesome_sidebar_app_item";
import { AppTabPane } from "./awesome_sidebar_tab_pane";
import { UserProfile } from "../user_profile/user_profile";

import { useService } from "@web/core/utils/hooks";
import { bus, _t } from 'web.core';


export class SideBarMenu extends Component {

    setup() {
        
        this.currentAppSectionsExtra = [];

        this.actionService = useService("action");
        this.menuService = useService("menu");
        this.appboardService = useService("awesome_app_board");
        this.appTabPanes = useRef("appSubMenus");
        this.menu_data = {}

        // init the app data, add is_open to overserve it, 
        // colone the info to avoid change the origin data
        var self = this;
        function post_deal_app_data(app) {
            self.menu_data[app.id] = app
            if (app.childrenTree) {
                _.each(app.childrenTree, (child) => {
                    child.is_open = false;
                    child.parent = app;
                    if (child.childrenTree) {
                        post_deal_app_data(child)
                    } else {
                        self.menu_data[child.id] = child
                    }
                })
            }
        }

        // add the active app
        var apps = this.menuService.getApps();
        apps.map((app) => {
            app.active = false;
            app.childrenTree = this.menuService.getMenuAsTree(app.id).childrenTree
            post_deal_app_data(app)
        })

        // get all menus
        this.state = useState({ apps });
    }

    mounted() {
        this._addTooltips();
    }

    patched() {
        this._addTooltips();
    }

    willUnmount() {
        this.env.bus.off("MENUS:APP-CHANGED", this);
    }
    
    /**
     * Add the tooltips to the items
     * @private
     */
    _addTooltips() {
        $(this.el.querySelectorAll('[title]')).tooltip({
            delay: { show: 500, hide: 0 }
        });
    }

    _isBoardVisible() {
        let $app_board = $(document.querySelector('.awesome_app_board'))
        return !$app_board.hasClass('d-none')
    }

    on_app_board_toggler_click() {
        if (!this._isBoardVisible()) {
            this.appboardService.show();
        } else {
            this.appboardService.hide();
        }
    }
}

SideBarMenu.components = { SideBarAppItem, AppTabPane, UserProfile };
SideBarMenu.props = {};
SideBarMenu.template = 'awesome_theme.sidebar_menu';

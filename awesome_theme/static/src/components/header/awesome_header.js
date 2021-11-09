/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ErrorHandler, NotUpdatable } from "@web/core/utils/components";
import config from 'web.config';
import { session } from '@web/session'

const { Component, hooks } = owl;
const systrayRegistry = registry.category("systray");
import { useService } from "@web/core/utils/hooks";
const { useExternalListener, useState, useRef } = hooks;


export class AwesomeHeader extends Component {

    setup() {
        this.userService = useService('user')
        this.overlayService = useService("awesome_overlay");

        let company = session.company_id;

        config.device.bus.on('size_changed', this, () => {
            if (config.device.isMobile) {
                if ($('body').hasClass('navigation-show')) {
                    this.overlayService.show()
                }
            } else {
                this.overlayService.hide()
            }
        });

        // if click outside the panel close it
        useExternalListener(window, 'click', (event) => {
            if ($('body').hasClass("navigation-show")) {
                if (!$(event.target).is($(".sidebar_menu, .sidebar_menu *, .navigation-toggler *"))) {
                    this.overlayService.hide()
                    $('body').removeClass("navigation-show");
                }
            }
        });

        this.state = useState({
            logo_url: '/web/binary/company_logo' + '?db=' + session.db + (company ? '&company=' + company : ''),
        })
    }

    handleItemError(error, item) {
        // remove the faulty component
        item.isDisplayed = () => false;
        Promise.resolve().then(() => {
            throw error;
        });
    }

    get systrayItems() {
        return systrayRegistry
            .getAll()
            .filter((item) => ("isDisplayed" in item ? item.isDisplayed(this.env) : true))
            .reverse();
    }

    on_logo_click() {
        let self = this;
        
        this.rpc('/web/action/load', { action_id: 'base.action_res_company_form' }).then(function (result) {
            result.res_id = session.company_id;
            result.target = "new";
            result.views = [[false, 'form']];
            // result.context = '{"form_view_ref": "awesome_theme_pro.awesome_view_company_pop_form"}'
            result.flags = {
                action_buttons: true,
                headless: true,
            };
            self.trigger('do-action', {
                action: result,
                options: {
                    on_close: () => {
                        self.update_logo.bind(self, true)()
                    }
                }
            });
        });
    }

    get logo_url() {
        return '/web/binary/company_logo' + '?db=' + session.db + (company ? '&company=' + session.user_context.current_company : '')
    }

    update_logo(reload) {
        let company = session.company_id
        this.state.logo_url = '/web/binary/company_logo' + '?db=' + session.db + (company ?
            '&company=' + session.user_context.current_company : '') + moment().format('x')
    }

    on_toggler_click() {

        let $body = $('body');

        // create overlay when the size is below 1200
        if (config.device.isMobile) {
            $body.addClass("navigation-show");
            this.overlayService.show()
        } else {
            this.overlayService.hide()
            if ($body.hasClass("navigation-toggle-one")) {
                $body.removeClass("navigation-toggle-one");
                $body.removeClass("navigation-show");
                $body.addClass("navigation-toggle-none");
                localStorage.setItem('awesome_menu_mode', 'navigation-toggle-none')
            } else if ($body.hasClass("navigation-toggle-two")) {
                // jump one to none
                if (!$body.hasClass('not_have_child')) {
                    $body.removeClass("navigation-toggle-two");
                    $body.removeClass("navigation-show");
                    $body.addClass("navigation-toggle-one");
                    localStorage.setItem('awesome_menu_mode', 'navigation-toggle-one')
                } else {
                    $body.removeClass("navigation-toggle-two");
                    $body.removeClass("navigation-show");
                    $body.addClass("navigation-toggle-none");
                    localStorage.setItem('awesome_menu_mode', 'navigation-toggle-one')
                }
            } else if ($body.hasClass("navigation-toggle-none")) {
                $body.removeClass("navigation-toggle-none");
                $body.removeClass("navigation-show");
                $body.addClass("navigation-toggle-two");
                localStorage.setItem('awesome_menu_mode', 'navigation-toggle-two')
            } else {
                // if nothing
                $body.removeClass("navigation-toggle-two");
                $body.removeClass("navigation-show");
                $body.addClass("navigation-toggle-one");
                localStorage.setItem('awesome_menu_mode', 'navigation-toggle-one')
            }
        }
    }
}

AwesomeHeader.template = "awesome_theme.header";
AwesomeHeader.components = { NotUpdatable, ErrorHandler };

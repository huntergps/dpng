odoo.define('awesome_theme.ControlPanel', function (require) {
    "use strict";

    const ControlPanel = require('web.ControlPanel')
    const { patch } = require("web.utils");
    const config = require('web.config')
    const search_options = require('awesome_theme.search_options')

    const AwesomeFilterMenu = search_options.AwesomeFilterMenu
    const AwesomeGroupMenu = search_options.AwesomeGroupMenu
    const AwesomeFavoriteMenu = search_options.AwesomeFavoriteMenu
    const AwesomeComparisonMenu = search_options.AwesomeComparisonMenu

    const { misc, hooks} = owl;
    const { Portal } = misc;
    const { useState } = hooks;
    const { useExternalListener, useRef } = hooks;

    patch(ControlPanel.prototype, "awesome_theme_control_panel", {

        setup() {
            this._super.apply(this, arguments);
    
            // check if it is mobile device
            let isMobile = false;
            if (config.device.isMobile) {
                isMobile = true;
            } else {
                isMobile = false;
            }

            this.state = useState({
                "isMobile": isMobile,
                "mobile_search_bar_visible": false
            })
    
            config.device.bus.on('size_changed', this, () => {
                if (config.device.isMobile) {
                    this.state.isMobile = true;
                } else {
                    this.state.isMobile = false;
                }
            });

            this.optionDropDown = useRef('optionDropDown');
            this.mobileOptionDropDown = useRef('mobileOptionDropDown');

            useExternalListener(window, 'click', this._hideOptions);
        },

        get_active_view_icon(env) {
            var activeView = _.findWhere(this.props.views, { type: env.view.type });
            return activeView.icon
        },

        _OptionDropdownToggleClick(event) {
            this.optionDropDown.el.classList.add('show');
        },

        _MobileOptionDropdownToggleClick(event) {
            this.mobileOptionDropDown.el.classList.add('show');
        },

        _hideOptions(event) {
            if (this.state.isMobile) {
                if (!this.mobileOptionDropDown.el) {
                    return
                }
            } else {
                if (!this.optionDropDown.el) {
                    return
                }
            }

            // check if it need to hide the option
            if (!$(event.target).is(
                $(".awesome_search_option_dropdown, .awesome_search_option_dropdown *, .search_option_dropdown_toggler"))) 
            {
                if (this.state.isMobile) {
                    this.mobileOptionDropDown.el.classList.remove('show');
                } else {
                    this.optionDropDown.el.classList.remove('show');
                }
            }
        },

        on_mobile_search_bar_toggle_click() {
            this.state.mobile_search_bar_visible = !this.state.mobile_search_bar_visible;
        }
    });

    ControlPanel.defaultProps = {
        ...ControlPanel.defaultProps,
        isActive: true,
        isInDialog: false
    }

    ControlPanel.props = {...ControlPanel.props, isActive: Boolean, isInDialog: Boolean}
    ControlPanel.components = {...ControlPanel.components, Portal, AwesomeFilterMenu, AwesomeGroupMenu, AwesomeFavoriteMenu, AwesomeComparisonMenu}
});

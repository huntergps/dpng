/** @odoo-module **/

import { AwesomeFullScreen } from '../full_screen/awesome_full_screen';
import config from 'web.config';

const { Component, hooks } = owl;
const { useState } = hooks;


export class AwesomeFooter extends Component {

    setup() {
        super.setup();
        this.state = useState({ 
            isMobile: config.device.isMobile? true : false 
        });
        config.device.bus.on('size_changed', this, this._onDeviceSizeChanged);
    }

    _onDeviceSizeChanged() {
        this.state.isMobile = config.device.isMobile? true : false
    }
}

AwesomeFooter.components = {
    AwesomeFullScreen
};

AwesomeFooter.defaultProps = {};
AwesomeFooter.props = {};
AwesomeFooter.template = 'awesome_theme.footer';

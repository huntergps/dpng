/** @odoo-module **/

const { Component, hooks } = owl;
const { useState } = hooks;

export class AwesomeFullScreen extends Component {

    constructor() {
        super(...arguments);

        this.state = useState({
            maxized: false,
        });

        $(document).bind("fullscreenchange", () => {
            this.state.maxized = $(document).fullScreen();
        });
    }

    _toggle_full_screen() {
        if (!this.state.maxized) {
            this.state.maxized = true;
            $(document).fullScreen(true);
        } else {
            this.state.maxized = false;
            $(document).fullScreen(false);
        }
    }
}

AwesomeFullScreen.template = 'awesome_theme.full_screen';

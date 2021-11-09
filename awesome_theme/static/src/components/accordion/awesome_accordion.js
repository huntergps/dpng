/** @odoo-module **/


const { Component, hooks, QWeb } = owl;
const { useState } = hooks;


export class AwesomeAccordion extends Component {

    setup() {
        this.state = useState({
            'collapse': true
        })
    }

    toggleDisplay() {
        this.state.collapse = !this.state.collapse;
    }
}

AwesomeAccordion.props = {
    title: {
        type: String
    }
};
AwesomeAccordion.template = "awesome_theme.accordion";
AwesomeAccordion.components = {};

QWeb.registerComponent("AwesomeAccordion", AwesomeAccordion);

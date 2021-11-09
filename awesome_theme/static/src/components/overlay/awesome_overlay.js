/** @odoo-module **/

const { Component, tags } = owl;
const { useState } = owl.hooks;


export class AwesomeOverlay extends Component {

    setup() {

        this.state = useState({
            active: false,
            zIndex: 100
        })

        this.props.bus.on("Show", this, (zIndex) => {
            this.state.active = true
            if (zIndex) {
                this.state.zIndex = zIndex
            }
        });

        this.props.bus.on("Hide", this, () => {
            this.state.active = false
        });
    }
}

AwesomeOverlay.components = {};
AwesomeOverlay.template = tags.xml`<div class="awesome_overlay" t-att-class="{'d-none': !state.active}" t-attf-style="z-index: {{state.zIndex}}"></div>`;

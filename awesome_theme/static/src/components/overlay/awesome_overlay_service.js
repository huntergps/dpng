/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AwesomeOverlay } from "./awesome_overlay";

const { core } = owl;
const { EventBus } = core;


export const AwesomeOverlayService = {

    start() {
        const bus = new EventBus();

        registry.category("main_components").add("Overlay", {
            Component: AwesomeOverlay,
            props: { bus },
        });

        function show(zIndex) {
            bus.trigger("Show", {
                zIndex: zIndex
            });
        }

        function hide() {
            bus.trigger("Hide");
        }

        return {
            show,
            hide
        }
    }
};

registry.category("services").add("awesome_overlay", AwesomeOverlayService);

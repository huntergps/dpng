/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AppBoard } from "./awesome_app_board";

const { core } = owl;
const { EventBus } = core;


export const AwesomeAppboardService = {
    dependencies: ["menu"],

    start() {
        const bus = new EventBus();
        registry.category("main_components").add("AwesomeAppBoard", {
            Component: AppBoard,
            props: {
                bus: bus
            },
        });

        return {
            show: () => {
                bus.trigger("ShowAppBoard");
            },

            hide: () => {
                bus.trigger("HideAppBoard");
            }
        }
    }
};

registry.category("services").add("awesome_app_board", AwesomeAppboardService);

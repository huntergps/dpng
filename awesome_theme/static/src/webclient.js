/** @odoo-module **/

import { SideBarMenu } from "./components/sidebar_menu/awesome_sidebar_menu";
import { AwesomeHeader } from "./components/header/awesome_header";
import { AwesomeFooter } from "./components/footer/awesome_footer";
import { WebClient }  from '@web/webclient/webclient';


export class AnitaWebClient extends WebClient {}

AnitaWebClient.components = {
    ...WebClient.components,
    SideBarMenu,
    AwesomeFooter,
    AwesomeHeader
};

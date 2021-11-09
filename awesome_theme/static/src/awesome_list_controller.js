/** @odoo-module alias=awesome_theme.list_controller **/

/**
 * The List Controller controls the list renderer and the list model.  Its role
 * is to allow these two components to communicate properly, and also, to render
 * and bind all extra buttons/pager in the control panel.
 */

 import config from 'web.config';
 import core from 'web.core';
 import ListController from 'web.ListController';
 
 var _t = core._t;
 var qweb = core.qweb;
 
ListController.include({
    _updateSelectionBox() {
        this._renderHeaderButtons();
        if (this.$selectionBox) {
            this.$selectionBox.remove();
            this.$selectionBox = null;
        }
        if (this.selectedRecords.length) {
            const state = this.model.get(this.handle, {raw: true});
            this.$selectionBox = $(qweb.render('ListView.selection', {
                isDomainSelected: this.isDomainSelected,
                isMobile: config.device.isMobile,
                isPageSelected: this.isPageSelected,
                nbSelected: this.selectedRecords.length,
                nbTotal: state.count,
            }));
            if (config.device.isMobile ) {
                this.$selectionBox.prependTo(this.$buttons);
             } else {
                this.$selectionBox.appendTo(this.$buttons);
             }
        }
    }
 });
 
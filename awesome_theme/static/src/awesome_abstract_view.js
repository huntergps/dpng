/** @odoo-module alias=awesome_theme.AbstractView **/

 import AbstractView from 'web.AbstractView'

 AbstractView.include({
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        this.controllerParams.isInDialog = params.isInDialog || false;
    }
 })

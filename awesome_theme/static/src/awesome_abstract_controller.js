/** @odoo-module alias=awesome_theme.AbstractController **/

 import AbstractController from 'web.AbstractController'


 AbstractController.include({

    init(parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this.inputParams = params;
    },
     /**
      * extend to add if it is in dialog
      * @param {*} state 
      * @returns 
      */
    _updateControlPanelProps(state) {
        this.controlPanelProps.isInDialog = this.inputParams.isInDialog || false
        return this._super.apply(this, arguments);
    }
 })

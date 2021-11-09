/** @odoo-module alias=awesome_theme.view_dialogs **/

import config from 'web.config';
import core from 'web.core';
import Dialog from 'web.Dialog';
import dom from 'web.dom';
import view_registry from 'web.view_registry';
import select_create_controllers_registry from 'web.select_create_controllers_registry';
import view_dialogs from 'web.view_dialogs'

const SelectCreateDialog = view_dialogs.SelectCreateDialog

var _t = core._t;

SelectCreateDialog.include({
    /**
     * rewrite the set the view is in dialog
     * @param {*} fieldsViews 
     * @returns 
     */
    setup: function (fieldsViews) {
        var self = this;
        var fragment = document.createDocumentFragment();

        var domain = this.domain;
        if (this.initialIDs) {
            domain = domain.concat([['id', 'in', this.initialIDs]]);
        }
        var ViewClass = view_registry.get(this.viewType);
        var viewOptions = {
            isInDialog: true
        };
        var selectCreateController;
        if (this.viewType === 'list') { // add listview specific options
            _.extend(viewOptions, {
                hasSelectors: !this.options.disable_multiple_selection,
                readonly: true,

            }, this.options.list_view_options);
            selectCreateController = select_create_controllers_registry.SelectCreateListController;
        }
        if (this.viewType === 'kanban') {
            _.extend(viewOptions, {
                noDefaultGroupby: true,
                selectionMode: this.options.selectionMode || false,
            });
            selectCreateController = select_create_controllers_registry.SelectCreateKanbanController;
        }
        var view = new ViewClass(fieldsViews[this.viewType], _.extend(viewOptions, {
            action: {
                controlPanelFieldsView: fieldsViews.search,
                help: _.str.sprintf("<p>%s</p>", _t("No records found!")),
            },
            action_buttons: false,
            dynamicFilters: this.options.dynamicFilters,
            context: this.context,
            domain: domain,
            modelName: this.res_model,
            withBreadcrumbs: false,
            withSearchPanel: false,
        }));
        view.setController(selectCreateController);
        return view.getController(this).then(function (controller) {
            self.viewController = controller;
            // render the footer buttons
            self._prepareButtons();
            return self.viewController.appendTo(fragment);
        }).then(function () {
            return fragment;
        });
    },
})

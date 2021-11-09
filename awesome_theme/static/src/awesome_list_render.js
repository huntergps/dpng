/** @odoo-module alias=awesome_theme.ListRenderer **/

import listRender from 'web.ListRenderer'


listRender.include({
    /**
     * Main render function for the list.  It is rendered as a table. For now,
     * this method does not wait for the field widgets to be ready.
     *
     * @override
     * @returns {Promise} resolved when the view has been rendered
     */
     async _renderView() {
        const oldPagers = this.pagers;
        let prom;
        let tableWrapper;
        if (this.state.count > 0 || !this.noContentHelp) {
            // render a table if there are records, or if there is no no content
            // helper (empty table in this case)
            this.pagers = [];

            const orderedBy = this.state.orderedBy;
            this.hasHandle = orderedBy.length === 0 || orderedBy[0].name === this.handleField;
            this._computeAggregates();

            const $table = $(
                '<table class="o_list_table table table-sm table-hover table-striped"/>'
            );
            $table.toggleClass('o_list_table_grouped', this.isGrouped);
            $table.toggleClass('o_list_table_ungrouped', !this.isGrouped);
            const defs = [];
            this.defs = defs;
            if (this.isGrouped) {
                $table.append(this._renderHeader());
                $table.append(this._renderGroups(this.state.data));
                $table.append(this._renderFooter());

            } else {
                $table.append(this._renderHeader());
                $table.append(this._renderBody());
                $table.append(this._renderFooter());
            }
            tableWrapper = Object.assign(document.createElement('div'), {
                className: 'table-responsive',
            });
            tableWrapper.appendChild($table[0]);
            delete this.defs;
            prom = Promise.all(defs);
        }

        await Promise.all([this._super.apply(this, arguments), prom]);

        this.el.innerHTML = "";
        this.el.classList.remove('o_list_optional_columns');

        // destroy the previously instantiated pagers, if any
        oldPagers.forEach(pager => pager.destroy());

        // append the table (if any) to the main element
        if (tableWrapper) {
            this.el.appendChild(tableWrapper);
            if (document.body.contains(this.el)) {
                this.pagers.forEach(pager => pager.on_attach_callback());
            }
            if (this._shouldRenderOptionalColumnsDropdown()) {
                this.el.classList.add('o_list_optional_columns');
                this.$('table > thead > tr').append(
                    $('<i class="o_optional_columns_dropdown_toggle fa fa-ellipsis-v"/>')
                );
                this.$el.append(this._renderOptionalColumnsDropdown());
            }
            if (this.selection.length) {
                const $checked_rows = this.$('tr').filter(
                    (i, el) => this.selection.includes(el.dataset.id)
                );
                $checked_rows.find('.o_list_record_selector input').prop('checked', true);
                if ($checked_rows.length === this.$('.o_data_row').length) { // all rows are checked
                    this.$('thead .o_list_record_selector input').prop('checked', true);
                }
            }
        }

        // display the no content helper if necessary
        if (!this._hasContent() && !!this.noContentHelp) {
            this._renderNoContentHelper();
        }
    }
})


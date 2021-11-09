odoo.define("awesome_theme.relational_fields", function (require) {
    "use strict";

    var config = require('web.config')
    var RelationalFields = require('web.relational_fields')
    var core = require('web.core')
    let qweb = core.qweb

    // change the mobile status
    RelationalFields.FieldStatus.include({

        start: function () {
            this._super.apply(this, arguments);
            // render the element again
            config.device.bus.on('size_changed', this, () => {
                this.renderElement();
            });
        },

        _render: function () {
            var selections = _.partition(this.status_information, function (info) {
                return (info.selected || !info.fold);
            });
            if (config.device.isMobile) {
                this.$el.html(qweb.render("awesome_theme.FieldStatus.mobile", {
                    selection_unfolded: selections[0],
                    selection_folded: selections[1],
                    clickable: this.isClickable,
                }));
            } else {
                this.$el.html(qweb.render("FieldStatus.content", {
                    selection_unfolded: selections[0],
                    selection_folded: selections[1],
                    clickable: this.isClickable,
                }));
            }
        },
    });
})

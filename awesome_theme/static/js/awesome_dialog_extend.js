odoo.define('awesome_theme.dialog_extend', function (require) {
    "use strict";

    var core = require('web.core');
    const OwlDialog = require('web.OwlDialog');
    const Dialog = require('web.Dialog')
    var ThemeSetting = require('anita_theme_setting.theme_setting')

    Dialog.include({
        open: function (options) {
            var pop_style = ThemeSetting.settings.dialog_pop_style
            if (!ThemeSetting.settings.dialog_pop_style) {
                return this._super.apply(this, arguments)
            } else {
                $('.tooltip').remove(); // remove open tooltip if any to prevent them staying when modal is opened

                var self = this;
                // add a popup style
                this.appendTo($('<div/>')).then(function () {

                    if (self.isDestroyed()) {
                        return;
                    }
                    // add the pop style
                    self.$modal.addClass(pop_style)

                    self.$modal.find(".modal-body").replaceWith(self.$el);
                    self.$modal.attr('open', true);
                    self.$modal.removeAttr("aria-hidden");
                    if (self.$parentNode) {
                        self.$modal.appendTo(self.$parentNode);
                    }
                    self.$modal.modal({
                        show: true,
                        backdrop: self.backdrop,
                        keyboard: false,
                    });
                    self._openedResolver();
                    if (options && options.shouldFocusButtons) {
                        self._onFocusControlButton();
                    }
                    // Notifies OwlDialog to adjust focus/active properties on owl dialogs
                    OwlDialog.display(self);

                    // Notifies new webclient to adjust UI active element
                    core.bus.trigger("legacy_dialog_opened", self);
                });

                return self;
            }
        }
    });

    return Dialog;
});

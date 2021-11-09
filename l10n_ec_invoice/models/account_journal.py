# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command, _
from odoo.addons.l10n_ec.models.res_partner import verify_final_consumer

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    l10n_ec_sri_payment_id = fields.Many2one('l10n_ec.sri.payment',string="Forma de Pago (SRI)")

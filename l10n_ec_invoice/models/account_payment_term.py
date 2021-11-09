# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    l10n_ec_sri_payment_id = fields.Many2one('l10n_ec.sri.payment',string="Forma de Pago (SRI)")
    is_cash_sale = fields.Boolean(string='Pago en Efectivo')
    unidad_tiempo_sri = fields.Char(string='Unidad de tiempo Reportar al SRI',default='15')
    plazo_sri = fields.Char(string='Plazo a Reportar al SRI', default='Días')

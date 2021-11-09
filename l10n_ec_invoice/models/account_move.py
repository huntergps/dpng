# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command, _
from odoo.addons.l10n_ec.models.res_partner import verify_final_consumer

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import json


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_default_partner_id(self):
        return self.env.ref('l10n_ec.ec_final_consumer') or False

    @api.model
    def _get_default_invoice_date(self):
        return fields.Date.context_today(self)


    debit_lines_ids = fields.One2many('account.partial.reconcile', 'debit_main_id', string='Debitos',copy=False, readonly=True,)
    credit_lines_ids = fields.One2many('account.partial.reconcile', 'credit_main_id', string='Creditos',copy=False, readonly=True,)

    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        default=_get_default_partner_id,
        check_company=True,
        string='Partner', change_default=True)


    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        default=_get_default_invoice_date,
        states={'draft': [('readonly', False)]})

    tipo_compra = fields.Selection([
        ('inventario', 'Inventario'),
        ('gasto', 'Gastos'),
        ('importacion', 'Gastos de Importación')
    ], string='Tipo de Compra', default='inventario')

    invoice_payment_term_ids_domain = fields.Char(compute='_compute_invoice_payment_terms_domain',
        help="Technical field used to have a invoice payments authorized for the current partner")

    suitable_invoice_payment_term_ids = fields.Many2many('account.payment.term', compute='_compute_invoice_payment_terms_domain')

    def _l10n_ec_get_invoice_totals_for_report(self):
        self.ensure_one()
        tax_ids_filter = tax_line_id_filter = None


        tax_lines_data = self._prepare_tax_lines_data_for_totals_from_invoice(
            tax_ids_filter=tax_ids_filter, tax_line_id_filter=tax_line_id_filter)

        amount_untaxed = self.amount_untaxed
        return self._get_tax_totals(self.partner_id, tax_lines_data, self.amount_total, amount_untaxed, self.currency_id)


    @api.depends('partner_id')
    def _compute_invoice_payment_terms_domain(self):
        for move in self:
            payment_methods_list=[]
            pefectivo =  self.env.ref('account.account_payment_term_immediate')
            if move.is_sale_document(include_receipts=True):
                payment_methods_list = move.partner_id.terminos_pagos_ids.ids
                if not pefectivo.id in payment_methods_list:
                    payment_methods_list.append(pefectivo.id)
                move.invoice_payment_term_ids_domain = payment_methods_list
            elif move.is_purchase_document(include_receipts=True):
                payment_methods_list = move.partner_id.terminos_pagos_supplier_ids.ids
                if not pefectivo.id in payment_methods_list:
                    payment_methods_list.append(pefectivo.id)
                move.invoice_payment_term_ids_domain = payment_methods_list
            else:
                move.invoice_payment_term_ids_domain = False
            if move.invoice_payment_term_ids_domain:
                domain = [ ('id', 'in', json.loads(move.invoice_payment_term_ids_domain))]
                print(domain)
                move.suitable_invoice_payment_term_ids=self.env['account.payment.term'].search(domain)


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        self.l10n_ec_sri_payment_id= self.partner_id.l10n_ec_sri_payment_id or self.env.ref('l10n_ec.P1')
        return res

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.l10n_latam_use_documents and self.company_id.account_fiscal_country_id.code == 'EC':
            return 'l10n_ec_invoice.report_invoice_document'
        return super()._get_name_invoice_report()

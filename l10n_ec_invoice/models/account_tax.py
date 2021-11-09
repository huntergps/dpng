# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountTax(models.Model):

    _inherit = "account.tax"

    electronic_tax_code = fields.Char(
        string="Codigo de Tarifa",
    )
    electronic_group_tax_code = fields.Char(related='tax_group_id.electronic_group_tax_code', string='Codigo del Grupo', store=True)


class AccountTaxTemplate(models.Model):

    _inherit = "account.tax.template"

    def _get_tax_vals(self, company, tax_template_to_tax):
        vals = super(AccountTaxTemplate, self)._get_tax_vals(
            company, tax_template_to_tax
        )
        vals.update(
            {
                "electronic_tax_code": self.electronic_tax_code,
            }
        )
        return vals


    electronic_tax_code = fields.Char(
        string="Codigo de Tarifa",
    )

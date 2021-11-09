# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict,OrderedDict
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import unicodedata
from datetime import datetime



class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    quantity_round = fields.Char(string='Cantidad Impresion', compute='_compute_quantity_round')

    def _compute_quantity_round(self):
        for rec in self:
            if rec.quantity % 1==0:
                rec.quantity_round='%.0f'% rec.quantity
            else:
                rec.quantity_round='%.2f'% rec.quantity


    product_code = fields.Char(string='Código' ,related='product_id.default_code', store=True, readonly=True)
    price_unit_net = fields.Float(string='Unit Price Net', digits='Product Price')
    price_unit_discount = fields.Float(string='Unit Price Discount', digits='Product Price')
    price_subtotal_discount = fields.Monetary(string='Subtotal Discount', store=True, readonly=True,
        currency_field='currency_id')

    price_subtotal_line = fields.Monetary(string='Subtotal Line', store=True, readonly=True,
        currency_field='currency_id')

    vat_iva_unit = fields.Float(string='Unit Vat IVA', digits='Product Price')
    vat_iva_subtotal = fields.Float(string='Subtotal Vat IVA', digits='Product Price')

    vat_ice_unit = fields.Float(string='Unit Vat ICE', digits='Product Price')
    vat_ice_subtotal = fields.Float(string='Subtotal Vat ICE', digits='Product Price')

    vat_irbpnr_unit = fields.Float(string='Unit Vat IRBPNR', digits='Product Price')
    vat_irbpnr_subtotal = fields.Float(string='Subtotal Vat IRBPNR', digits='Product Price')

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        price_subtotal_line = price_unit * quantity
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit
        res['price_unit_net'] = line_discount_price_unit
        res['price_subtotal_line'] = price_subtotal_line
        res['price_unit_discount'] = price_unit-line_discount_price_unit
        res['price_subtotal_discount'] = (quantity * price_unit) - subtotal
        # Compute 'price_total'.
        # print(taxes)
        if taxes:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of VAT IVA
        taxes_iva = taxes.filtered(lambda x: x.tax_group_id.l10n_ec_type in ('vat12','vat14'))
        vat_iva_subtotal = vat_iva_unit = 0.0
        if taxes_iva:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            for tr in taxes_res['taxes']:
                vat_iva_subtotal+=tr['amount']
                vat_iva_unit=vat_iva_subtotal/quantity

        res['vat_iva_subtotal']=vat_iva_subtotal
        res['vat_iva_unit'] = vat_iva_unit
        #In case of VAT ICE
        taxes_ice = taxes.filtered(lambda x: x.tax_group_id.l10n_ec_type in ('ice'))
        vat_ice_subtotal = vat_ice_unit = 0.0
        if taxes_ice:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            for tr in taxes_res['taxes']:
                vat_ice_subtotal+=tr['amount']
                vat_ice_unit=vat_ice_subtotal/quantity

        res['vat_ice_subtotal']=vat_ice_subtotal
        res['vat_ice_unit'] = vat_ice_unit

        #In case of VAT IRBPNR
        taxes_irbpnr = taxes.filtered(lambda x: x.tax_group_id.l10n_ec_type in ('irbpnr'))
        vat_irbpnr_subtotal = vat_irbpnr_unit = 0.0
        if taxes_irbpnr:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            for tr in taxes_res['taxes']:
                vat_irbpnr_subtotal+=tr['amount']
                vat_irbpnr_unit=vat_irbpnr_subtotal/quantity

        res['vat_irbpnr_subtotal']=vat_irbpnr_subtotal
        res['vat_irbpnr_unit'] = vat_irbpnr_unit

        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        # print(res)
        return res


    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang,display_default_code=False)
        else:
            product = self.product_id.with_context(display_default_code=False)

        values = []
        if product.partner_ref:
            values.append(product.partner_ref)
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        nline='\n'.join(values)
        return  nline.replace('\n',' ')


    def _l10n_ec_prices_and_taxes(self):
        self.ensure_one()
        invoice = self.move_id
        included_taxes = self.tax_ids
        if not included_taxes:
            price_unit = self.tax_ids.with_context(round=False).compute_all(
                self.price_unit, invoice.currency_id, 1.0, self.product_id, invoice.partner_id)
            price_unit = price_unit['total_excluded']
            price_subtotal = self.price_subtotal
        else:
            price_unit = included_taxes.compute_all(
                self.price_unit, invoice.currency_id, 1.0, self.product_id, invoice.partner_id)['total_included']
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            price_subtotal = included_taxes.compute_all(
                price, invoice.currency_id, self.quantity, self.product_id, invoice.partner_id)['total_included']
        price_net = price_unit * (1 - (self.discount or 0.0) / 100.0)

        return {
            'price_unit': price_unit,
            'price_subtotal': price_subtotal,
            'price_net': price_net,
        }


    ####################################################
    # Export Electronic Document
    ####################################################

    def get_detallesadicionales(self):
        """
        return: [(nombre,valor),(nombre,valor)]
        """
        return []

    def get_detalle_dict(self):
        for line in self:
            invoice = line.move_id
            impuestos = OrderedDict([
                ('impuesto', []),
            ])
            # print(line.tax_ids)
            # print("*"*50)
            # print(line.l10n_latam_tax_ids)
            if line.tax_ids:
                taxes = line.tax_ids
                price_unit = line.price_unit #line.price_subtotal/line.quantity or 0.0
                taxes_res = taxes._origin.compute_all(price_unit,quantity=line.quantity,  is_refund=False)
                for tax_res in taxes_res['taxes']:
                    tax = self.env['account.tax'].browse(tax_res['id'])
                    impuestos['impuesto'].append(
                        OrderedDict([
                            ('codigo', tax.electronic_group_tax_code or ''),
                            ('codigoPorcentaje', tax.electronic_tax_code or ''),
                            ('tarifa', tax.amount),
                            ('baseImponible', '{:.4f}'.format(tax_res['base'])),
                            ('valor', '{:.4f}'.format(abs(tax_res['amount']))),
                        ])
                    )

            if invoice.move_type=='out_invoice':
                detalle = OrderedDict([
                    ('codigoPrincipal', line.product_id.default_code.replace("\n","")),
                    ('codigoAuxiliar', line.product_id.barcode.replace("\n","") if line.product_id.barcode else line.product_id.default_code.replace("\n","")), #line.product_id.barcode[0:25] if line.product_id.barcode[0:25] else line.product_id.default_code[0:25]),
                    ('descripcion', line.name.replace("\n","") or ''),
                    ('cantidad', '{:.2f}'.format(line.quantity)),
                    ('precioUnitario', '{:.4f}'.format(line.price_unit_net)),
                    ('descuento', '{:.4f}'.format(line.price_subtotal_discount)),
                    ('precioTotalSinImpuesto',
                     '{:.4f}'.format(line.price_subtotal)),
                ])
            elif self.move_type=='out_refund':
                detalle = OrderedDict([
                    ('codigoInterno', line.product_id.default_code),
                    ('codigoAdicional', line.product_id.barcode.replace("\n","") if line.product_id.barcode else line.product_id.default_code.replace("\n","")), #line.product_id.barcode[0:25] if line.product_id.barcode[0:25] else line.product_id.default_code[0:25]),
                    ('descripcion', line.name.replace("\n","") or ''),
                    ('cantidad', '{:.2f}'.format(line.quantity)),
                    ('precioUnitario', '{:.4f}'.format(line.price_unit)),
                    ('descuento', '{:.4f}'.format(line.price_unit_discount)),
                    ('precioTotalSinImpuesto',
                     '{:.4f}'.format(line.price_subtotal)),
                ])

            detAdicionales = line.get_detallesadicionales()

            if detAdicionales:
                detallesAdicionales = OrderedDict([
                    ('detAdicional', []),
                ])
                for d in detAdicionales:
                    detallesAdicionales['detAdicional'].append(OrderedDict([
                        ('@nombre', d[0]),
                        ('@valor', d[1]),
                    ]))
                detalle.update(
                    OrderedDict([
                        ('detallesAdicionales', detallesAdicionales),
                    ])
                )

            detalle.update(
                OrderedDict([
                    ('impuestos', impuestos),
                ])
            )
        return detalle



# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     product_code = fields.Char(string='Código' ,related='product_id.default_code', store=True, readonly=True)
#
#     l10n_latam_price_discount = fields.Float(compute='compute_l10n_latam_prices_and_taxes', digits='Product Price')
#
#     def _get_computed_name(self):
#         self.ensure_one()
#
#         if not self.product_id:
#             return ''
#
#         if self.partner_id.lang:
#             product = self.product_id.with_context(lang=self.partner_id.lang,display_default_code=False)
#         else:
#             product = self.product_id.with_context(display_default_code=False)
#
#         values = []
#         if product.partner_ref:
#             values.append(product.partner_ref)
#         if self.journal_id.type == 'sale':
#             if product.description_sale:
#                 values.append(product.description_sale)
#         elif self.journal_id.type == 'purchase':
#             if product.description_purchase:
#                 values.append(product.description_purchase)
#         nline='\n'.join(values)
#         return  nline.replace('\n',' ')
#         # return ' - '.join(str(values).replace('\n',' '))
#
#     # @api.depends('price_unit', 'price_subtotal', 'move_id.l10n_latam_document_type_id')
#     # def compute_l10n_latam_prices_and_taxes(self):
#     #     super().compute_l10n_latam_prices_and_taxes()
#     #     for line in self:
#     #         line.l10n_latam_price_discount = line.l10n_latam_price_unit - line.l10n_latam_price_net
#
#
#     @api.depends('price_unit', 'price_subtotal', 'move_id.l10n_latam_document_type_id')
#     def compute_l10n_latam_prices_and_taxes(self):
#         for line in self:
#             invoice = line.move_id
#             included_taxes = \
#                 invoice.l10n_latam_document_type_id and invoice.l10n_latam_document_type_id._filter_taxes_included(
#                     line.tax_ids)
#             # For the unit price, we need the number rounded based on the product price precision.
#             # The method compute_all uses the accuracy of the currency so, we multiply and divide for 10^(decimal accuracy of product price) to get the price correctly rounded.
#             price_digits = 10**self.env['decimal.precision'].precision_get('Product Price')
#             if not included_taxes:
#                 price_unit = line.tax_ids.with_context(round=False, force_sign=invoice._get_tax_force_sign()).compute_all(
#                     line.price_unit * price_digits, invoice.currency_id, 1.0, line.product_id, invoice.partner_id)
#                 l10n_latam_price_unit = price_unit['total_excluded'] / price_digits
#                 l10n_latam_price_subtotal = line.price_subtotal
#                 not_included_taxes = line.tax_ids
#                 l10n_latam_price_net = l10n_latam_price_unit * (1 - (line.discount or 0.0) / 100.0)
#             else:
#                 not_included_taxes = line.tax_ids - included_taxes
#                 l10n_latam_price_unit = included_taxes.with_context(force_sign=invoice._get_tax_force_sign()).compute_all(
#                     line.price_unit * price_digits, invoice.currency_id, 1.0, line.product_id, invoice.partner_id)['total_included'] / price_digits
#                 l10n_latam_price_net = l10n_latam_price_unit * (1 - (line.discount or 0.0) / 100.0)
#                 price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#                 l10n_latam_price_subtotal = included_taxes.with_context(force_sign=invoice._get_tax_force_sign()).compute_all(
#                     price, invoice.currency_id, line.quantity, line.product_id,
#                     invoice.partner_id)['total_included']
#
#             line.l10n_latam_price_subtotal = l10n_latam_price_subtotal
#             line.l10n_latam_price_unit = l10n_latam_price_unit
#             line.l10n_latam_price_net = l10n_latam_price_net
#             line.l10n_latam_tax_ids = not_included_taxes
#             line.l10n_latam_price_discount = (line.l10n_latam_price_unit - line.l10n_latam_price_net)*line.quantity
#
#
#     ####################################################
#     # Export Electronic Document
#     ####################################################
#
#     def get_detallesadicionales(self):
#         """
#         return: [(nombre,valor),(nombre,valor)]
#         """
#         return []
#
#     def get_detalle_dict(self):
#         for line in self:
#             invoice = line.move_id
#             impuestos = OrderedDict([
#                 ('impuesto', []),
#             ])
#             # print(line.tax_ids)
#             # print("*"*50)
#             # print(line.l10n_latam_tax_ids)
#             if line.l10n_latam_tax_ids:
#                 taxes = line.l10n_latam_tax_ids
#                 price_unit = line.l10n_latam_price_unit #line.price_subtotal/line.quantity or 0.0
#                 taxes_res = taxes._origin.compute_all(price_unit,quantity=line.quantity,  is_refund=False)
#                 for tax_res in taxes_res['taxes']:
#                     tax = self.env['account.tax'].browse(tax_res['id'])
#                     impuestos['impuesto'].append(
#                         OrderedDict([
#                             ('codigo', tax.electronic_group_tax_code),
#                             ('codigoPorcentaje', tax.electronic_tax_code),
#                             ('tarifa', tax.amount),
#                             ('baseImponible', '{:.4f}'.format(tax_res['base'])),
#                             ('valor', '{:.4f}'.format(abs(tax_res['amount']))),
#                         ])
#                     )
#
#             if invoice.move_type=='out_invoice':
#                 detalle = OrderedDict([
#                     ('codigoPrincipal', line.product_id.default_code.replace("\n","")),
#                     ('codigoAuxiliar', line.product_id.barcode.replace("\n","") or ''), #line.product_id.barcode[0:25] if line.product_id.barcode[0:25] else line.product_id.default_code[0:25]),
#                     ('descripcion', line.name.replace("\n","") or ''),
#                     ('cantidad', '{:.2f}'.format(line.quantity)),
#                     ('precioUnitario', '{:.4f}'.format(line.l10n_latam_price_unit)),
#                     ('descuento', '{:.4f}'.format(line.l10n_latam_price_discount)),
#                     ('precioTotalSinImpuesto',
#                      '{:.4f}'.format(line.l10n_latam_price_subtotal)),
#                 ])
#             elif self.move_type=='out_refund':
#                 detalle = OrderedDict([
#                     ('codigoInterno', line.product_id.default_code),
#                     ('codigoAdicional',line.product_id.barcode.replace("\n","") or ''), #line.product_id.barcode[0:25] if line.product_id.barcode[0:25] else line.product_id.default_code[0:25]),
#                     ('descripcion', line.name.replace("\n","") or ''),
#                     ('cantidad', '{:.2f}'.format(line.quantity)),
#                     ('precioUnitario', '{:.4f}'.format(line.l10n_latam_price_unit)),
#                     ('descuento', '{:.4f}'.format(line.l10n_latam_price_discount)),
#                     ('precioTotalSinImpuesto',
#                      '{:.4f}'.format(line.l10n_latam_price_subtotal)),
#                 ])
#
#             detAdicionales = line.get_detallesadicionales()
#
#             if detAdicionales:
#                 detallesAdicionales = OrderedDict([
#                     ('detAdicional', []),
#                 ])
#                 for d in detAdicionales:
#                     detallesAdicionales['detAdicional'].append(OrderedDict([
#                         ('@nombre', d[0]),
#                         ('@valor', d[1]),
#                     ]))
#                 detalle.update(
#                     OrderedDict([
#                         ('detallesAdicionales', detallesAdicionales),
#                     ])
#                 )
#
#             detalle.update(
#                 OrderedDict([
#                     ('impuestos', impuestos),
#                 ])
#             )
#         return detalle

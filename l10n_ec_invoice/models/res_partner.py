# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.l10n_ec.models.res_partner import verify_final_consumer

import stdnum.ec
import re
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = 'res.partner'


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        try:
            recs = self.search(['|','|', ('tradename', operator, name), ('name', operator, name), ('vat', operator, name)] + args, limit=limit)
        except:
            recs = self.search(['|', ('tradename', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    def _default_country_id(self):
        return self.env['res.country'].search([('code', '=ilike', 'EC')]) or False

    def _default_property_payment_term_id(self):
        # if not self.terminos_pagos_ids:
        #     self.terminos_pagos_ids.append(self.env.ref('account.account_payment_term_immediate').id)
        return self.env.ref('account.account_payment_term_immediate') or False

    def _default_property_supplier_payment_term_id(self):
        return self.env.ref('account.account_payment_term_immediate') or False

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',default=_default_country_id)

    tradename = fields.Char('Nombre Comercial', size=300, )



    es_transportista = fields.Boolean('Es Transportista',default=False)

    terminos_pagos_ids = fields.Many2many(
        'account.payment.term','res_partner_payment_term_rel',
        'res_partner_id', 'payment_term_id',
        'Terminos de Pago autorizados en Ventas')

    terminos_pagos_supplier_ids = fields.Many2many(
        'account.payment.term','res_partner_payment_term_rel',
        'res_partner_id', 'payment_term_id',
        'Terminos de Pago autorizados en Compras')

    l10n_ec_sri_payment_id = fields.Many2one(
        'l10n_ec.sri.payment', string='Forma de pago principal', )

    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
        string='Customer Payment Terms',
        default = _default_property_payment_term_id,
        # domain="[('company_id', 'in', [current_company_id, False]),('id','in',terminos_pagos_ids)]",
        help="This payment term will be used instead of the default one for sales orders and customer invoices")

    property_supplier_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
        string='Vendor Payment Terms',
        default = _default_property_supplier_payment_term_id,
        # domain="[('company_id', 'in', [current_company_id, False]),('id','in',terminos_pagos_supplier_ids)]",
        help="This payment term will be used instead of the default one for purchase orders and vendor bills")

    vat = fields.Char(string='Tax ID', index=True, copy=False,
    help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")

    @api.constrains("vat", "country_id", "l10n_latam_identification_type_id")
    def check_vat(self):
        if self.same_vat_partner_id:
            raise ValidationError(
                _("El %s Nro %s ya esta registrado a nombre de %s con ID #%s") %(self.l10n_latam_identification_type_id.name,self.vat,self.same_vat_partner_id.name,self.same_vat_partner_id.id)
            )
        it_ruc = self.env.ref("l10n_ec.ec_ruc", False)
        it_dni = self.env.ref("l10n_ec.ec_dni", False)
        it_consumidor_final = self.env.ref("l10n_ec_invoice.it_consumidor_final", False)
        ecuadorian_partners = self.filtered(
            lambda x: x.country_id == self.env.ref("base.ec")
        )
        for partner in ecuadorian_partners:
            if partner.vat:
                if partner.l10n_latam_identification_type_id.id in (
                    it_ruc.id,
                    it_dni.id,
                    it_consumidor_final.id,
                ):
                    if partner.l10n_latam_identification_type_id.id == it_dni.id and len(partner.vat) != 10:
                        raise ValidationError(_('If your identification type is %s, it must be 10 digits')
                                              % it_dni.display_name)
                    if partner.l10n_latam_identification_type_id.id == it_ruc.id and len(partner.vat) != 13:
                        raise ValidationError(_('If your identification type is %s, it must be 13 digits')
                                              % it_ruc.display_name)

                    if partner.l10n_latam_identification_type_id.id == it_consumidor_final.id:
                        if len(partner.vat) != 13:
                            raise ValidationError('El numero de %s, debe tener 13 digitos'% it_consumidor_final.display_name)
                        final_consumer = verify_final_consumer(partner.vat)
                        print('final_consumer =%s'%final_consumer)
                        if final_consumer:
                            valid = True
                        else:
                            raise ValidationError('El numero de %s, debe ser 9999999999999'% it_consumidor_final.display_name)
                    else:
                        if partner.l10n_latam_identification_type_id.id == it_ruc.id:
                            valid = self.is_valid_ruc_ec(partner.vat)
                            if not valid:
                                raise ValidationError(
                                    _(
                                        "El RUC %s no es un numero valido para Ecuador, "
                                        "debe ser de la forma0993143790001"
                                    )
                                    % partner.vat
                                )
                        if partner.l10n_latam_identification_type_id.id == it_dni.id:
                            valid = self.is_valid_ci_ec(partner.vat)
                            if not valid:
                                raise ValidationError(
                                    _(
                                        "La Cedula %s no es un numero valido para Ecuador, "
                                        "debe ser de la forma 0993143790"
                                    )
                                    % partner.vat
                                )
                # partner.l10n_ec_identification_validation()
            # else:
            #     raise ValidationError('El numero de Identificacion es obligatorio')

        return super(ResPartner, self - ecuadorian_partners).check_vat()




    def _format_vat_ec(self, values):
        vat = values['vat']
        it_ruc = self.env.ref("l10n_ec.ec_ruc", False)
        it_dni = self.env.ref("l10n_ec.ec_dni", False)
        it_consumidor_final = self.env.ref("l10n_ec_invoice.it_consumidor_final", False)
        identification_types = [it_ruc.id, it_dni.id,it_consumidor_final.id]
        country = self.env["res.country"].browse(values.get('country_id'))
        identification_type = self.env['l10n_latam.identification.type'].browse(values.get('l10n_latam_identification_type_id'))
        partner_country_is_ecuador = country.code == "EC" or identification_type.country_id.code == "EC"
        if partner_country_is_ecuador and values.get('l10n_latam_identification_type_id') in identification_types and values.get('vat'):
            if identification_type.code == 'C':
                vat = str(stdnum.ec.ci.compact(vat))
            elif identification_type.code == 'R':
                print(stdnum.ec.ruc.compact(vat))
                vat = str(stdnum.ec.ruc.compact(vat))
            elif identification_type.code == 'F':
                vat = '9999999999999'
        return vat





    @api.model
    def create(self, values):
        if values.get('vat'):
            values['vat'] = self._format_vat_ec(values)
        return super().create(values)

    def write(self, values):
        if 'vat' in values or 'l10n_latam_identification_type_id' in values:
            for record in self:
                vat_values = {
                    'vat': values.get('vat', record.vat),
                    'l10n_latam_identification_type_id': values.get(
                        'l10n_latam_identification_type_id', record.l10n_latam_identification_type_id.id),
                    'country_id': values.get('country_id', record.country_id.id)
                }
                values['vat'] = self._format_vat_ec(vat_values)
        return super().write(values)

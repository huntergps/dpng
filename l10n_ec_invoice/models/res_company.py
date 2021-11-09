# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    tradename = fields.Char('Nombre Comercial', size=300, )

    logo_header = fields.Binary(string="Logo de Cabecera")
    logo_footer = fields.Binary(string="Logo de Pie")
    lleva_contabilidad = fields.Boolean('Obligado a llevar Contabilidad')
    emitir_retenciones = fields.Boolean('Emitir Retenciones')
    contribuyente_especial = fields.Boolean('Contribuyente Especial')
    contribuyente_especial_nro = fields.Integer('Resolución Contr. Esp. No.', )
    agente_retencion = fields.Boolean('Agente de Retencion Asignado')
    agente_retencion_nro = fields.Integer(string='Agente Ret. No.', default=0)
    regimen_impositivo = fields.Selection([
            ('RUC','RUC'),
            ('RISE', 'RISE'),
            ('MICRO', 'Microempresa')],string='Regimen Impositivo',
        default='RUC' )
    autorizacion_id = fields.Many2one(
        'l10n_ec_invoice.autorizacion', string='Punto de Emision', )
    # autorizacion_notas_credito_id = fields.Many2one(
    #     'l10n_ec_invoice.autorizacion', string='Autorizacion en notas de crédito', )
    # autorizacion_retenciones_id = fields.Many2one(
    #     'l10n_ec_invoice.autorizacion', string='Autorizacion en retenciones', )
    # autorizacion_liquidaciones_id = fields.Many2one(
    #     'l10n_ec_invoice.autorizacion', string='Autorizacion en liquidaciones', )
    # autorizacion_guias_remision_id = fields.Many2one(
    #     'l10n_ec_invoice.autorizacion',
    #     string='Autorizacion en guías de remisión', )

    # def _localization_use_documents(self):
    #     """ Ecuadorian localization use documents """
    #     self.ensure_one()
    #     return self.account_fiscal_country_id.code == "EC" or super()._localization_use_documents()
    firma_id = fields.Many2one(
        'l10n_ec_invoice.firma', string='Firma electrónica', )
    ambiente_id = fields.Many2one(
        'l10n_ec_invoice.ambiente', string='Ambiente', )
    logo_electronic_doc = fields.Binary(string="Logo para Ride")
    logo_header = fields.Binary(string="Logo de Cabecera")
    logo_footer = fields.Binary(string="Logo de Pie")

# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class SriAmbiente(models.Model):
    _name = 'l10n_ec_invoice.ambiente'
    _description ='Ambiente de Facturcion SRI'
    
    name = fields.Char(string='Descripción', )
    ambiente = fields.Selection(
        [
            ('1', 'Pruebas'),
            ('2', 'Producción'),
        ],
        string='Ambiente', )
    recepcioncomprobantes = fields.Char(
        string='URL de recepción de comprobantes', )
    autorizacioncomprobantes = fields.Char(
        string='URL de autorización de comprobantes', )

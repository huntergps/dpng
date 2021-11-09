# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression


class Autorizacion(models.Model):
    _name = 'l10n_ec_invoice.autorizacion'
    _description = "Autorizaciones de Punto de Venta"

    name = fields.Char(string="Descripcion")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, index=True, default=lambda self: self.env.company,
        help="Company related to this journal")
    company_partner_id = fields.Many2one('res.partner', related='company_id.partner_id', string='Account Holder', readonly=True, store=False)

    l10n_ec_entity = fields.Char(string="Emission Entity", size=3, default="001")
    l10n_ec_emission = fields.Char(string="Emission Point", size=3, default="001")
    l10n_ec_emission_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Emission address",
        domain="['|', ('id', '=', company_partner_id), '&', ('id', 'child_of', company_partner_id), ('type', '!=', 'contact')]",
    )

    l10n_ec_emission_type = fields.Selection(
        string="Tipo de Emision",
        selection=[
            ("pre_printed", "PreImpresa"),
            ("auto_printer", "AutoImpresa"),
            ("electronic", "Electronica"),
        ],
        default="electronic",
    )
    sale_invoice_secuence = fields.Integer(string='Secuencia de Facturas',default=1)
    sale_credit_note_secuence = fields.Integer(string='Secuencia de NC',default=1)
    sale_delivery_note_secuence = fields.Integer(string='Secuencia de Guias de Remision',default=1)
    purchase_liquidation_secuence = fields.Integer(string='Secuencia de Liquidaciones',default=1)
    purchase_retention_secuence = fields.Integer(string='Secuencia de Retenciones',default=1)

    user_ids = fields.Many2many('res.users', 'l10n_ec_invoice_autorizacion_users', string='Usuarios')

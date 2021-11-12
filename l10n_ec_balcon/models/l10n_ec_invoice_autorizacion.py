# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression


class Autorizacion(models.Model):
    _inherit = 'l10n_ec_invoice.autorizacion'

    id_theos = fields.Char('Theos ID')
    para_patentes = fields.Boolean('Para patentes')
    oficina = fields.Selection(
        string="Oficina de Emision",
        selection=[
            ("SX", "Santa Cruz"),
            ("SC", "San Cristobal"),
            ("IS", "Isabela"),
            ("FL", "Floreana"),
        ],
        default="SX",
    )

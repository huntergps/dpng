# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from odoo import models, api, fields
from odoo.tools.sql import column_exists, create_column



class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auto_init(self):
        if not column_exists(self.env.cr, "res_users", "autorizacion_id"):
            create_column(self.env.cr, "res_users", "autorizacion_id", "int4")
        return super()._auto_init()

    # # Autorizaciones por usuario.
    autorizacion_id = fields.Many2one(
        'l10n_ec_invoice.autorizacion', string='Punto de Emision' )

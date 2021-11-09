# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    sia_id = fields.Char('SIA ID')

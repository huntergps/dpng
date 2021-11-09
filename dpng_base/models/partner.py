# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta,datetime

# import datetime
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sia_id = fields.Char('SIA ID')
    tur_id = fields.Char('Anterior ID')
    id_theos = fields.Char('Theos ID')

    operador_tur = fields.Boolean(string='Es operador Turistico',
                               help="Marque esta caja si es Operador Turistico")
    dpng_repre_legal = fields.Char('Representante Legal')
    dpng_repre_gps = fields.Char('Representante en Galápagos')
    dpng_modalidad = fields.Char('Modalidad')
    guardaparque = fields.Boolean(string='Es Guardaparque', default=False)

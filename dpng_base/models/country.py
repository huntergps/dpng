# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta,datetime

# import datetime
from odoo.exceptions import UserError

class ResCountry(models.Model):
    _inherit = 'res.country'
    sia_id = fields.Char('SIA ID')
    tur_id = fields.Char('Anterior ID')
    id_theos = fields.Char('Theos ID')

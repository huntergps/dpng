# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date, timedelta,datetime

# import datetime
from odoo.exceptions import UserError

class ProductCategory(models.Model):
    _inherit = "product.category"
    codigo = fields.Char('Codigo')
    sia_id = fields.Char('SIA ID')
    tur_id = fields.Char('Anterior ID')
    id_theos = fields.Char('Theos ID')


class ProductTemplate(models.Model):
    _inherit = ["product.template"]
    patente_tur = fields.Boolean(string='Es para Patente Turistica',
                           help="Marque si es Servicio Turistico")
    sia_id = fields.Char('SIA ID')
    tur_id = fields.Char('Anterior ID')
    id_theos = fields.Char('Theos ID')



class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        result = super(ProductProduct, self.with_context(display_default_code=False)).name_get()
        return result

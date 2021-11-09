    # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_split

import json
import requests

from werkzeug.urls import url_encode

MESES ={
    1:'ENERO',
    2:'FEBRERO',
    3:'MARZO',
    4:'ABRIL',
    5:'MAYO',
    6:'JUNIO',
    7:'JULIO',
    8:'AGOSTO',
    9:'SEPTIEMBRE',
    10:'OCTUBRE',
    11:'NOVIEMBRE',
    12:'DICIEMBRE'
    }

class RolRubros(models.Model):
    _name = "gob.roles.rubros"
    _description = "Rubros de Roles de Pagos"

    name = fields.Char(string='Nombre', required=True)
    rubro_codigo = fields.Char(string='Codigo Rubro')
    cod_deduc = fields.Char(string='Codigo Deduccion', index=True)
    rubro_tipo = fields.Selection([
        ('A', 'Aporte'),
        ('D', 'Descuento'),
        ('I', 'Ingreso')
        ], string='Tipo de Rubro',default='A')
    id_theos = fields.Char('Theos ID')


class RolPagos(models.Model):
    _name = "gob.roles.pagos"
    _description = "Roles de Pagos"

    name = fields.Char(string='Nombre', compute='_compute_name', readonly=False, store=True)
    ejercicio = fields.Integer(string='Ejercicio')
    periodo = fields.Integer(string='Periodo')
    periodo_name = fields.Char(string='Periodo', compute='_compute_periodo_name', store=True)
    nomina_lines = fields.One2many('gob.roles.nominas', 'rol_id', string='Nominas de Rol', copy=True, auto_join=True)
    detail_lines = fields.One2many('gob.roles.det', 'rol_id', string='Roles Individuales', copy=True, auto_join=True)

    id_theos = fields.Char('Theos ID')

    @api.depends('ejercicio', 'periodo')
    def _compute_periodo_name(self):
        self.periodo_name = MESES[self.periodo]


    @api.depends('ejercicio', 'periodo')
    def _compute_name(self):
        for rec in self:
            rec.name = 'ROL DE PAGOS UNIFICADO %s %s'%( MESES[rec.periodo],rec.ejercicio)




class NominaPagos(models.Model):
    _name = "gob.roles.nominas"
    _description = "Nominas de Roles de Pagos"

    rol_id = fields.Many2one('gob.roles.pagos', string='Rol de Pagos', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Nombre', required=True)
    tipo_nomina = fields.Char(string='Tipo de Nomina', required=True)
    cur_nro = fields.Integer(string='Numero de CUR')
    cur_fecha = fields.Date(string='Fecha de CUR')
    id_spring = fields.Integer(string='ID en Spring')
    ejercicio = fields.Integer(string='Ejercicio')
    periodo = fields.Integer(string='Periodo')
    id_theos = fields.Char('Theos ID')



class NominaRolesDetail(models.Model):
    _name = "gob.roles.det"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Detalles de Roles de Pago"

    name = fields.Char(string='Nombre', compute='_compute_name', readonly=False, store=True)
    rol_id = fields.Many2one('gob.roles.pagos', string='Rol de Pagos', required=True, ondelete='cascade', index=True)
    lines_ids = fields.One2many('gob.roles.det.lin', 'detail_id', string='Lineas de Detalle',  auto_join=True)
    ejercicio = fields.Integer(string='Ejercicio')
    periodo = fields.Integer(string='Periodo')
    periodo_name = fields.Char(related='rol_id.periodo_name',store=True)
    nro_documento = fields.Char(string='Numero Documento')
    apellidos_nombres = fields.Char(string='Apellidos y Nombres')
    email = fields.Char(related='partner_id.email')
    partner_id = fields.Many2one(
        'res.partner', string='Empleado',
        change_default=True, index=True)
    amount_in = fields.Float(string='Ingresos', digits='Product Price',compute='_compute_amounts')
    amount_out = fields.Float(string='Egresos', digits='Product Price',compute='_compute_amounts')
    amount_apo= fields.Float(string='Aportes', digits='Product Price',compute='_compute_amounts')
    amount_balance= fields.Float(string='Saldo', digits='Product Price',compute='_compute_amounts')

    id_theos = fields.Char('Theos ID')


    @api.depends('ejercicio', 'periodo','nro_documento','partner_id')
    def _compute_name(self):
        for rec in self:
            rec.name = 'Rol de Pagos %s %s - %s %s'%( MESES[rec.periodo],rec.ejercicio,rec.nro_documento,rec.apellidos_nombres)


    @api.depends('lines_ids', 'lines_ids.amount_desc')
    def _compute_amounts(self):
        for rec in self:
            amount_in = amount_out = amount_apo = amount_balance = 0.0
            for line in rec.lines_ids:
                amount_in += line.amount_desc if line.rubro_tipo=='I' else 0.0
                amount_out += line.amount_desc if line.rubro_tipo=='D' else 0.0
                amount_apo += line.amount_desc if line.rubro_tipo=='A' else 0.0
            amount_balance= amount_in-(amount_out+amount_apo)
            rec.amount_in = amount_in
            rec.amount_out = amount_out
            rec.amount_apo = amount_apo
            rec.amount_balance = amount_balance



class RolesDetailLines(models.Model):
    _name = "gob.roles.det.lin"
    _description = "Lineas de Detalles de Roles de Pagos"

    detail_id = fields.Many2one('gob.roles.det', string='Detalle de Rol de Pagos', required=True, ondelete='cascade', index=True)
    rol_id = fields.Many2one(related='detail_id.rol_id', store=True)
    nomina_statement_line_id = fields.Many2one(comodel_name='gob.roles.statment.line',string="Linea de Extracto de Nomina", copy=False, check_company=True)

    rubro_id = fields.Many2one('gob.roles.rubros', string='Rubro de Rol de Pagos', required=True, ondelete='cascade', index=True)
    rubro_tipo = fields.Selection(related='rubro_id.rubro_tipo',store=True)
    rubro_codigo = fields.Char(related='rubro_id.rubro_codigo',store=True)
    amount_calc = fields.Float(string='Monto Calculado', digits='Product Price',default=0.0)
    amount_desc = fields.Float(string='Monto Descuento', digits='Product Price',default=0.0)
    amount_pend = fields.Float(string='Monto Pendiente', digits='Product Price',default=0.0)
    amount_int= fields.Float(string='Ingresos', digits='Product Price',compute='_compute_amounts_line')
    amount_out = fields.Float(string='Egresos', digits='Product Price',compute='_compute_amounts_line')
    id_theos = fields.Char('Theos ID')

    @api.depends('amount_calc', 'amount_desc')
    def _compute_amounts_line(self):
        for rec in self:
            amount_int = rec.amount_desc if rec.rubro_tipo =='I' else 0.0
            amount_out = rec.amount_desc if rec.rubro_tipo in ('A','D') else 0.0
            rec.amount_int = amount_int
            rec.amount_out = amount_out

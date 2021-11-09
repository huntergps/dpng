    # -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import io
import logging
import tempfile
import binascii
from datetime import datetime
import unidecode

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


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


class NominaStatment(models.Model):
    _name = "gob.roles.statment"
    _description = "Extractos de Nomina"

    name = fields.Char(string='Referencia', states={'open': [('readonly', False)]}, copy=False, readonly=True)
    reference = fields.Char(string='Referencia Externa', states={'open': [('readonly', False)]}, copy=False, readonly=True)
    date = fields.Date(string="Fecha", required=True, states={'confirm': [('readonly', True)]}, index=True, copy=False, default=fields.Date.context_today)
    date_done = fields.Datetime(string="Fecha de Procesamiento")
    state = fields.Selection(string='Status', required=True, readonly=True, copy=False, selection=[
            ('open', 'Nuevo'),
            ('posted', 'Procesando'),
            ('confirm', 'Validado'),
        ], default='open')

    company_id = fields.Many2one('res.company', string='Company', store=True, readonly=True,
        default=lambda self: self.env.company)
    line_ids = fields.One2many('gob.roles.statment.line', 'nomina_statement_id', string='Lineas de Extracto', states={'confirm': [('readonly', True)]}, copy=True)

    user_id = fields.Many2one('res.users', string='Responsable', required=False, default=lambda self: self.env.user)

    statement_lines_ids = fields.One2many(
        'gob.roles.statment.line','nomina_statement_id', 'Extractos de Nomina Disponibles',
        compute="_get_statement_lines_ids")
    used_statement_lines_ids = fields.One2many(
        'gob.roles.statment.line','nomina_statement_id', 'Extractos de Nomina Usados',
        compute="_get_used_statement_lines_ids")


    def button_procesar_nominas(self,role_id,ejercicio,periodo):
        for rec in self:
            query = """
                select distinct ejercicio,periodo,tipo_nomina,name,cur_nro,cur_fecha,id_spring from gob_roles_statment_line
                where is_reconciled is not True and ejercicio='%s' and periodo=%s"""%(ejercicio,periodo)
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()
            for result in results:
                nominas_id = self.env['gob.roles.nominas'].search([('id_spring','=',result['id_spring'])])
                if not nominas_id:
                    self.env['gob.roles.nominas'].create({
                        'ejercicio':result['ejercicio'],
                        'periodo':result['periodo'],
                        'tipo_nomina':result['tipo_nomina'],
                        'name':result['name'],
                        'cur_nro':result['cur_nro'],
                        'cur_fecha':result['cur_fecha'],
                        'id_spring':result['id_spring'],
                        'rol_id':role_id,
                        })



    def button_procesar_detalles(self,role_id,ejercicio,periodo):
        for rec in self:
            query = """
                select distinct ejercicio,periodo,nro_documento,apellidos_nombres,partner_id from gob_roles_statment_line
                where is_reconciled is not True and ejercicio='%s' and periodo=%s"""%(ejercicio,periodo)
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()
            for result in results:
                detalles_id = self.env['gob.roles.det'].search([('ejercicio','=',ejercicio),('periodo','=',periodo),('nro_documento','=',result['nro_documento'])])
                if not detalles_id:
                    self.env['gob.roles.det'].create({
                        'ejercicio':result['ejercicio'],
                        'periodo':result['periodo'],
                        'nro_documento':result['nro_documento'],
                        'apellidos_nombres':result['apellidos_nombres'],
                        'partner_id':result['partner_id'],
                        'rol_id':role_id,
                        })

    def get_detalle_id(self,role_id,ejercicio,periodo,result):
        domain_detalle=[('ejercicio','=',ejercicio),('periodo','=',periodo),('nro_documento','=',result['nro_documento'])]
        if result['partner_id']:
            domain_detalle=[('ejercicio','=',ejercicio),('periodo','=',periodo),('nro_documento','=',result['nro_documento']),('partner_id','=',result['partner_id'])]
        detalles_id = self.env['gob.roles.det'].search(domain_detalle)
        obj_detalle_id = detalles_id and detalles_id[0] or False
        if not obj_detalle_id:
            obj_detalle_id=self.env['gob.roles.det'].create({
                'ejercicio':result['ejercicio'],
                'periodo':result['periodo'],
                'nro_documento':result['nro_documento'],
                'apellidos_nombres':result['apellidos_nombres'],
                'partner_id':result['partner_id'],
                'rol_id':role_id,
                })
            detalle_id=obj_detalle_id.id
        else:
            detalle_id=obj_detalle_id.id
        return detalle_id

    def get_detalle_line_id(self,detail_id,rubro_id):
        detalle_line_id = False
        domain_detalle_line=[('rubro_id','=',rubro_id),('detail_id','=',detail_id)]
        detalles_lines_id = self.env['gob.roles.det.lin'].search(domain_detalle_line)
        obj_ddetalle_line_id = detalles_lines_id and detalles_lines_id[0] or False
        if obj_ddetalle_line_id:
            detalle_line_id=obj_ddetalle_line_id
        return detalle_line_id


    def button_procesar_detalles_lines(self,role_id,ejercicio,periodo):
        for rec in self:
            query = """
                select id,ejercicio,periodo,nro_documento,apellidos_nombres,partner_id,rubro_id,amount_calc,amount_desc,amount_pend from gob_roles_statment_line
                where is_reconciled is not True and ejercicio='%s' and periodo=%s"""%(ejercicio,periodo)
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()
            for result in results:
                detalle_id= self.get_detalle_id(role_id,ejercicio,periodo,result)
                if detalle_id:
                    detalle_line_id = self.get_detalle_line_id(detalle_id,result['rubro_id'])
                    val_line={
                        'rubro_id':result['rubro_id'],
                        'detail_id':detalle_id,
                        'amount_calc':result['amount_calc'],
                        'amount_desc':result['amount_desc'],
                        'amount_pend':result['amount_pend'],
                        'nomina_statement_line_id':result['id'],
                        }
                    if not detalle_line_id:
                        detalle_line_id=self.env['gob.roles.det.lin'].create(val_line)
                    else:
                        detalle_line_id.write(val_line)
                    gob_roles_statment_line = self.env['gob.roles.statment.line'].browse(result['id'])
                    gob_roles_statment_line.write({'detail_line_id':detalle_line_id.id})

    def button_procesar_movimientos(self):
        for rec in self:
            query = """Select distinct ejercicio,periodo from gob_roles_statment_line where is_reconciled is not True"""
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()
            for result in results:
                roles_id = self.env['gob.roles.pagos'].search([('ejercicio','=',result['ejercicio']),('periodo','=',result['periodo'])])
                if not roles_id:
                    _name='ROL DE PAGOS UNIFICADO %s %s'%(MESES[result['periodo']],result['ejercicio'])
                    roles_id = self.env['gob.roles.pagos'].create({'ejercicio':result['ejercicio'],'periodo':result['periodo'],'name':_name})
                for rol in roles_id:
                    rec.button_procesar_nominas(rol.id,result['ejercicio'],result['periodo'])
                    rec.button_procesar_detalles(rol.id,result['ejercicio'],result['periodo'])
                    rec.button_procesar_detalles_lines(rol.id,result['ejercicio'],result['periodo'])


    def button_cancel_and_delete(self):
        for rec in self:
            rec.button_vaciar_movimientos()
            rec.unlink()
        return True


    def button_vaciar_movimientos(self):
        for rec in self:
            rec.statement_lines_ids.unlink()
            rec.used_statement_lines_ids.unlink()



    @api.depends('date','state')
    def _get_statement_lines_ids (self):
        domain = [
            ('nomina_statement_id','=',self.id),
            ('is_reconciled', '=', False)
        ]
        statement_lines_ids = self.env['gob.roles.statment.line'].search(domain)
        self.statement_lines_ids = statement_lines_ids


    @api.depends('date','state')
    def _get_used_statement_lines_ids (self):
        domain = [
            ('nomina_statement_id','=',self.id),
            ('is_reconciled', '=', True)
        ]
        used_statement_lines_ids = self.env['gob.roles.statment.line'].search(domain)
        self.used_statement_lines_ids = used_statement_lines_ids



    def action_import_movimientos(self):
        action_name = 'action_gob_roles_statement_import'
        [action] = self.env.ref('dpng_roles.%s' % action_name).read()
        # Note: this drops action['context'], which is a dict stored as a string, which is not easy to update
        # action.update({'context': (u"{'journal_id': " + str(self.id) + u"}")})
        return action


    def action_import_movimientos1(self):
        view = self.env.ref('dpng_roles.action_gob_roles_statement_import')

        return {
            'name': 'Importación de Extractos Bancarios',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }



class NominaStatmentLine(models.Model):
    _name = "gob.roles.statment.line"
    _description = "Lineas de Extractos de Nominas de Roles"
    _order = "nomina_statement_id desc, ejercicio, periodo, id desc"

    nomina_statement_id = fields.Many2one(
        comodel_name='gob.roles.statment',
        string='Extracto de Nomina', index=True, required=True, ondelete='cascade',
        check_company=True)

    detail_line_id = fields.Many2one(
        comodel_name='gob.roles.det.lin',
        string='Detalle de Rol', required=True, readonly=True, ondelete='cascade',
        check_company=True)

    ejercicio = fields.Integer(string='Ejercicio')
    periodo = fields.Integer(string='Periodo')
    tipo_nomina = fields.Char(string='Tipo de Nomina')
    name = fields.Char(string='Descripcion')
    cur_nro = fields.Integer(string='Nro de CUR')
    cur_fecha = fields.Date(string='Fecha de CUR')
    id_spring = fields.Integer(string='ID en Spring')
    nro_documento = fields.Char(string='Numero Documento')
    apellidos_nombres = fields.Char(string='Apellidos y Nombres')
    rubro_cod_deduc = fields.Char(string='Codigo Deduccion')
    rubro_tipo = fields.Char(string='Tipo de Nomina')
    rubro_codigo = fields.Char(string='Codigo Rubro')
    rubro_name = fields.Char(string='Nombre de Rubro')
    amount_calc = fields.Float(string='Monto Calculado', digits='Product Price',default=0.0)
    amount_desc = fields.Float(string='Monto Descuento', digits='Product Price',default=0.0)
    amount_pend = fields.Float(string='Monto Pendiente', digits='Product Price',default=0.0)
    rubro_id = fields.Many2one('gob.roles.rubros', string='Rubro de Rol de Pagos', required=True, ondelete='cascade', index=True)
    unique_import_id = fields.Char(string='Import ID', readonly=True, copy=False)
    is_reconciled = fields.Boolean(compute='_check_reconciled', store=True)
    partner_id = fields.Many2one('res.partner', string='Empleado', index=True)
    _sql_constraints = [
        ('unique_import_id', 'unique (unique_import_id)', 'La linea de la nomina debe ser unica !')
    ]


    @api.depends('detail_line_id')
    def _check_reconciled(self):
        for line in self:
            line.is_reconciled = len(line.detail_line_id)>0

def import_fecha(fecha):
    try:
        fecha_res=fecha.decode("utf-8")
    except:
        fecha_res=fecha
    fechas =None

    try:
        fechas= datetime.utcfromtimestamp(int((float(fecha_res) - 25569) * 86400.0)).date()
        #print(fechas)
        #fechas==datetime.date.fromordinal(int(fecha_res)).strftime('%d.%m.%Y')
    except:
        fechas = None
    return fechas



class AccountBankStatementImport(models.TransientModel):
    _name = 'gob.roles.statment.import'
    _description = 'Importacion de Lineas de Extractos de Nominas'

    attachment_ids = fields.Many2many('ir.attachment', string='Archivos', required=True)



    def create_statement(self, values):

        statement = self.env['gob.roles.statment'].create(values)
        return statement

    def get_unique_import_id(self, ejercicio,periodo,cur_nro,cur_fecha,id_spring,nro_documento,rubro_tipo,rubro_codigo,amount_calc):
        unique_import_id = ('%s%s%s%s%s%s%s%s%s'%(ejercicio,periodo,cur_nro,cur_fecha,id_spring,nro_documento,rubro_tipo,rubro_codigo,amount_calc)).upper()
        unique_import_id = unique_import_id.replace('*', '').replace(' ', '').replace('-', '').replace('_', '').replace(':', '').replace('=', '').replace('.', '').replace(',', '')
        unique_import_id = unidecode.unidecode(unique_import_id)
        return unique_import_id

    def get_rubros_id(self):
        rol_rubros = self.env['gob.roles.rubros'].browse()
        rubros={}
        for cat in rol_rubros:
            rubros[cat.rubro_codigo]=cat.id
        return rubros

    def get_guardaparques_id(self):
        guardaparque_ids=self.env['res.partner'].search([('guardaparque','=',True)])
        # guardaparque_ids = self.env['res.partner'].browse(ids)
        guardaparques={}
        for rec in guardaparque_ids:
            guardaparques[rec.vat]=rec.id
        return guardaparques

    # def get_name_rubro(self,cadena):
    #     cads = cadena.split()
    #     if len(cads)>1:
    #         cadLetras=''.join([i for i in cads[0] if not i.isdigit()])
    #
    #     return cad

    def import_file(self):
        for data_file in self.attachment_ids:
            file_name = data_file.name.lower()
            if file_name.strip().endswith('.xls') or file_name.strip().endswith('.xlsx'):
                statement = False
                if file_name.strip().endswith('.xls'):
                    try:
                        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xls")
                        fp.write(binascii.a2b_base64(data_file.datas))
                        fp.seek(0)
                        values = {}
                        workbook = xlrd.open_workbook(fp.name)
                        sheet = workbook.sheet_by_index(0)
                    except:
                        raise UserError(_("Archivo invalido!"))

                if file_name.strip().endswith('.xlsx'):
                    try:
                        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                        fp.write(binascii.a2b_base64(data_file.datas))
                        fp.seek(0)
                        values = {}
                        workbook = xlrd.open_workbook(fp.name)
                        sheet = workbook.sheet_by_index(0)
                    except:
                        raise UserError(_("Archivo invalido!"))
                if sheet:
                    vals_list = []
                    rubros=self.get_rubros_id()
                    guardaparques = self.get_guardaparques_id()
                    for row_no in range(sheet.nrows):
                        val = {}
                        values = {}
                        if row_no <= 0:
                            fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                        else:
                            line = list(map(
                                lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                    row.value), sheet.row(row_no)))

                            fecha=import_fecha(line[5])
                            cur_fecha=None
                            if fecha:
                                cur_fecha = fecha.strftime('%Y-%m-%d')

                            unique_import_id = self.get_unique_import_id(int(float(line[0])),int(float(line[1])),int(float(line[4])),cur_fecha,int(float(line[6])),line[7],line[10],line[11],line[13])
                            last_line = self.env['gob.roles.statment.line'].search([('unique_import_id', '=',unique_import_id)], limit=1)

                            try:
                                guardaparque_id=guardaparques[line[7]] if len(line[7])>0 else False
                            except Exception as e:
                                guardaparque_id = False

                            rubro_id=False
                            try:
                                rubro_id=rubros[line[11]] if len(line[11])>0 else False
                            except Exception as e:
                                rubro_id=False
                            if not rubro_id:
                                rubro_vals={
                                'rubro_codigo':line[11],
                                'cod_deduc':line[9],
                                'rubro_tipo':line[10],
                                'name':str(''.join([i for i in line[12] if not i.isdigit()])).strip() ,
                                }
                                obj_rubros=self.env['gob.roles.rubros'].search([('rubro_codigo','=',line[11])])
                                obj_rubro_id = obj_rubros and obj_rubros[0] or False
                                if not obj_rubro_id:
                                    new_rubro_id=self.env['gob.roles.rubros'].create(rubro_vals)
                                    rubros=self.get_rubros_id()
                                    rubro_id=new_rubro_id.id
                                else:
                                    rubro_id=obj_rubro_id.id
                            if not last_line:
                                values.update({
                                    'ejercicio': int(float(line[0])),
                                    'periodo': int(float(line[1])),
                                    'tipo_nomina': line[2],
                                    'name': line[3],
                                    'cur_nro': int(float(line[4])),
                                    'cur_fecha': cur_fecha,
                                    'id_spring': int(float(line[6])),
                                    'nro_documento': line[7],
                                    'apellidos_nombres': line[8],
                                    'rubro_cod_deduc': line[9],
                                    'rubro_tipo': line[10],
                                    'rubro_codigo': line[11],
                                    'rubro_name': line[12],
                                    'amount_calc': line[13],
                                    'amount_desc': line[14],
                                    'amount_pend': line[15],
                                    'nomina_statement_id': self._context.get('active_id'),
                                    'unique_import_id':unique_import_id,
                                    'rubro_id':rubro_id,
                                })
                                if guardaparque_id:
                                    values['partner_id']=guardaparque_id
                                self.env['gob.roles.statment.line'].create(values)
                #     statement_vals = {
                #         'name': 'Extracto de ' + str(datetime.today().date()),
                #         'line_ids': vals_list
                #     }
                #     if len(vals_list) != 0:
                #         statement = self.create_statement(statement_vals)
                #
                # if statement:
                #     return {
                #         'type': 'ir.actions.act_window',
                #         'res_model': 'gob.roles.statment',
                #         'view_mode': 'form',
                #         'res_id': statement.id,
                #         'views': [(False, 'form')],
                #     }
            else:
                raise ValidationError(_("Formato de archivo no soportado!!"))

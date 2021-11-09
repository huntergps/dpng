
import re
#import xmlrpc.client as xmlrpclib

import sys
import argparse
import logging
import csv
from datetime import datetime
import erppeek
#from erppeek import Client
import requests
import json
import os
import math


_logger = logging.getLogger(__name__)
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')



def theos_get_data_api(url):
    response = requests.get(url)
    jdata = None
    if response.status_code == 200:
        jdata= json.loads(response.content.decode('utf-8'))
    return jdata



ODOO_DATABASE = 'dpng'
ODOO_SERVER = 'http://localhost:8069'
ODOO_USER='admin'
ODOO_USER_CLAVE = '123'

THEOS_API_URL = "http://facturas.galapagos.gob.ec:81/vERP_2_dat_dat/v1/"
THEOS_SERVICIOS = "art_m"
THEOS_API_KEY = "api_key=1234"

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PRODUCT_IMAGE = os.path.join(THIS_FOLDER, 'icon.png')

TIPOS_NOMINA={
    'N':'NOMINA NORMAL',
    'D':'DECIMO TERCERO Y/O CUARTO MENSUALIZADOS',
    'C':'DECIMO CUARTO ANUAL LOSEP Y OTRAS LEYES',
    'F':'FONDO DE RESERVA',
    'S':'SUBROGACION Y/O ENCARGOS',
    'L':'LIQUIDACION DE HABERES PENDIENTED',

}

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

def get_id_local_record(odoo_obj,id_theos):
    odoo_ids = odoo_obj.browse([('id_theos', '=', id_theos)])
    odoo_id = odoo_ids and odoo_ids[0] or False
    return odoo_id


def get_theos_png_records(odoo_obj,theos_resource,pagina=1):
    jdata = theos_get_data_api(THEOS_API_URL+theos_resource+'?'+THEOS_API_KEY+'&page[number]='+str(pagina))
    data=[]
    mdata=jdata[theos_resource]
    h = [str(x['id']) for x in mdata]
    odoo_obj_ids = odoo_obj.browse([('id_theos', 'in', h)])
    h2 =sorted(set(odoo_obj_ids.mapped("id_theos")))
    h3 = [x for x in mdata if str(x['id']) not in h2]
    return h3,jdata['total_count']


def import_gob_rol_theos_png(odoo_obj,theos_resource):
    jdata,total_count = get_theos_png_records(odoo_obj,theos_resource)

    pos=0
    for rec in jdata:
        pos+=1
        print(rec)
        try:
            vals={
                'name':rec['name'],
                'id_theos':rec['id'],
                'ejercicio':rec['eje_c'],
                'periodo':rec['periodo'],
            }
            odoo_id_new = odoo_obj.create(vals)
            print("%s > %s - %s [creado]"%(pos,rec['name'],rec['id']))
        except Exception as e:
            print("%s > %s - %s [NO creado]"%(pos,rec['name'],rec['id']))
            _logger.error(e)
            print(e)


def import_gob_rol_rubros_theos_png(odoo_obj,theos_resource):
    jdata,total_count = get_theos_png_records(odoo_obj,theos_resource)
    pos=0
    for rec in jdata:
        pos+=1
        print(rec)
        rubro_codigo_ids = odoo_obj.browse([('rubro_codigo', '=', rec['id'])])
        rubro_codigo_id = rubro_codigo_ids and rubro_codigo_ids[0] or False
        if not rubro_codigo_id:
            try:
                vals={
                    'name':rec['name'],
                    'rubro_codigo':rec['id'],
                    'cod_deduc':rec['cod_deduc'],
                    'rubro_tipo':rec['tip_rub_pub'],
                    'id_theos':rec['id'],
                }
                odoo_id_new = odoo_obj.create(vals)
                print("%s > %s - %s [creado]"%(pos,rec['name'],rec['id']))
            except Exception as e:
                print("%s > %s - %s [NO creado]"%(pos,rec['name'],rec['id']))
                _logger.error(e)
                print(e)
        else:
            # rubro_codigo_id = odoo_obj.browse(rubro_codigo_id)
            rubro_codigo_id.write({'id_theos':rec['id']})

def import_gob_nomina_theos_png(odoo_obj,theos_resource,roles_lista_ids):
    jdata,total_count = get_theos_png_records(odoo_obj,theos_resource)

    pos=0
    roles_odoo_obj = client.model('gob.roles.pagos')
    for rec in jdata:
        pos+=1
        print(rec)
        # print(rec['fch_cur'][:10])
        # fecha = datetime.strptime(rec['fch_cur'][:10], '%Y-%m-%d')
        # print(fecha)
        rol_id=roles_odoo_obj.browse(roles_lista_ids[rec['gob_rol']])
        print(rol_id)
        vals={
            'name':rec['name'],
            'id_theos':rec['id'],
            'cur_fecha':rec['fch_cur'][:10],
            'cur_nro':rec['nro_cur'],
            'id_spring':rec['id_nomina'],
            'ejercicio':rol_id.ejercicio,
            'periodo':rol_id.periodo,
            'tipo_nomina':TIPOS_NOMINA[rec['tip_rol_pub']] if len(rec['tip_rol_pub'])>0 else 'NO ESPECIFICADO',
            'rol_id':rol_id.id,
        }

        try:
            odoo_id_new = odoo_obj.create(vals)
            print("%s > %s - %s [creado]"%(pos,rec['name'],rec['id']))
        except Exception as e:
            print("%s > %s - %s [NO creado]"%(pos,rec['name'],rec['id']))
            _logger.error(e)
            print(e)


def get_odoo_roles_theos_id(mdata):
    h = [str(x['gob_rol']) for x in mdata]
    odoo_obj = client.model('gob.roles.pagos')
    odoo_records={}
    for rec in odoo_obj.browse([('id_theos', 'in', h)]):
        if rec.id_theos:
            odoo_records[int(rec.id_theos)]=rec.id
    return odoo_records


def import_gob_rol_det_theos_png(odoo_obj,theos_resource):
    tam_pagina=1000
    pagina=1
    jdata,total_count = get_theos_png_records(odoo_obj,theos_resource,pagina)
    import_gob_rol_det_theos_png_ciclo(odoo_obj,theos_resource,jdata)
    pagina_total = math.ceil(total_count/tam_pagina)
    pagina=2
    if pagina_total>1:
        while pagina < pagina_total:
            print(" ***** import_gob_rol_det_theos_png ciclo ***** %s => %s"%(pagina,pagina_total))
            jdata,total_count = get_theos_png_records(odoo_obj,theos_resource,pagina)
            import_gob_rol_det_theos_png_ciclo(odoo_obj,theos_resource,jdata)
            pagina+=1


def import_gob_rol_det_theos_png_ciclo(odoo_obj,theos_resource,jdata):

    pos=0
    roles_lista_ids=get_odoo_roles_theos_id(jdata)
    roles_odoo_obj = client.model('gob.roles.pagos')
    partner_odoo_obj = client.model('res.partner')
    params=''
    for rec in jdata:
        pos+=1
        rol_id=roles_odoo_obj.browse(roles_lista_ids[rec['gob_rol']])
        partner_id=get_id_local_record(partner_odoo_obj,rec['ent_m'])
        # print(partner_id)
        if not partner_id:
            params+='filter[id]=%s&'%rec['ent_m']
            continue

        name = 'Rol de Pagos %s %s - %s %s'%( MESES[rol_id.periodo],rol_id.ejercicio,partner_id.vat,partner_id.name)
        vals={
            'id_theos':rec['id'],
            'partner_id':partner_id.id,
            'nro_documento':partner_id.vat,
            'apellidos_nombres':partner_id.name,
            'ejercicio':rol_id.ejercicio,
            'periodo':rol_id.periodo,
            'rol_id':rol_id.id,
            'name':name,
        }
        try:
            odoo_id_new = odoo_obj.create(vals)
            print("%s > %s - %s [creado]"%(pos,name,rec['id']))
        except Exception as e:
            print("%s > %s - %s [NO creado]"%(pos,name,rec['id']))
            _logger.error(e)
            print(e)

    if params:
        update_id_sia_empleados(params)

def get_odoo_detail_theos_id(mdata):
    h = [str(x['gob_det_rol']) for x in mdata]
    odoo_obj = client.model('gob.roles.det')
    odoo_records={}
    for rec in odoo_obj.browse([('id_theos', 'in', h)]):
        if rec.id_theos:
            try:
                odoo_records[int(rec.id_theos)]=rec.id
            except Exception as e:
                odoo_records[rec.id_theos]=rec.id

    return odoo_records



def import_gob_rol_det_line_theos_png(odoo_obj,theos_resource,rubros_lista_ids):
    tam_pagina=1000
    pagina=1
    jdata,total_count = get_theos_png_records(odoo_obj,theos_resource,pagina)
    import_gob_rol_det_line_theos_png_ciclo(odoo_obj,theos_resource,jdata,rubros_lista_ids)
    pagina_total = math.ceil(total_count/tam_pagina)
    pagina=2
    if pagina_total>1:
        while pagina <= pagina_total:
            print(" ***** import_gob_rol_det_theos_png ciclo ***** %s => %s"%(pagina,pagina_total))
            jdata,total_count = get_theos_png_records(odoo_obj,theos_resource,pagina)
            import_gob_rol_det_line_theos_png_ciclo(odoo_obj,theos_resource,jdata,rubros_lista_ids)
            pagina+=1



def import_gob_rol_det_line_theos_png_ciclo(odoo_obj,theos_resource,jdata,rubros_lista_ids):

    pos=0
    detail_lista_ids=get_odoo_detail_theos_id(jdata)
    for rec in jdata:
        pos+=1


        try:
            val_line={
                'id_theos':rec['id'],
                'rubro_id':rubros_lista_ids[rec['gob_rub']],
                'detail_id':detail_lista_ids[rec['gob_det_rol']],
                'amount_calc':rec['monto_calc'],
                'amount_desc':rec['monto_desc'],
                'amount_pend':0.0,
                }
            odoo_id_new = odoo_obj.create(val_line)
            print("%s > %s - %s [creado]"%(pos,rec['gob_rub'],rec['id']))
        except Exception as e:
            print("%s > %s - %s [NO creado]"%(pos,rec['gob_rub'],rec['id']))
            _logger.error(e)
            print(e)



def get_odoo_theos_id(odoo_obj):
    odoo_obj_ids = odoo_obj.search([('id_theos','=?',None)])
    odoo_records={}
    for rec in odoo_obj.browse(odoo_obj_ids): #.filtered(lambda r: r.id_theos!=False):
        if rec.id_theos:
            odoo_records[int(rec.id_theos)]=rec.id
    return odoo_records

def get_odoo_theos_id_char(odoo_obj):
    odoo_obj_ids = odoo_obj.search([('id_theos','=?',None)])
    odoo_records={}
    for rec in odoo_obj.browse(odoo_obj_ids): #.filtered(lambda r: r.id_theos!=False):
        if rec.id_theos:
            odoo_records[rec.id_theos]=rec.id
    return odoo_records


def update_id_sia_empleados(custom_params):
    theos_resource='ent_m'
    partner_obj = client.model('res.partner')
    params =''
    if not custom_params:
        for p in partner_obj.browse([('guardaparque','=',True)]):
            if not p.id_theos:
                params+='filter[cif]=%s&'%p.vat
    else:
        params=custom_params
    if params:
        url=THEOS_API_URL+theos_resource+'?'+params+THEOS_API_KEY
        print(url)
        jdata = theos_get_data_api(url)
        for rec in jdata[theos_resource]:
            odoo_ids = partner_obj.browse([('vat', '=', rec['cif'][:10])])
            odoo_id = odoo_ids and odoo_ids[0] or False
            # print(odoo_id)
            if odoo_id:
                odoo_id.write({'id_theos':rec['id']})



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script de importacion de Productos')
    print(70*"==")
    print(' IMPORTACION DE DATOS DESDE THEOS DPNG')
    print(70*"==")
    # Conectamos con el server
    client = erppeek.Client(ODOO_SERVER, db=ODOO_DATABASE, user=ODOO_USER, password=ODOO_USER_CLAVE, verbose=False)
    # Modelos a utilizar
    product_obj = client.model('product.product')
    product_uom_unit = client.model(name='uom.uom').browse([('id','=',1)])[0]
    product_categories = client.model(name='product.category').browse([('id','>',4)])
    print(70*"==")
    print(' IMPORTACION DE ROLES DESDE THEOS DPNG')
    print(70*"==")
    roles_odoo_obj = client.model('gob.roles.pagos')
    rubros_odoo_obj = client.model('gob.roles.rubros')
    nominas_odoo_obj = client.model('gob.roles.nominas')
    rol_detalles_odoo_obj = client.model('gob.roles.det')
    rol_detalles_line_odoo_obj = client.model('gob.roles.det.lin')
    print(70*"==")

    import_gob_rol_theos_png(roles_odoo_obj,'gob_rol')          #activar para importar
    import_gob_rol_rubros_theos_png(rubros_odoo_obj,'gob_rub')
    rubros_lista_ids=get_odoo_theos_id_char(rubros_odoo_obj)

    roles_lista_ids=get_odoo_theos_id(roles_odoo_obj)           #activar para importar
    # print(roles_lista_ids)
    import_gob_nomina_theos_png(nominas_odoo_obj,'gob_nom_rol',roles_lista_ids) #activar para importar
    # nomina_lista_ids=get_odoo_theos_id(nominas_odoo_obj)
    # print(nomina_lista_ids)
    # update_id_sia_empleados(False)
    import_gob_rol_det_theos_png(rol_detalles_odoo_obj,'gob_det_rol')          #activar para importar
    import_gob_rol_det_line_theos_png(rol_detalles_line_odoo_obj,'gob_lin_rol',rubros_lista_ids)

    # detalles_lista_ids=get_odoo_theos_id(rol_detalles_odoo_obj)
    # print(detalles_lista_ids)

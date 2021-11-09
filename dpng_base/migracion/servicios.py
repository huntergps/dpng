
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
THEOS_API_KEY = "?api_key=1234"

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PRODUCT_IMAGE = os.path.join(THIS_FOLDER, 'icon.png')



def get_id_local_emission_point(code):
    emission_point_obj=client.model(name='l10n_ec_invoice.autorizacion')
    emission_point_ids = emission_point_obj.search([('id_theos', '=', code)])
    emission_point_id = emission_point_ids and emission_point_ids[0] or False
    return emission_point_id

def get_id_local_emission_point_by_point(l10n_ec_entity,l10n_ec_emission):
    emission_point_obj=client.model(name='l10n_ec_invoice.autorizacion')
    emission_point_ids = emission_point_obj.search([('l10n_ec_emission', '=', l10n_ec_emission),('l10n_ec_entity','=',l10n_ec_entity)])
    emission_point_id = emission_point_ids and emission_point_ids[0] or False
    return emission_point_id

def import_emission_point_theos_png():
    RESOURCE = 'pto_emi_g'
    jdata = theos_get_data_api(THEOS_API_URL+RESOURCE+THEOS_API_KEY)
    id = code_emission_point_parent = False
    pos=0
    for rec in jdata[RESOURCE]:
        pos+=1
        emission_point_obj=client.model(name='l10n_ec_invoice.autorizacion')
        emission_point_id = get_id_local_emission_point_by_point(rec['estab'],rec['ptoemi'])
        vals={
            'name':rec['name'],
            'l10n_ec_entity':rec['estab'],
            'l10n_ec_emission':rec['ptoemi'],
            'para_patentes':rec['tc_patentes'],
            'id_theos':rec['id']
        }
        if not emission_point_id:
            try:
                emission_point_id_new = emission_point_obj.create(vals)
                print("%s > %s - %s [creado emission_point_obj ]"%(pos,rec['name'],rec['id']))
            except Exception as e:
                _logger.error(">>>>>> emission_point_obj %s no se pudo crear.", rec['name'])
                _logger.error(e)
                print(e)
        else:
            emission_point_id.write(vals)




def get_id_local_cat(code):
    cat_obj=client.model(name='product.category')
    cat_ids = cat_obj.search([('codigo', '=', code)])
    cat_id = cat_ids and cat_ids[0] or False
    return cat_id


def import_cat_theos_png():
    RESOURCE = 'fam_m'
    jdata = theos_get_data_api(THEOS_API_URL+RESOURCE+THEOS_API_KEY)
    # print(jdata)
    id = code_cat_parent = False
    pos=0
    for rec in jdata[RESOURCE]:
        pos+=1
        cat_obj=client.model(name='product.category')
        code_cat = rec['id']
        cat_ids = cat_obj.search([('codigo', '=', code_cat)])
        cat_id = cat_ids and cat_ids[0] or False
        print('code_cat >>> ',code_cat,'   cat_id >>>> ',cat_id)

        if not cat_id:
            try:
                vals={
                    'name':rec['name'],
                    'codigo':code_cat,
                    'id_theos':code_cat
                }
                # if code_product in ('0801'):
                #     vals['balcon_ok'] = True

                if len(code_cat)==4:
                    code_cat_parent=code_cat[2:]
                if len(code_cat)==6:
                    code_cat_parent=code_cat[4:]
                if code_cat_parent:
                    code_cat_parent_id = get_id_local_cat(code_cat_parent)
                    if code_cat_parent_id:
                        vals['parent_id'] = code_cat_parent_id
                print(vals)
                cat_id_new = cat_obj.create(vals)
                print("%s > %s - %s [creado]"%(pos,cat_id['name'],code_cat))
            except Exception as e:
                _logger.error(">>>>>> Categoria %s no se pudo crear.", code_cat)
                _logger.error(e)
                print(e)




def get_image(PRODUCT_IMAGE):
    try:
        with open(PRODUCT_IMAGE, 'rb') as f:
            data = base64.b64encode(f.read())
            image = data
        return image
    except Exception as e:
        raise UserError('%s'%e)


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
    categorias={}
    for cat in product_categories:
        categorias[cat.codigo]=cat.id
    print(categorias)
    print(70*"==")
    print(' IMPORTACION DE CATEGORIAS DESDE THEOS DPNG')
    print(70*"==")
    import_cat_theos_png()
    print(70*"==")

    pos=0
    response = requests.get(THEOS_API_URL+THEOS_SERVICIOS+THEOS_API_KEY)
    if response.status_code == 200:
        jdata= json.loads(response.content.decode('utf-8'))
        # print(jdata)
        for p in jdata['art_m']:
            pos+=1
            print(p)
            code_product=str(p['ref']).strip()
            product_ids = product_obj.search([('default_code', '=', code_product)])
            product_id = product_ids and product_ids[0] or False
            # print('<%s>'%p['fam'])
            print(categorias)
            cat_id=categorias[p['fam']] if len(p['fam'])>0 else categorias['02']
            vals={
                'name':p['name'],
                'default_code':code_product,
                'barcode':code_product,
                'list_price':p['pvp'],
                'uom_id': product_uom_unit.id,
                'uom_po_id': product_uom_unit.id,
                'purchase_ok':False,
                'type':'service',
                'sale_ok':True,
                'categ_id':cat_id,
                'taxes_id':[],
                'supplier_taxes_id':[],
            }
            if code_product in ('119','120','121','122','123','124','125','127','128','129','130'):
                vals['balcon_ok']=True
            if code_product in ('119','120','121','122','123','129'):
                vals['extranjero']=True

            if code_product in ('120','122','125'):
                vals['menor_edad']=True

            if code_product in ('121','122'):
                vals['mercosur']=True

            if not product_id:
                try:
                    product_id_n = product_obj.create(vals)
                    product_id=product_id_n.id
                    print("%s > %s - %s [creado]"%(pos,p['name'],code_product))
                except Exception as e:
                    _logger.error(">>>>>> Producto %s no se pudo crear.", code_product)
                    _logger.error(e)
                    print(e)
            else:
                print('product_id  >> ',product_id)
                product= product_obj.browse([('id','=',product_id)])[0]
                product.write(vals)
                print("%s > %s - %s [existe]"%(pos,p['name'],code_product))

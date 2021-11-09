
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



ODOO_DATABASE = 'odoo15'
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
            emission_point_id_wr=emission_point_obj.browse([('id','=',emission_point_id)])
            emission_point_id_wr.write(vals)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script de importacion de Productos')
    print(70*"==")
    print(' IMPORTACION DE DATOS DESDE THEOS DPNG')
    print(70*"==")
    # Conectamos con el server
    client = erppeek.Client(ODOO_SERVER, db=ODOO_DATABASE, user=ODOO_USER, password=ODOO_USER_CLAVE, verbose=False)
    # Modelos a utilizar
    print(70*"==")
    print(' IMPORTACION DE import_emission_point_theos_png DESDE THEOS DPNG')
    print(70*"==")
    import_emission_point_theos_png()
    print(70*"==")

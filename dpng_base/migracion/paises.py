
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
THEOS_PAIS = "pai_m"
THEOS_API_KEY = "?api_key=1234"

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PRODUCT_IMAGE = os.path.join(THIS_FOLDER, 'icon.png')

def get_id_country_bye_code(code):
    country_obj=client.model(name='res.country')
    country_ids = country_obj.search([('code', '=', code)])
    country_id = country_ids and country_ids[0] or False
    return country_id

def get_id_country_bye_theos(id_theos):
    country_obj=client.model(name='res.country')
    country_ids = country_obj.search([('id_theos', '=', id_theos)])
    country_id = country_ids and country_ids[0] or False
    return country_id



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script de importacion de Productos')
    print(70*"==")
    print(' IMPORTACION DE DATOS DESDE THEOS DPNG')
    print(70*"==")
    # Conectamos con el server
    client = erppeek.Client(ODOO_SERVER, db=ODOO_DATABASE, user=ODOO_USER, password=ODOO_USER_CLAVE, verbose=False)
    # Modelos a utilizar
    pais_obj = client.model('res.country')

    print(70*"==")
    print(' IMPORTACION DE PAISES DESDE THEOS DPNG')
    print(70*"==")

    pos=0

    response_paises = theos_get_data_api(THEOS_API_URL+THEOS_PAIS+THEOS_API_KEY)
    # if response_facturas.status_code == 200:
    if response_paises:
        for p in response_paises['pai_m']:
            pos+=1
            print(p)
            code_pais=str(p['iso_2']).strip()
            pais_id = get_id_country_bye_code(code_pais)
            print(pais_id)
            #
            # vals={
            #     'id_theos':p['iso_2']
            # }
            #
            if not pais_id:
                try:
                    pais_id_n = pais_obj.create({'name':p['name'],'code':p['iso_2'],'currency_id':2,'id_theos':p['id']})
                    pais_id=pais_id_n.id
                    print("%s > %s - %s [creado]"%(pos,p['name'],p['iso_2']))
                except Exception as e:
                    _logger.error(">>>>>> Pais %s no se pudo crear.", p['name'])
                    _logger.error(e)
                    print(e)
            else:
                print('pais_id  >> ',pais_id)
                pais= pais_obj.browse([('id','=',pais_id)])[0]
                pais.write({'id_theos':p['id']})
                print("%s > %s - %s [existe]"%(pos,p['name'],p['name']))

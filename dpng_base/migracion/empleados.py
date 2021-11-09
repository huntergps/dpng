
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



def odoo_get_user(conexion, partner_id):
    user_obj = conexion.model('res.users')
    user_obj_id=None
    user_obj_ids = user_obj.search([('partner_id', '=', partner_id)])
    user_obj_id = user_obj_ids and user_obj_ids[0] or False
    return user_obj_id

def odoo_create_user(conexion, vals):
    user_obj = conexion.model('res.users')
    user_obj_id = odoo_get_user(conexion, vals['partner_id'])
    if not user_obj_id:
        user_obj_id= user_obj.create(vals)
        return user_obj_id
    else:
        return user_obj.browse(user_obj_id)


def odoo_get_partner(conexion, p_vat):
    partner_obj = conexion.model('res.partner')
    partner_obj_id=None
    partner_obj_ids = partner_obj.search([('vat', '=', p_vat)])
    partner_obj_id = partner_obj_ids and partner_obj_ids[0] or False
    return partner_obj_id



def odoo_create_entidad_user(conexion, record):
    vals_prov = {}
    table_obj = conexion.model('res.partner')
    mrecord = None
    razonSocial= record['name'].upper()
    identificacion = record['vat'].upper()
    email=''
    account_payment_term_immediate = conexion.model("account.payment.term").get('account.account_payment_term_immediate')

    if record["email"]:
        if email:
            email += ','
        email += record["email"]

    vals_prov['sia_id']= identificacion
    vals_prov['name']=razonSocial
    vals_prov['vat']=identificacion
    vals_prov['customer_rank']=1
    vals_prov['supplier_rank']=0
    vals_prov['street']=record["dir"]
    vals_prov['email']=email
    vals_prov['phone']=record["fono"]
    vals_prov['guardaparque']=True

    # vals_prov['city']=record['ciudad']
    vals_prov['property_payment_term_id'] = account_payment_term_immediate
    vals_prov['property_supplier_payment_term_id'] = account_payment_term_immediate
    mrecord = table_obj.create(vals_prov)
    # print("*** CREO ENTIDAD PARA USUARIO ***")
    return mrecord



ODOO_DATABASE = 'dpng'
ODOO_SERVER = 'http://localhost:8069'
ODOO_USER='admin'
ODOO_USER_CLAVE = '123'

THEOS_API_URL = "http://facturas.galapagos.gob.ec:81/vERP_2_dat_dat/v1/"
THEOS_SERVICIOS = "art_m"
THEOS_API_KEY = "?api_key=1234"

SIA_JWT_URL='https://sia.galapagos.gob.ec:8007/api/v1'
SIA_JWT_USERNAME='sysadmin'
SIA_JWT_PASSWORD='Dpng#$IA.2021'
# SIA_JWT_PASSWORD='sys4dm1n'

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PRODUCT_IMAGE = os.path.join(THIS_FOLDER, 'icon.png')

def get_sia_jwt_auth_token():
    url=SIA_JWT_URL+'/api-token-auth-jwt/'
    url=url.replace('1//a','1/a')
    payload = json.dumps({
      "username": SIA_JWT_USERNAME,
      "password": SIA_JWT_PASSWORD
    })
    headers = {
      'Content-Type': 'application/json'
    }
    # print("*"*50)
    # print("**** get_sia_jwt_auth_token *****")
    # print(url)
    # print(headers)
    # print(payload)
    # print("*"*50)
    response = requests.request("POST", url, headers=headers, data=payload)
    jdata = False
    # print(response.text)
    if response.status_code == 200:
        jdata= json.loads(response.content.decode('utf-8'))
        print(jdata['success'])
        if  jdata['success']==True:
            return jdata['session_token']
    return jdata

def odoo_get_company(conexion, id):
    partner_obj = conexion.model('res.company').browse(id)
    return partner_obj

def get_empleados_sia(client,logger):
    company_id = 1
    url=SIA_JWT_URL+'/perfuncionario_list2/'
    url=url.replace('1//p','1/p')
    payload={}
    authorization ='PNG %s'%get_sia_jwt_auth_token()
    print(authorization)
    headers = {
      'Authorization': authorization
    }
    print("*"*50)
    print("**** get_empleados_sia *****")
    print(url)
    print(headers)
    print(payload)
    print("*"*50)
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response)
    jdata = False
    no_creados=[]
    if response.status_code == 200:
        jdata= json.loads(response.content.decode('utf-8'))
        posi=0
        total_posi=jdata['count']
        if  jdata['count']>0:
            jusers=jdata['results']
            for user in jusers:
                # if user['estado']!='A':
                #     continue
                user_id=user['id']
                email=user['email'] or ''
                fono=user['telefonos_contacto'] or ''
                dir=user['direccion_domicilio'] or ''
                persona_user=user['persona_id']
                if persona_user['apellidos'] and persona_user['nombres']:
                    name=persona_user['apellidos']+' '+persona_user['nombres']
                else:
                    name=persona_user['nombre_completo']

                vat=persona_user['identificacion'] or ''
                record_partner={
                    'vat':vat,
                    'name':name,
                    'dir':dir,
                    'fono':fono,
                    # 'ciudad':ciudad,
                    'email':email,
                    }
                partner_id=odoo_get_partner(client,vat)
                if not partner_id:
                    try:
                        odoo_create_entidad_user(client, record_partner)
                        print("%s => %s = %s > %s [creado]"%(total_posi,posi,vat,name))
                    except Exception as e:
                        logger.error(e)
                        print("%s => %s = %s > %s [fallo]"%(total_posi,posi,vat,name))
                        print(e)
                else:
                    print("%s en %s => %s = [existe]"%(total_posi,posi,vat))
                if user['estado']=='A':
                    user_partner_id = odoo_get_partner(client,vat)
                    user_id= False
                    if user_partner_id and email:
                        vals_user={
                            'partner_id':user_partner_id,
                            'login':email,
                            'company_id':company_id,
                            'notification_type':'inbox',
                            'password':vat
                            }
                        # print("*** CREA USER ***")
                        try:
                            salesman_id = odoo_create_user(client,vals_user)
                        except Exception as e:
                            print(vals_user)
                            print(e)
                            no_creados.append(vals_user)
                            # raise

                posi+=1
            print(len(jusers))
            if no_creados!=[]:
                print("*"*60)
                print("* USUARIOS NO CREADOS ")
                print(no_creados)
                print("*"*60)
                # print(user['id'],'>>>>',user['persona_id'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script de importacion de Productos')
    print(70*"==")
    print(' IMPORTACION DE DATOS DESDE THEOS DPNG')
    print(70*"==")
    # Conectamos con el server
    client = erppeek.Client(ODOO_SERVER, db=ODOO_DATABASE, user=ODOO_USER, password=ODOO_USER_CLAVE, verbose=False)
    # Modelos a utilizar
    # print(70*"==")
    # print(' IMPORTACION DE EMPLEADOS DESDE THEOS DPNG')
    # print(70*"==")
    get_empleados_sia(client,_logger)

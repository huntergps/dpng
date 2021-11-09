# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields
import requests, json


class ResCompany(models.Model):
    _inherit = "res.company"

    sia_jwt_url = fields.Char('SIA Api URL')
    sia_jwt_username = fields.Char('SIA Api Usuario')
    sia_jwt_password = fields.Char('SIA Api Clave')

    def get_sia_jwt_auth_token(self):
        url=self.sia_jwt_url+'/api-token-auth-jwt/'
        url=url.replace('1//a','1/a')
        payload = json.dumps({
          "username": self.sia_jwt_username,
          "password": self.sia_jwt_password
        })
        headers = {
          'Content-Type': 'application/json'
        }
        print("*"*50)
        print("**** get_sia_jwt_auth_token *****")
        print(url)
        print(headers)
        print(payload)
        print("*"*50)
        response = requests.request("POST", url, headers=headers, data=payload)
        jdata = False
        print(response.text)
        if response.status_code == 200:
            jdata= json.loads(response.content.decode('utf-8'))
            if  jdata['success']==True:
                return jdata['session_token']
        return jdata

    def get_empleados_sia(self):
        url=self.sia_jwt_url+'/perfuncionario_list/'
        url=url.replace('1//p','1/p')
        payload={}
        authorization ='PNG %s'%self.get_sia_jwt_auth_token()
        headers = {
          'Authorization': authorization
        }
        print("*"*50)
        print("**** get_empleados_sia *****")
        print(url)
        print(headers)
        print(payload)
        print("*"*50)
        # response = requests.request("GET", url, headers=headers, data=payload)
        # jdata = False
        # if response.status_code == 200:
        #     jdata= json.loads(response.content.decode('utf-8'))
        #     if  jdata['count']>0:
        #         jusers=jdata['results']
        #         for user in jusers:
        #             user_id=user['id']
        #             persona_user=user['persona_id']
        #             name=persona_user['apellidos']+' 'persona_user['apellidos']
        #             print(user['id'],'>>>>',user['persona_id'])
        #             # obj_user=self.env['res.partner'].search([('vat','=')])
        #             #

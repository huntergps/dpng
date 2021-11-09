# -*- coding: utf-8 -*-
import base64
import logging
import os
import io
import pathlib
import subprocess
import tempfile
import xml
from collections import OrderedDict
from datetime import datetime
from random import randrange

from lxml import etree as e
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

_logger = logging.getLogger(__name__)



try:
    import xmltodict
except ImportError:
    _logger.error(
        "The module xmltodict can't be loaded, try: pip install xmltodict")
"""
try:
    from suds.client import Client
except ImportError:
    logging.getLogger('xades.sri').info('Intente pip3 install suds-jurko')
"""

try:
    from zeep import Client
except ImportError:
    _logger.warning("The module zeep can't be loaded, try: pip install zeep")


try:
    from barcode import generate
    from barcode.writer import ImageWriter
except ImportError:
    _logger.warning(
        "The module viivakoodi can't be loaded, try: pip install viivakoodi")




class SriDocumentoElectronico(models.Model):
    _name = 'l10n_ec_invoice.documento.electronico'
    _description ='Documento Electronico'


    def name_get(self):
        return [(documento.id, '%s %s' % (documento.claveacceso, documento.estado)) for documento in self]

    @api.model
    def create(self, vals):
        res = super(SriDocumentoElectronico, self).create(vals)
        if not res:
            return
        print("passsss!!!!")
        line = self.env['l10n_ec_invoice.documento.electronico.queue.line']
        print(line)

        vals_cola={
            'reference':self.reference,
            'queue_id': self.env.ref('l10n_ec_invoice.documento_electronico_queue').id,
            'documento_electronico_id': res.id}
        line.create(vals_cola)

        return res

    def replace_in_cola(self,reference):
        print("entra * replace_in_cola * ")
        line = self.env['l10n_ec_invoice.documento.electronico.queue.line']
        lines_hay = line.search([('documento_electronico_id','=',self.id)])
        print(lines_hay)
        print(reference)
        if not lines_hay:
            vals_cola={
                'reference':reference,
                'queue_id': self.env.ref('l10n_ec_invoice.documento_electronico_queue').id,
                'documento_electronico_id': self.id}
            print(vals_cola)
            line.create(vals_cola)

    def validate_xsd_schema(self, xml, xsd_path):
        """

        :param xml: xml codificado como utf-8
        :param xsd_path: /dir/archivo.xsd
        :return:
        """

        xsd_path = os.path.join(__file__, "../..", xsd_path)
        xsd_path = os.path.abspath(xsd_path)

        xsd = open(xsd_path)
        schema = e.parse(xsd)
        xsd = e.XMLSchema(schema)

        xml = e.XML(xml)

        try:
            xsd.assertValid(xml)
            return True,''
        except Exception as err:
            print(err)
            _msn_error="%s"%err
            _msn_error=_msn_error.replace('Element','Elemento XML ').replace(', line',' en la linea').replace('The value','\n').replace('is not accepted by the pattern','\nNO CUMPLE la restricción')
            _msn_error=_msn_error.replace("[facet 'pattern'] ","").replace("'[^\\n]*'.","NO SE ADMITE SALTOS DE LINEA '[^\\n]*'")
            return False,_msn_error


    def modulo11(self, clave):
        digitos = list(clave)
        nro = 6  # cantidad de digitos en cada segmento
        segmentos = [digitos[n:n + nro] for n in range(0, len(digitos), nro)]
        total = 0
        while segmentos:
            segmento = segmentos.pop()
            factor = 7  # numero inicial del mod11
            for s in segmento:
                total += int(s) * factor
                factor -= 1
        mod = 11 - (total % 11)
        if mod == 11:
            mod = 0
        elif mod == 10:
            mod = 1
        return mod


    def firma_xades_bes(self, xml, p12, clave):
        """

        :param xml: cadena xml
        :param clave: clave en formato base64
        :param p12: archivo p12 en formato base64
        :return:
        """

        jar_path = os.path.join(__file__, "../../src/xadesBes/firma.jar")
        jar_path = os.path.abspath(jar_path)
        cmd = ['java','-XX:MaxHeapSize=512m','-XX:CompressedClassSpaceSize=64m' ,'-jar', jar_path, xml,
        base64.b64encode(bytes(p12,'utf-8')).decode('ascii'),
        base64.b64encode(bytes(clave,'utf-8')).decode('ascii')
        ]

        try:
            subprocess.check_call(cmd)
            sp = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            res = sp.communicate()
            return res[0]
        except subprocess.CalledProcessError as se:
            _logger.exception('FIRMA ELECTRONICA FALLIDA: %s' % se.returncode)


    def enviar_doc(self):
        try:
            if self.send_de_backend():
                self.receive_de_offline()
        except Exception as e:
            return False


    def send_de_backend(self):
        """
        Envía el documento electrónico desde el backend
        para evitar demoras en caso de que el SRI se encuentre
        fuera de línea.

        """
        ambiente_id = self.env.user.company_id.ambiente_id
        #xml = self.xml_file #base64.b64decode(self.xml_file)
        xml = base64.b64decode(self.xml_file)
        envio = self.send_de_offline(ambiente_id, xml)
        if envio:
            self.write({
                'estado': envio['estado'],
                'mensajes': envio['comprobantes'] or '',
            })
            if envio['estado'] not in ('AUTORIZADO','RECIBIDA'):
                return False

            return True
        else:
            return False


    def check_service(self, URL):
        flag = False
        #for i in [1, 2, 3]:
        for i in [1, 2,]:
            try:
                res = requests.head(URL, timeout=3)
                flag = True
            except URLError:
                return flag, False
        return flag, res


    def send_de_offline(self, ambiente_id, xml):
        """
        :param ambiente_id: recordset del ambiente
        :param xml: documento xml en base 64
        :return: respuesta del SRI
        """
        client = Client(ambiente_id.recepcioncomprobantes)
        with client.settings(raw_response=False):
            response = client.service.validarComprobante(xml)
        return response


    def send_de_offline1(self, ambiente_id, document):
        """
        :param ambiente_id: recordset del ambiente
        :param xml: documento xml en base 64
        :return: respuesta del SRI
        """

        """
        try:
            mtest= self.check_service(ambiente_id.recepcioncomprobantes)
        except:
            errores.append('-10')
            errores.append('Servicio SRI no disponible.')
            errores.append('Error de comunicación.')
            return False, errores,'ERROR_ENVIO'
        if not mtest:
            errores.append('-11')
            errores.append('Fallo General Servicio SRI no disponible.')
            errores.append('Error de comunicación.')
            return False, errores,'ERROR_ENVIO'
        """
        #buf = StringIO()
        #buf.write(document)
        errores = []


        try:
            print("====== CREAR cliente ======")
            client = Client(ambiente_id.recepcioncomprobantes)
            print("====== LLAMA A validarComprobante ======")
            with client.settings(raw_response=False):
                response = client.service.validarComprobante(document)
            #response = client.service.validarComprobante(document)
        except Exception as e:
            print(e)
            print('======>>>>>>>>>>>>>>>>>>>>>>>> ERROR >>>>>>',e)
            return None

        print("====== FIN DE validarComprobante ======")
        #print('Estado de respuesta documento: %s' % response.estado)
        # print(30*"==")
        # print("==  RESULT=>",response)
        return response

        """
        client = Client(ambiente_id.recepcioncomprobantes)
        with client.options(raw_response=False):
            response = client.service.validarComprobante(document)
        return response
        """


    def message_ride_sri(self, msn):
        try:
            html='<p><strong>DOCUMENTO ELECTRONICO</strong></p>'
            html+=msn
            print(html)
            self.reference.message_ride_sri(html)
        except:
            pass


    def receive_de_offline(self):
        ambiente_id = self.env.user.company_id.ambiente_id
        claveacceso = self.claveacceso

        print(40*"**")
        print("====== CREAR cliente >>> receive_de_offline ======")
        client = Client(ambiente_id.autorizacioncomprobantes)
        print("====== LLAMA A autorizacionComprobante ======")
        try:
            with client.settings(raw_response=False):
                response = client.service.autorizacionComprobante(claveacceso)
        except Exception as e:
            print(e)
            msn="<span style='color: #ff0000;'>ERROR SRI</span>"
            msn+="<p><span style='color: #ff0000;'>"+"%s"%(e)+"</span></p>"
            self.message_ride_sri(msn)

            return None

        #with client.options(raw_response=False):
        #    response = client.service.autorizacionComprobante(claveacceso)
        autorizaciones = None
        try:
            autorizaciones = response['autorizaciones']['autorizacion'][0]
        except Exception as e:
            self.write({
                'estado': 'ERROR TCP',
                'mensajes': ('%s  >>  %s')%(response,e)
            })
            msn="<span style='color: #ff0000;'>ERROR SRI</span>"
            msn+="<p><span style='color: #ff0000;'>"+"%s  \n  %s"%(response,e)+"</span></p>"
            self.message_ride_sri(msn)
            # return False

        if not autorizaciones and self.estado=='ERROR TCP':
            self.write({
                        'estado':'NO ENVIADO',
                        'mensajes':'Documento no enviado al SRI'
                        })
            return False

        if not autorizaciones:
            self.write({
                        'estado':'FAIL READ',
                        'mensajes':'Documento no devuelto por el SRI'
                        })
            msn="<span style='color: #cc3300;'>ADVERTENCIA SRI</span>"
            msn+="<p><span style='color: #cc3300;'>FAIL READ \n  Documento no devuelto por el SRI</span></p>"
            self.message_ride_sri(msn)

            self.message_ride_sri('Documento no devuelto por el SRI')
            return False
        else:
            print(5*'\n')
            print(autorizaciones)
            autorizacion = OrderedDict([
                ('autorizacion', OrderedDict([
                    ('estado', autorizaciones['estado']),
                    ('numeroAutorizacion', autorizaciones['numeroAutorizacion']),
                    ('fechaAutorizacion',  str(autorizaciones['fechaAutorizacion'])),
                    ('ambiente', autorizaciones['ambiente']),
                    ('comprobante', u'<![CDATA[{}]]>'.format(
                        autorizaciones['comprobante'])),
                ]))
            ])
            comprobante = xml.sax.saxutils.unescape(
                xmltodict.unparse(autorizacion))
            self.write({
                'estado': autorizaciones['estado'],
                'mensajes': autorizaciones['mensajes'],
                'xml_file': base64.b64encode(comprobante.encode('utf-8')),
                'fechaautorizacion': fields.Datetime.to_string(autorizaciones['fechaAutorizacion']),
            })
            print(50*"..")
            # Enviar correo si el documento es AUTORIZADO.
            msn1='Estados= %s/nNumero de Autorizacion=%s/nFecha%s/nAmbiente=%s'%(autorizaciones['estado'],autorizaciones['numeroAutorizacion'],str(autorizaciones['fechaAutorizacion']),autorizaciones['ambiente'])

            msn="<span style='color: #0057e7;'>MENSAJE SRI</span>"
            msn+="<p><span style='color: #0057e7;'>"+"%s"%(msn1)+"</span></p>"
            self.message_ride_sri(msn)


            if autorizaciones['estado'] == 'AUTORIZADO':
                try:
                    sent = self.reference.send_email_de()
                    # Si se envía, marcamos la línea como enviada.
                    if sent:
                        line_obj = self.env['l10n_ec_invoice.documento.electronico.queue.line']
                        line = line_obj.search([('documento_electronico_id','=', self.id)], limit=1)
                        line.sent = True
                except:
                    pass
            return True


    def get_documento_electronico_xml( self, ambiente_id, comprobante_id, documento, claveacceso, tipoemision, reference):
        xml = xmltodict.unparse(documento, pretty=False)
        xml = xml.encode('utf8')
        xsd_path = 'src/esquemasXsd/Factura_V_1_1_0.xsd'
        _es_valido= self.validate_xsd_schema(xml, xsd_path)
        if _es_valido:
            print("Es valido")
        else:
            print("No es valido")

        return xml


    def validate_xsd_schema_documento_electronico_dict( self,  documento,type_doc):
        xml = xmltodict.unparse(documento, pretty=False)
        xml = xml.encode('utf8')
        # Validamos el esquema.
        if type_doc=='out_invoice':
            xsd_path = 'src/xsd/factura_v1.0.0.xsd'
        elif type_doc=='out_refund':
            xsd_path = 'src/xsd/notaCredito_v1.0.0.xsd'
        elif type_doc=='in_invoice_ret':
            xsd_path = 'src/xsd/comprobanteRetencion_v1.0.0.xsd'
        elif type_doc=='stock_picking':
            xsd_path = 'src/xsd/guiaRemision_v1.0.0.xsd'
        _es_valido = False
        _msn_error=''
        if xsd_path:
            try:
                _es_valido,_msn_error = self.validate_xsd_schema(xml, xsd_path)
            except Exception as e:
                _msn_error="%s"%e
                print("****Exception ****")
                print(_msn_error)
                print(e)
        if _es_valido==False:
            return False,_msn_error
        return True, _msn_error


    def get_documento_electronico_dict( self, ambiente_id, comprobante_id, documento, claveacceso, tipoemision, reference,type_doc):

        xml = xmltodict.unparse(documento, pretty=False)
        xml = xml.encode('utf8')
        # Validamos el esquema.
        if type_doc=='out_invoice':
            xsd_path = 'src/xsd/factura_v1.0.0.xsd'
        elif type_doc=='out_refund':
            xsd_path = 'src/xsd/notaCredito_v1.0.0.xsd'
        elif type_doc=='in_invoice_ret':
            xsd_path = 'src/xsd/comprobanteRetencion_v1.0.0.xsd'
        elif type_doc=='stock_picking':
            xsd_path = 'src/xsd/guiaRemision_v1.0.0.xsd'
        _es_valido = False
        _msn_error=''
        if xsd_path:
            try:
                _es_valido,_msn_error = self.validate_xsd_schema(xml, xsd_path)
            except Exception as e:
                _msn_error="%s"%e
                print("****Exception ****")
                print(_msn_error)
                print(e)
        if _es_valido==False:
            return False,_msn_error

        firma = self.env.user.company_id.firma_id
        if not os.path.exists(firma.path):
            firma.write({
                'path': firma.save_sign(firma.p12),
            })
        errores = []
        estado_sri=''
        xml=xml.decode('utf-8').replace("\n","").encode('utf8')
        xml= self.firma_xades_bes(xml, firma.path, firma.clave)
        filename = ''.join([claveacceso, '.xml'])
        # Creamos el diccionario del documento electrónico.
        vals = {
            'xml_file': base64.b64encode(xml),
            'xml_filename': filename,
            'estado': 'NO ENVIADO',
            'mensajes': '',
            'ambiente': ambiente_id.ambiente,
            'tipoemision': tipoemision,
            'claveacceso': claveacceso,
            'reference': reference,
            'comprobante_id': comprobante_id.id,
        }
        return vals,_msn_error


    def get_claveacceso(self, id, fecha, comprobante, ruc, ambiente_id,establecimiento, puntoemision, secuencial):
        fecha = datetime.strptime(str(fecha), '%Y-%m-%d')
        data = [
            fecha.strftime('%d%m%Y'),
            str(comprobante),
            str(ruc),
            str(ambiente_id),
            str(establecimiento).zfill(3),
            str(puntoemision).zfill(3),
            str(secuencial).zfill(9),
            str(id).zfill(8),
            #str(randrange(1, 99999999)).zfill(8),
            '1',
        ]
        try:
            claveacceso = ''.join(data)
            claveacceso += str(self.modulo11(claveacceso))
        except:
            raise UserError(_(
                u"""
                *****************************************************
                * Falta informacion para generar la Clave de Acceso *
                *****************************************************
                fecha = %s,
                comprobante = %s,
                ruc = %s,
                ambiente = %s,
                establecimiento = %s,
                puntoemision = %s,
                secuencial = %s,
                nro aleatorio = %s,
                Tipo de emisión = %s,
                """ % tuple(data)))
        return claveacceso


    def _get_reference_models(self):
        records = self.env['ir.model'].search(
            ['|', ('model', '=', 'account.move'), ('model', '=', 'stock.picking')])
        val=[(record.model, record.name) for record in records] + [('', '')]
        print(val)
        return val

    reference = fields.Reference(
        string='Reference', selection='_get_reference_models')

    comprobante_id = fields.Many2one(
        'l10n_latam.document.type', string='Comprobante', copy=False, )

    tipoemision = fields.Selection(
        [
            ('1', 'Emisión normal'),
            ('2', 'Emisión por indisponibilidad del sistema'),
        ],
        string='Tipo de emisión', )

    ambiente = fields.Selection([
        ('1', 'Pruebas'),
        ('2', 'Producción'),
    ], string='Ambiente', )


    def get_barcode_128(self):
        if self.claveacceso:
            file_data = io.StringIO()
            generate('code128', u'{}'.format(self.claveacceso),
                     writer=ImageWriter(), output=file_data)
            file_data.seek(0)
            self.barcode128 = base64.encodestring(file_data.read())

    claveacceso = fields.Char('Clave de acceso', )
    barcode128 = fields.Binary('Barcode', compute=get_barcode_128)
    fechaautorizacion = fields.Datetime('Fecha y hora de autorización', )
    mensajes = fields.Text('Mensajes', )
    estado = fields.Selection([
        ('NO ENVIADO', 'NO ENVIADO'),  # Documentos fuera de línea.
        ('RECIBIDA', 'RECIBIDA'),
        ('EN PROCESO', 'EN PROCESO'),
        ('DEVUELTA', 'DEVUELTA'),
        ('AUTORIZADO', 'AUTORIZADO'),
        ('NO AUTORIZADO', 'NO AUTORIZADO'),
        ('ANULADA', 'ANULADA'),
        ('RECHAZADA', 'RECHAZADA'),
        ('CANCELADA', 'CANCELADA'),
        ('ERROR TCP','ERROR TCP'),
        ('ENVIADA CONTRIBUYENTE','ENVIADA AL CONTRIBUYENTE'),
    ])

    xml_file = fields.Binary('Archivo XML', attachment=True, readonly=True, )
    xml_filename = fields.Char('Filename', )

    def get_xml_render_info(self):
        # directory = os.path.normpath(os.path.normcase(os.path.join(config['path_electronic_import'],"render")))
        # print(directory)
        # pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        # file_to_write = os.path.normpath(os.path.normcase(os.path.join(directory,obj.data_filename)))
        # filew = open(file_to_write,'wb+')
        # filew.write(base64.b64decode(self.data_file))
        # filew.close()
        # auth= obj.read_xml(file_to_write)
        xml = base64.b64decode(self.xml_file)
        return xml

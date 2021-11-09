# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command, _
from odoo.addons.l10n_ec.models.res_partner import verify_final_consumer
from collections import defaultdict,OrderedDict

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime
import unicodedata  # para normalizar el nombre

_DOCUMENTS_MAPPING = {
    "01": [
        'ec_dt_01',
        'ec_dt_02',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_08',
        'ec_dt_09',
        'ec_dt_11',
        'ec_dt_12',
        'ec_dt_20',
        'ec_dt_21',
        'ec_dt_41',
        'ec_dt_42',
        'ec_dt_43',
        'ec_dt_45',
        'ec_dt_47',
        'ec_dt_48'
    ],
    "02": [
        'ec_dt_03',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_09',
        'ec_dt_19',
        'ec_dt_41',
        'ec_dt_294',
        'ec_dt_344'
    ],
    "03": [
        'ec_dt_03',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_09',
        'ec_dt_15',
        'ec_dt_19',
        'ec_dt_41',
        'ec_dt_45',
        'ec_dt_294',
        'ec_dt_344'
    ],
    "04": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_18',
        'ec_dt_41',
        'ec_dt_44',
        'ec_dt_47',
        'ec_dt_48',
        'ec_dt_49',
        'ec_dt_50',
        'ec_dt_51',
        'ec_dt_52',
        'ec_dt_370',
        'ec_dt_371',
        'ec_dt_372',
        'ec_dt_373'
    ],
    "05": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_18',
        'ec_dt_41',
        'ec_dt_44',
        'ec_dt_47',
        'ec_dt_48',
        'ec_dt_370',
        'ec_dt_371',
        'ec_dt_372',
        'ec_dt_373'
    ],
    "06": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_18',
        'ec_dt_41',
        'ec_dt_44',
        'ec_dt_47',
        'ec_dt_48',
        'ec_dt_370',
        'ec_dt_371',
        'ec_dt_372',
        'ec_dt_373'
    ],
    "07": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_18'
    ],
    "09": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_15',
        'ec_dt_16',
        'ec_dt_41',
        'ec_dt_47',
        'ec_dt_48',
    ],
    "20": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_15',
        'ec_dt_16',
        'ec_dt_41',
        'ec_dt_47',
        'ec_dt_48'
    ],
    "21": [
        'ec_dt_01',
        'ec_dt_04',
        'ec_dt_05',
        'ec_dt_15',
        'ec_dt_16',
        'ec_dt_41',
        'ec_dt_47',
        'ec_dt_48'
    ],
}



class AccountMove(models.Model):
    _inherit = "account.move"


    def normalize(self, s):
        if not s:
            return
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

    def normalize_date(self, date):
        if not date:
            return
        try:
            date=str(date)
            res = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            res = datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        return res

    @api.model
    def _get_l10n_ec_documents_allowed(self, identification_code):
        documents_allowed = self.env['l10n_latam.document.type']
        for document_ref in _DOCUMENTS_MAPPING.get(identification_code, []):
            document_allowed = self.env.ref('l10n_ec.%s' % document_ref, False)
            if document_allowed:
                documents_allowed |= document_allowed
        return documents_allowed


    #para poner mensajes de envio al SRI en la pantalla de la factura
    def message_ride_sri(self, html):
        self.sudo().message_post(body=html)

    def _get_report_base_filename(self):
        # if any(not move.is_invoice() for move in self):
        #     raise UserError(_("Only invoices could be printed."))
        return self._get_move_display_name()





    def _default_autorizacion_id(self):
        """
        Obtiene la autorización de comprobante por defecto dependiendo
        tipo de factura y el usuario tiene una autorización caso contrario
        se usa de la commpania
        """
        u = self.env.user
        c = self.env.company
        return u.autorizacion_id or c.autorizacion_id

    @api.depends('factura_electronica_id.estado','state')
    def _get_ce_state(self):
        for r in self:
            edoc = r.factura_electronica_id or False
            if edoc:
                r.ce_state = edoc.estado
            else:
                if r.state=='cancel':
                    r.cece_state ='ANULADA'
                else:
                    r.ce_state='SIN COMPROBANTE'
            return True


    factura_electronica_id = fields.Many2one(
        'l10n_ec_invoice.documento.electronico', ondelete='restrict',
        string="Factura electrónica", copy=False, )

    partner_id_vat = fields.Char(related='partner_id.vat', string='Identificacion', store=True)
    partner_id_vat_code = fields.Char(related='partner_id.l10n_latam_identification_type_id.code', string='Codigo SRI', store=True)
    partner_id_vat_tpidprov = fields.Char(related='partner_id.l10n_latam_identification_type_id.tpidprov', string='Tipo Proveedor SRI', store=True)
    partner_id_vat_tpidcliente = fields.Char(related='partner_id.l10n_latam_identification_type_id.tpidcliente', string='Tipo Cliente SRI', store=True)
    l10n_ec_entity = fields.Char(string="Emission Entity", size=3,compute='_compute_split_sequence', store=True)
    l10n_ec_emission = fields.Char(string="Emission Point", size=3,compute='_compute_split_sequence', store=True)
    ce_state = fields.Char('Estado SRI', store=True, compute=_get_ce_state)
    l10n_ec_invoice_autorizacion_id = fields.Many2one(
        comodel_name="l10n_ec_invoice.autorizacion",
        string="Punto de Emision", default=_default_autorizacion_id
    )

    l10n_ec_emission_type = fields.Selection(related='l10n_ec_invoice_autorizacion_id.l10n_ec_emission_type', string='Tipo de Emision', store=True)
    autorizacion = fields.Char('Autorización', copy=False,  )
    clave = fields.Char('Clave de Acceso', copy=False,  )
    ifactura_key = fields.Char('Key de Ifactura', copy=False,  )
    email_sent = fields.Char('Email de Envio', copy=False,  )
    ifactura_sent = fields.Boolean('Enviado a Ifactura', copy=False,  )

    nota_adicional = fields.Text("Observaciones",size=300)
    pedido_cliente = fields.Text("Nro de Pedido de Cliente",size=30)


    def _set_next_sequence(self):
        res = super(AccountMove, self)._set_next_sequence()
        try:
            if self.move_type in ('out_refund','out_invoice','in_invoice','in_refund') and self.journal_id.l10n_latam_use_documents:
                var = self.sequence_prefix.split(" ", 1)[-1]
                emision_array = var.split("-")
                self.l10n_ec_entity = emision_array[0]
                self.l10n_ec_emission = emision_array[1]
        except Exception as e:
            pass
        return res


    # Obtiene las secuencias de los puntos de venta
    # cambia comportamiento de modulo ln10_ec que trae desde el diario
    def _get_ec_formatted_sequence(self, number=0):
        if self.l10n_ec_invoice_autorizacion_id:
            return "%s %s-%s-%09d" % (
                self.l10n_latam_document_type_id.doc_code_prefix,
                self.l10n_ec_invoice_autorizacion_id.l10n_ec_entity,
                self.l10n_ec_invoice_autorizacion_id.l10n_ec_emission,
                number,
            )
        return super()._get_ec_formatted_sequence(number=number)


    def _get_last_sequence_domain(self, relaxed=False):
        l10n_latam_document_type_model = self.env['l10n_latam.document.type']
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(relaxed)
        if self.country_code == "EC" and self.l10n_latam_use_documents and self.move_type in (
            "out_invoice",
            "out_refund",
            "in_invoice",
            "in_refund",
        ):
            where_string, param = super(AccountMove, self)._get_last_sequence_domain(False)
            internal_type = self._get_l10n_ec_internal_type()
            document_types = l10n_latam_document_type_model.search([
                ('internal_type', '=', internal_type),
                ('country_id.code', '=', 'EC'),
            ])
            if document_types:
                where_string += """
                AND l10n_latam_document_type_id in %(l10n_latam_document_type_id)s
                """
                param["l10n_latam_document_type_id"] = tuple(document_types.ids)

            if self.l10n_ec_invoice_autorizacion_id:
                where_string += " AND l10n_ec_invoice_autorizacion_id = %(l10n_ec_invoice_autorizacion_id)s "
                param['l10n_ec_invoice_autorizacion_id'] = self.l10n_ec_invoice_autorizacion_id.id
        return where_string, param
    ##############################################################################

    def sri_legalizar_documento(self):
        for r in self:
            if r.l10n_latam_document_type_id and r.l10n_latam_document_type_id.code in ('NA', False):
                return
            if not r.l10n_ec_invoice_autorizacion_id:
                raise UserError('Debe seleccionar un Punto de Emision')
            if r.l10n_ec_invoice_autorizacion_id.l10n_ec_emission_type == 'electronic':
                r.emision_documentos_electronicos()
            else:
                r.emision_documentos_fisicos()
            return True


    def emision_documentos_electronicos(self):
        """
        Función para sobreescribir.
        """
        return

    def emision_documentos_fisicos(self):
        """
        En documentos físicos, solo colocamos el nro de autorización.
        """

    def button_send_factura_electronica(self):
        if self.state=='cancel':
            raise UserError("La factura fue cancelada, no puede generar un comprobante electronico")
            return False
        if self.ce_state=='AUTORIZADO':
            raise UserError("La factura fue AUTORIZADA, no puede generar un comprobante electronico")
            return False

        if self.move_type=='out_invoice':
            documento_electronico,claveacceso,tipoemision=self.get_factura_dict()
            print(documento_electronico)
            print('*** button_send_factura_electronica ***')
        # NCredito
        # elif move_type.type=='out_refund':
        #     ambiente_id, comprobante_id, documento_electronico, claveacceso, tipoemision = self.get_nota_credito_dict()
        company = self.env.user.company_id
        ambiente_id = company.ambiente_id
        comprobante_id = self.l10n_latam_document_type_id
        de_obj = self.env['l10n_ec_invoice.documento.electronico']
        reference = 'account.move,%s' % self.id
        type_doc=self.move_type
        generar_documento_electronico = self.env.context.get('generar_documento_electronico',True)
        print(de_obj)
        print("*"*60)
        if generar_documento_electronico:
            vals,msn_error = de_obj.get_documento_electronico_dict(
                ambiente_id, comprobante_id, documento_electronico, claveacceso, tipoemision, reference,self.move_type
            )
            if vals==False:
                raise UserError("****** ERROR AL VALIDAR EL DOCUMENTO ELECTRONICO****** \n%s"%msn_error)
        else:
            _error,msn_error = de_obj.validate_xsd_schema_documento_electronico_dict(documento_electronico,self.move_type)
            if _error==False:
                raise UserError("****** ERROR AL VALIDAR EL DOCUMENTO ELECTRONICO****** \n%s"%msn_error)
            vals = False

        self.autorizacion = claveacceso
        self.clave = claveacceso

        if self.move_type=='out_invoice':
            if self.factura_electronica_id:
                self.factura_electronica_id.write(vals)
                self.factura_electronica_id.replace_in_cola(reference)
            else:
                if vals:
                    print(" Valassss ok **************************************** >>>")
                    print("*"*60)
                    print(vals)
                    print("*"*60)
                    self.factura_electronica_id = de_obj.create(vals)
        # elif self.move_type=='out_refund':
        #     if self.nota_credito_electronica_id:
        #         self.nota_credito_electronica_id.write(vals)
        #         self.nota_credito_electronica_id.replace_in_cola(reference)
        #     else:
        #         if vals:
        #             self.nota_credito_electronica_id = de_obj.create(vals)
        # # Envía el archivo xml electónico a los correos de los clientes.
        # # self.send_email_de()
        # #self.send_de_backend()
        print("*"*60)
        return True


    def get_detalle_dict(self):
        detalles = OrderedDict([('detalle', []),])
        for line in self.invoice_line_ids:
            detalle = line.get_detalle_dict()
            detalles['detalle'].append(detalle)
        return detalles


    def get_propina(self):
        """
        Modificar con super
        :param self:
        :return: propina float
        """
        propina = 0.00
        return propina


    def get_pagos(self):
        pagos = OrderedDict([
            ('pago', []),
        ])

        if not self.invoice_payment_term_id.is_cash_sale:
            pagos['pago'].append(
                OrderedDict([
                    ('formaPago', self.invoice_payment_term_id.l10n_ec_sri_payment_id.code),
                    ('total', '{:.2f}'.format(self.amount_total)),
                    ('plazo', self.invoice_payment_term_id.unidad_tiempo_sri),
                    ('unidadTiempo', self.invoice_payment_term_id.plazo_sri)
                ]))
        else:
            if self.debit_lines_ids:
                invoice_payments_widget = json.loads(self.invoice_payments_widget)
                if invoice_payments_widget:
                    c=0;
                    for p in invoice_payments_widget['content']:
                        if p['formapago_code'] !=False:
                            pagos['pago'].append(
                                OrderedDict([
                                    ('formaPago', p['formapago_code']),
                                    ('total', '{:.2f}'.format(p['amount'])),
                                ]))
                            c+=1
                    if c<1:
                        pagos['pago'].append(
                            OrderedDict([
                                ('formaPago', self.invoice_payment_term_id.l10n_ec_sri_payment_id.code),
                                ('total', '{:.2f}'.format(self.amount_total)),
                            ]))
            else:
                pagos['pago'].append(
                    OrderedDict([
                        ('formaPago', self.invoice_payment_term_id.l10n_ec_sri_payment_id.code),
                        ('total', '{:.2f}'.format(self.amount_total)),
                    ]))
        return pagos



    def get_total_con_impuestos(self):
        totalConImpuestos = OrderedDict([
            ('totalImpuesto', []),
        ])


        res={}
        for line in self.invoice_line_ids:
            if line.tax_ids:
                taxes = line.tax_ids
                price_unit = line.price_unit
                taxes_res = taxes._origin.compute_all(price_unit,quantity=line.quantity,  is_refund=False)
                for tax_res in taxes_res['taxes']:
                    tax = self.env['account.tax'].browse(tax_res['id'])
                    res.setdefault(tax_res['id'], {
                        'tax_id':tax_res['id'],
                        'codigo':tax.electronic_group_tax_code or '',
                        'codigoPorcentaje':tax.electronic_tax_code or 9,
                        'tarifa': 0.0,
                        'baseImponible': 0.0,
                        'valor': 0.0,
                        })
                    res[tax_res['id']]['tarifa'] += tax.amount
                    res[tax_res['id']]['baseImponible'] += tax_res['base']
                    res[tax_res['id']]['valor'] += tax_res['amount']
        for r in res:
            totalConImpuestos['totalImpuesto'].append(OrderedDict([
                ('codigo', res[r]['codigo']),
                ('codigoPorcentaje', res[r]['codigoPorcentaje']),
                ('baseImponible', '{:.2f}'.format(res[r]['baseImponible'])),
                ('valor', '{:.2f}'.format(abs(res[r]['valor']))),
            ]))
        return totalConImpuestos

    def get_secuencial_completo(self):
        return """%s-%s-%s"""%(self.l10n_ec_entity,self.l10n_ec_emission,str(self.sequence_number).zfill(9))


    def get_infotributaria_dict(self,claveacceso,tipoemision,es_microempresa):
        company = self.env.user.company_id
        if es_microempresa:
            infoTributaria = OrderedDict([
                ('ambiente', company.ambiente_id.ambiente),
                ('tipoEmision', tipoemision),
                ('razonSocial', self.normalize(company.name)),
                ('nombreComercial', self.normalize(
                    company.partner_id.tradename or company.name)),
                ('ruc', company.vat),
                ('claveAcceso', claveacceso),
                ('codDoc', self.l10n_latam_document_type_id_code),
                ('estab', self.l10n_ec_entity),
                ('ptoEmi', self.l10n_ec_emission),
                ('secuencial', str(self.sequence_number).zfill(9)),
                ('dirMatriz', self.normalize(
                    company.street or company.street + company.street2)),
                ('regimenMicroempresas', 'CONTRIBUYENTE RÉGIMEN MICROEMPRESAS'),    
            ])
        else:
            infoTributaria = OrderedDict([
                ('ambiente', company.ambiente_id.ambiente),
                ('tipoEmision', tipoemision),
                ('razonSocial', self.normalize(company.name)),
                ('nombreComercial', self.normalize(
                    company.partner_id.tradename or company.name)),
                ('ruc', company.vat),
                ('claveAcceso', claveacceso),
                ('codDoc', self.l10n_latam_document_type_id_code),
                ('estab', self.l10n_ec_entity),
                ('ptoEmi', self.l10n_ec_emission),
                ('secuencial', str(self.sequence_number).zfill(9)),
                ('dirMatriz', self.normalize(
                    company.street or company.street + company.street2)),
            ])
        return infoTributaria


    def get_infoadicional(self):
        """
        Información adicional para las notas de crédito
        y facturas.
        return: [(nombre,valor),(nombre,valor)]
        """
        infoadicional = OrderedDict([('ID Interno',self.id)])
        return infoadicional

    def button_send_factura_electronica_reprocesar(self):
        if self.state=='draft':
            raise UserError("La documento esta en Borrador, no puede generar un comprobante electronico")
            return False
        if self.state=='cancel':
            raise UserError("La documento fue cancelado, no puede generar un comprobante electronico")
            return False
        if self.ce_state=='AUTORIZADO':
            raise UserError("El documento fue AUTORIZADO, no puede generar un comprobante electronico")
            return False
        if self.move_type in ('out_invoice','out_refund'):
            self.button_send_factura_electronica()




    def get_factura_dict(self):
        company = self.env.user.company_id
        punto_emision = self.l10n_ec_invoice_autorizacion_id
        tipoemision = '1'  # offline siempre es normal.
#
        if company.ambiente_id.ambiente == '1':
            # Si el ambiente es de pruebas enviamos siempre la fecha actual.
            fechaemision = fields.Date.context_today(self)
        else:
            fechaemision = self.invoice_date
        dirEstablecimiento = (punto_emision.l10n_ec_emission_address_id and punto_emision.l10n_ec_emission_address_id.street) or company.street or company.street + company.street2
        contribuyenteEspecial = company.contribuyente_especial_nro or '000' if company.contribuyente_especial else '000'
        obligadoContabilidad = (company.lleva_contabilidad and 'SI') or 'NO'
        es_microempresa = company.regimen_impositivo=='MICRO'
        tipoIdentificacionComprador = self.partner_id_vat_tpidcliente or ''
        razonSocialComprador = self.partner_id.name
        direccionComprador = self.partner_id.street or 'S/N'
        identificacionComprador = self.partner_id.vat
        totalDescuento = sum(self.invoice_line_ids.mapped('price_subtotal_discount')) or 0.0
        totalConImpuestos = self.get_total_con_impuestos()
        pagos = self.get_pagos()
        electronic_document = self.env['l10n_ec_invoice.documento.electronico']
        # claveacceso = electronic_document.get_claveacceso(self, id, fecha, comprobante, ruc, ambiente_id,establecimiento, puntoemision, secuencial):
        claveacceso = electronic_document.get_claveacceso(self.id,fechaemision, self.l10n_latam_document_type_id_code, company.vat, company.ambiente_id.ambiente,
            self.l10n_ec_entity, self.l10n_ec_emission, self.sequence_number)
        infoTributaria = self.get_infotributaria_dict(claveacceso,tipoemision,es_microempresa)

        # TODO considerar esto para NC
        # ('codDocModificado', coddocmodificado),
        # ('numDocModificado', numdocmodificado),
        # ('fechaEmisionDocSustento',fechaemisiondocsustento ),
        # ('valorModificacion', '{:.2f}'.format(self.amount_total)),
        # ('motivo', self.ref),


        infoFactura = OrderedDict([
            ('fechaEmision', self.normalize_date(fechaemision)),
            ('dirEstablecimiento', self.normalize(dirEstablecimiento)),
            ('contribuyenteEspecial', contribuyenteEspecial),
            ('obligadoContabilidad',obligadoContabilidad),
            ('tipoIdentificacionComprador',tipoIdentificacionComprador),
            #('guiaRemision', '000-000-000000000'),  # TODO
            #('rise', ''),  # TODO
            ('razonSocialComprador', self.normalize(razonSocialComprador)),
            ('identificacionComprador', identificacionComprador),
            ('direccionComprador', direccionComprador),
            ('totalSinImpuestos', '{:.2f}'.format(self.amount_untaxed)),
            ('totalDescuento', '{:.2f}'.format(totalDescuento)),
            ('totalConImpuestos', totalConImpuestos),
            ('propina', '{:.2f}'.format(self.get_propina())),
            ('importeTotal', '{:.2f}'.format(self.amount_total)),
            ('moneda', 'DOLAR'),
            ('pagos', pagos),
        ])

        detalles = self.get_detalle_dict()

        factura_dict = OrderedDict([
            ('factura', OrderedDict([
                ('@id', 'comprobante'),
                ('@version', '1.1.0'),
                ('infoTributaria', infoTributaria),
                ('infoFactura', infoFactura),
                ('detalles', detalles),
            ]),
            )
        ])

        camposAdicionales = self.get_infoadicional()
        if camposAdicionales:
            infoAdicional = OrderedDict([
                ('campoAdicional', []),
            ])
            for c,d in camposAdicionales.items():
                infoAdicional['campoAdicional'].append(OrderedDict([
                    ('@nombre', c),
                    ('#text', str(d)),
                ]))

            factura_dict.get('factura').update(OrderedDict([
                ('infoAdicional', infoAdicional)
            ])
            )
        return factura_dict, claveacceso,tipoemision

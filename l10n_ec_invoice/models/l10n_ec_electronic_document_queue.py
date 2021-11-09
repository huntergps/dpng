# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging


_logger = logging.getLogger(__name__)


class SriDocumentosElectronicosQueue(models.Model):
    _name = 'l10n_ec_invoice.documento.electronico.queue'
    _description = 'Documentos Electronicos queue'

    name = fields.Char(string='Name', )
    queue_line_ids = fields.One2many(
        'l10n_ec_invoice.documento.electronico.queue.line',
        'queue_id',
        string='Cola de documentos electrónicos',
    )

    @api.model
    def process_de_delete(self, ids=None):
        queue = self.env.ref('l10n_ec_invoice.documento_electronico_queue')
        print(queue)
        try:
            queue.queue_line_ids.unlink()
            queue.queue_line_ids.flush()
        except:
            pass

    def procesar_ventas(self, moves_ventas):
        for mov in moves_ventas:
            if mov.ce_state in ('NO ENVIADO','NO ENVIADA','RECHAZADA','SIN COMPROBANTE','CANCELADA'):
                # if mov.state in ('draft'):
                #     try:
                #         if mov.type=='out_refund' and mov.comprobante_id==False:
                #             mov.comprobante_id = self.env.ref('l10n_ec_invoice.comprobante_04').id
                #         if not mov.partner_id.email:
                #             mov.partner_id.email  = mov.company_id.email
                #         #mov.action_post()
                #     except Exception as e:
                #         print(e)
                #         continue
                if mov.state in ('posted'):
                    try:
                        mov.button_send_factura_electronica_reprocesar()
                    except Exception as e:
                        continue


    @api.model
    def process_de_reload(self, ids=None):
        line = self.env['l10n_ec_invoice.documento.electronico.queue.line']
        domain_ventas = [('move_type','in',['out_invoice','out_refund']),('state','in',['posted','draft']),('ce_state','in',['NO ENVIADO','RECHAZADA','SIN COMPROBANTE'])]

        mens = "*********** >>>> process_de_reload   domain_ventas = %s"%(domain_ventas)
        _logger = logging.error(mens)

        limit = 20
        nro_regs = self.env['account.move'].search_count(domain_ventas) or 0
        moves_ventas = self.env['account.move'].search(domain_ventas, limit=limit)
        self.procesar_ventas( moves_ventas)
        self._cr.commit()



    def procesar_cola_docs(self, pendientes):
        for p in pendientes:
            de = p.documento_electronico_id
            if de.estado:
                if de.estado in  ('NO ENVIADO','ERROR TCP'):
                    try:
                        de.send_de_backend()
                    except Exception as e:
                        continue
                        try:
                            de.receive_de_offline()
                        except Exception as e:
                            continue

                de.flush()
                if de.estado in ('RECIBIDA', 'EN PROCESO','DEVUELTA','ERROR TCP','FAIL READ'):
                    try:
                        de.receive_de_offline()
                    except Exception as e:
                        continue
                        #de.receive_de_offline()

                if not p.sent and de.estado == 'AUTORIZADO':
                    try:
                        sent = de.reference.send_email_de()
                        p.sent = sent
                    except:
                        p.sent = False



    @api.model
    def process_de_queue_sent_client(self, ids=None):
        queue = self.env.ref('l10n_ec_invoice.documento_electronico_queue')
        canceladas = queue.queue_line_ids.filtered(lambda x: x.sent == True and x.estado == 'CANCELADA')
        if canceladas:
            try:
                canceladas.unlink()
            except:
                pass

        procesadas = queue.queue_line_ids.filtered(
            lambda x: x.sent == True and x.estado == 'AUTORIZADO'
        )
        if procesadas:
            # Usamos try porque es posible que el cron se ejecute
            # al mismo tiempo que una orden manual del usuario
            # y se intente borrar dos veces el mismo record.
            try:
                procesadas.unlink()
            except:
                pass


    @api.model
    def process_de_queue(self, ids=None):
        queue = self.env.ref('l10n_ec_invoice.documento_electronico_queue')
        canceladas = queue.queue_line_ids.filtered(
            lambda x: x.sent == True and x.estado == 'CANCELADA'
        )
        if canceladas:
            try:
                canceladas.unlink()
            except:
                pass

        procesadas = queue.queue_line_ids.filtered(
            lambda x: x.sent == True and x.estado == 'AUTORIZADO'
        )
        if procesadas:
            # Usamos try porque es posible que el cron se ejecute
            # al mismo tiempo que una orden manual del usuario
            # y se intente borrar dos veces el mismo record.
            try:
                procesadas.unlink()
            except:
                pass

        #pendientes = queue.queue_line_ids
        # raise UserError('Prueba')
        self._cr.commit()
        offset = 2
        nro_regs = 30 #len(pendientes)
        pos = 0
        line_obj = self.env['l10n_ec_invoice.documento.electronico.queue.line']
        pendientes = line_obj.search([('estado','in', ('NO ENVIADO','AUTORIZADO','RECIBIDA', 'EN PROCESO','DEVUELTA','ERROR TCP'))], limit=nro_regs)
        self.procesar_cola_docs(pendientes)
        self._cr.commit()




class SriDocumentosElectronicosQueueLine(models.Model):
    _name = 'l10n_ec_invoice.documento.electronico.queue.line'
    _description = 'Documentos Electronicos queue line'
    _order = 'create_date desc'

    def _get_reference_models(self):
        records = self.env['ir.model'].search(
            ['|', ('model', '=', 'account.move'), ('model', '=', 'stock.picking')])
        val=[(record.model, record.name) for record in records] + [('', '')]
        print("val2 >>> ",val)
        return val

    sent = fields.Boolean(string='Sent', default=False)


    documento_electronico_id = fields.Many2one(
        'l10n_ec_invoice.documento.electronico', string='Documento electronico', )
    estado = fields.Selection(
        string='State', related="documento_electronico_id.estado",
        store=True, )
    #reference = fields.Reference(
    #    related='documento_electronico_id.reference', string=_('Reference'), store=True)
    reference = fields.Reference(
        string='Reference', selection='_get_reference_models')


    queue_id = fields.Many2one(
        'l10n_ec_invoice.documento.electronico.queue', string='Queue', )

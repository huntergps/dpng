# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,exceptions,_
from odoo.exceptions import ValidationError, UserError

from datetime import datetime, timedelta, date

class BalconBankPayment(models.TransientModel):
    _name = 'balcon.bank.payment'
    _description = "Registro de Pago Bancario"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def default_get(self, fields):
        res = super(BalconBankPayment, self).default_get(fields)

        if self._context.get('active_model') == 'balcon.order' and self._context.get('active_id', False):
            balcon_order = self.env['balcon.order'].browse(self._context.get('active_id'))
            res.update({
                'order_id': self._context.get('active_id'),
                'amount':balcon_order.amount_total - balcon_order.payment_registered_amount,
            })
        return res

    @api.model
    def _default_currency_id(self):
        if self._context.get('active_model') == 'balcon.order' and self._context.get('active_id', False):
            balcon_order = self.env['balcon.order'].browse(self._context.get('active_id'))
            return balcon_order.currency_id

    def _default_payment_date(self):
        return fields.Date.today()

    order_id = fields.Many2one('balcon.order', string='Orden de Servicio', required=True, ondelete='cascade')
    date_order = fields.Datetime(string='Order Date', related='order_id.date_order')
    acquirer_id = fields.Many2one('payment.acquirer', string='Acquirer', required=True)
    amount_total = fields.Monetary(string='Total Order', related='order_id.amount_total')
    payment_registered_amount = fields.Monetary(string='Registered Amount', related='order_id.payment_registered_amount')
    payment_authorized_amount = fields.Monetary(string='Authorized Amount', related='order_id.payment_authorized_amount')
    amount_total_balance = fields.Monetary(string='Payment Balance', related='order_id.amount_total_balance')

    count = fields.Integer(default=_count, string='Order Count')
    payment_date = fields.Date(string='Payment Date', default=_default_payment_date)
    bank_ref = fields.Char(string='Bank Reference')
    narration = fields.Text(string='Notes')

    amount = fields.Float('Payment Amount', digits='Account')

    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency_id)
    payment_type = fields.Selection([
        ('cash', 'Airport Cash'),
        ('bank', 'Bank Deposit or Transfer'),
        ('online', 'Credit Card')
        ], string='Payment Type',  default='bank'
        )

    file = fields.Binary('Archivo')
    file_opt = fields.Selection([('pdf','Archivo PDF'),('image','Imagen (*.png,*.jpg)')],string='Extension del archivo', default='pdf')
    file_name = fields.Char('File Name')
    file_type = fields.Char('File Type')


    @api.constrains('file_name')
    def _check_filename(self):
        if self.file:
            if not self.file_name:
                raise exceptions.ValidationError("Seleccione un archivo")
            else:
                tmp = self.file_name.split('.')
                ext = tmp[len(tmp)-1]
                file_ext=['pdf','png','jpg']
                if ext not in file_ext:
                    raise exceptions.ValidationError("Solo se aceptan archivos PDF, PNG y JPG" )
        else:
            raise exceptions.ValidationError("Seleccione un archivo")

    @api.depends('order_id')
    def _compute_display_invoice_alert(self):
        for wizard in self:
            wizard.display_invoice_alert = bool(wizard.order_id.invoice_ids.filtered(lambda inv: inv.state == 'draft'))

    def action_cancel(self):
        return self.order_id.with_context({'disable_cancel_warning': True}).action_cancel()

    def get_transaction_vals(self):
        vals={
        'acquirer_id':self.acquirer_id.id,
        # 'type':'form',
        'state_message':'En espera de revision',
        'amount':self.amount,
        'reference':'%s-%s'%(self.order_id.name, datetime.now()),
        'acquirer_reference':self.bank_ref,
        # 'partner_id':self.order_id.partner_id.id,
        # 'partner_name':self.order_id.partner_id.name,
        # 'partner_address':self.order_id.partner_id.street,
        # 'partner_city':self.order_id.partner_id.city,
        # 'currency_id':self.currency_id.id,
        # 'date':fields.Datetime.now,

        }
        return vals
    def register_bank_payments(self):
        balcon_orders = self.env['balcon.order'].browse(self._context.get('active_ids', []))

        self._check_filename()
        if self.order_id:
            order_id= self.order_id
            order_id._create_payment_transaction(self.get_transaction_vals())
        else:
            raise exceptions.ValidationError("Seleccione una Orden de Servicio")

        if self._context.get('open_invoices', False):
            return balcon_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

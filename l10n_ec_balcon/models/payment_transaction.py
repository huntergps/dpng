# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import re

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools import float_compare


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    balcon_order_ids = fields.Many2many('balcon.order', 'balcon_order_transaction_rel', 'transaction_id', 'balcon_order_id',
                                      string='Balcon Orders', copy=False, readonly=True)
    balcon_order_ids_nbr = fields.Integer(compute='_compute_balcon_order_ids_nbr', string='# of Balcon Orders')

    def _compute_balcon_order_reference(self, order):
        self.ensure_one()
        if self.acquirer_id.bo_reference_type == 'bo_name':
            return order.name
        else:
            # self.acquirer_id.bo_reference_type == 'partner'
            identification_number = order.partner_id.id
            return '%s/%s' % ('CUST', str(identification_number % 97).rjust(2, '0'))

    @api.depends('balcon_order_ids')
    def _compute_balcon_order_ids_nbr(self):
        for trans in self:
            trans.balcon_order_ids_nbr = len(trans.balcon_order_ids)

    def _set_pending(self, state_message=None):
        """ Override of payment to send the quotations automatically. """
        super(PaymentTransaction, self)._set_pending(state_message=state_message)

        for record in self:
            balcon_orders = record.balcon_order_ids.filtered(lambda so: so.state in ['draft', 'sent'])
            balcon_orders.filtered(lambda so: so.state == 'draft').with_context(tracking_disable=True).write({'state': 'sent'})

            if record.acquirer_id.provider == 'transfer':
                for so in record.balcon_order_ids:
                    so.reference = record._compute_balcon_order_reference(so)
            # send order confirmation mail
            balcon_orders._send_balcon_order_confirmation_mail()

    def _check_amount_and_confirm_balcon_order(self):
        self.ensure_one()
        for order in self.balcon_order_ids.filtered(lambda so: so.state in ('draft', 'sent')):
            if order.currency_id.compare_amounts(self.amount, order.amount_total) == 0:
                order.with_context(send_email=True).action_confirm()
            else:
                _logger.warning(
                    '<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r',
                    self.acquirer_id.provider,order.name, order.id,
                    order.amount_total, self.amount,
                )
                order.message_post(
                    subject=_("Amount Mismatch (%s)", self.acquirer_id.provider),
                    body=_("The order was not confirmed despite response from the acquirer (%s): order total is %r but acquirer replied with %r.") % (
                        self.acquirer_id.provider,
                        order.amount_total,
                        self.amount,
                    )
                )

    def _set_authorized(self, state_message=None):
        """ Override of payment to confirm the quotations automatically. """
        super()._set_authorized(state_message=state_message)
        balcon_orders = self.mapped('balcon_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
        for tx in self:
            tx._check_amount_and_confirm_balcon_order()

        # send order confirmation mail
        balcon_orders._send_balcon_order_confirmation_mail()

    def _log_message_on_linked_documents(self, message):
        """ Override of payment to log a message on the sales orders linked to the transaction.

        Note: self.ensure_one()

        :param str message: The message to be logged
        :return: None
        """
        super()._log_message_on_linked_documents(message)
        for order in self.balcon_order_ids:
            order.message_post(body=message)

    def _reconcile_after_done(self):
        """ Override of payment to automatically confirm quotations and generate invoices. """
        balcon_orders = self.mapped('balcon_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
        for tx in self:
            tx._check_amount_and_confirm_balcon_order()
        # send order confirmation mail
        balcon_orders._send_balcon_order_confirmation_mail()
        # invoice the sale orders if needed
        self._invoice_balcon_orders()
        res = super()._reconcile_after_done()
        if self.env['ir.config_parameter'].sudo().get_param('l10n_ec_balcon.automatic_invoice') and any(so.state in ('sale', 'done') for so in self.balcon_order_ids):
            default_template = self.env['ir.config_parameter'].sudo().get_param('l10n_ec_balcon.default_invoice_email_template')
            if default_template:
                for trans in self.filtered(lambda t: t.balcon_order_ids.filtered(lambda so: so.state in ('sale', 'done'))):
                    trans = trans.with_company(trans.acquirer_id.company_id).with_context(
                        mark_invoice_as_sent=True,
                        company_id=trans.acquirer_id.company_id.id,
                    )
                    for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
                        invoice.message_post_with_template(int(default_template), email_layout_xmlid="mail.mail_notification_paynow")
        return res

    def _invoice_balcon_orders(self):
        if self.env['ir.config_parameter'].sudo().get_param('l10n_ec_balcon.automatic_invoice'):
            for trans in self.filtered(lambda t: t.balcon_order_ids):
                trans = trans.with_company(trans.acquirer_id.company_id)\
                    .with_context(company_id=trans.acquirer_id.company_id.id)
                confirmed_orders = trans.balcon_order_ids.filtered(lambda so: so.state in ('sale', 'done'))
                if confirmed_orders:
                    confirmed_orders._force_lines_to_invoice_policy_order()
                    invoices = confirmed_orders._create_invoices()
                    trans.invoice_ids = [(6, 0, invoices.ids)]

    @api.model
    def _compute_reference_prefix(self, provider, separator, **values):
        """ Override of payment to compute the reference prefix based on Sales-specific values.

        If the `values` parameter has an entry with 'balcon_order_ids' as key and a list of (4, id, O)
        or (6, 0, ids) X2M command as value, the prefix is computed based on the sales order name(s)
        Otherwise, the computation is delegated to the super method.

        :param str provider: The provider of the acquirer handling the transaction
        :param str separator: The custom separator used to separate data references
        :param dict values: The transaction values used to compute the reference prefix. It should
                            have the structure {'balcon_order_ids': [(X2M command), ...], ...}.
        :return: The computed reference prefix if order ids are found, the one of `super` otherwise
        :rtype: str
        """
        command_list = values.get('balcon_order_ids')
        if command_list:
            # Extract sales order id(s) from the X2M commands
            order_ids = self._fields['balcon_order_ids'].convert_to_cache(command_list, self)
            orders = self.env['balcon.order'].browse(order_ids).exists()
            if len(orders) == len(order_ids):  # All ids are valid
                return separator.join(orders.mapped('name'))
        return super()._compute_reference_prefix(provider, separator, **values)

    def action_view_balcon_orders(self):
        action = {
            'name': _('Balcon Order(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'balcon.order',
            'target': 'current',
        }
        balcon_order_ids = self.balcon_order_ids.ids
        if len(balcon_order_ids) == 1:
            action['res_id'] = balcon_order_ids[0]
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', balcon_order_ids)]
        return action

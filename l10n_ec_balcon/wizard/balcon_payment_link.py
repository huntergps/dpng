# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug import urls

from odoo import api, models


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'
    _description = 'Generate Sales Payment Link'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if res['res_id'] and res['res_model'] == 'balcon.order':
            record = self.env[res['res_model']].browse(res['res_id'])
            res.update({
                'description': record.name,
                'amount': record.amount_total - sum(record.invoice_ids.filtered(lambda x: x.state != 'cancel').mapped('amount_total')),
                'currency_id': record.currency_id.id,
                'partner_id': record.partner_id.id,
                'amount_max': record.amount_total
            })
        return res

    @api.depends('company_id', 'partner_id', 'currency_id')
    def _compute_available_acquirer_ids(self):
        balcon_links = self.filtered(lambda link: link.res_model == 'balcon.order')
        super(PaymentLinkWizard, self-balcon_links)._compute_available_acquirer_ids()
        for link in balcon_links:
            link.available_acquirer_ids = link.env['payment.acquirer']._get_compatible_acquirers(
                company_id=link.company_id.id,
                partner_id=link.partner_id.id,
                currency_id=link.currency_id.id,
                balcon_order_id=link.res_id)

    def _generate_link(self):
        """ Override of payment to add the balcon_order_id in the link. """
        for payment_link in self:
            # The balcon_order_id field only makes sense if the document is a sales order
            if payment_link.res_model == 'balcon.order':
                related_document = self.env[payment_link.res_model].browse(payment_link.res_id)
                base_url = related_document.get_base_url()
                payment_link.link = f'{base_url}/payment/pay' \
                                    f'?reference={urls.url_quote(payment_link.description)}' \
                                    f'&amount={payment_link.amount}' \
                                    f'&balcon_order_id={payment_link.res_id}' \
                                    f'{"&acquirer_id=" + str(payment_link.acquirer_id.id) if payment_link.acquirer_id else "" }' \
                                    f'&access_token={payment_link.access_token}'
                # Order-related fields are retrieved in the controller
            else:
                super(PaymentLinkWizard, payment_link)._generate_link()

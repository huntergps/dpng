# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    bo_reference_type = fields.Selection(string='Communication',
        selection=[
            ('bo_name', 'Based on Document Reference'),
            ('partner', 'Based on Customer ID')], default='bo_name',
        help='You can set here the communication type that will appear on sales orders.'
             'The communication will be given to the customer when they choose the payment method.')

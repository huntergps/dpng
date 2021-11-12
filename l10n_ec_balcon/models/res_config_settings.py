# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_auto_done_setting = fields.Boolean("Lock Confirmed Balcon Orders", implied_group='l10n_ec_balcon.group_auto_done_setting')
    balcon_order_validity_days = fields.Integer(related='company_id.balcon_order_validity_days', string="Default Quotation Validity (Days)", readonly=False)
    use_balcon_order_validity_days = fields.Boolean("Validez por defecto en las Ordenes de Servicio", config_parameter='l10n_ec_balcon.use_balcon_order_validity_days')
    group_warning_balcon = fields.Boolean("Sale Order Warnings", implied_group='l10n_ec_balcon.group_warning_balcon')
    portal_confirmation_sign = fields.Boolean(related='company_id.portal_confirmation_sign', string='Online Signature', readonly=False)
    portal_confirmation_pay = fields.Boolean(related='company_id.portal_confirmation_pay', string='Online Payment', readonly=False)
    group_balcon_delivery_address = fields.Boolean("Customer Addresses", implied_group='l10n_ec_balcon.group_delivery_invoice_address')
    group_proforma_sales = fields.Boolean(string="Pro-Forma Invoice", implied_group='l10n_ec_balcon.group_proforma_sales',
        help="Allows you to send pro-forma invoice.")
    default_invoice_policy = fields.Selection([
        ('order', 'Invoice what is ordered'),
        ('delivery', 'Invoice what is delivered')
        ], 'Invoicing Policy',
        default='order',
        default_model='product.template')
    deposit_default_product_id = fields.Many2one(
        'product.product',
        'Deposit Product',
        domain="[('type', '=', 'service')]",
        config_parameter='l10n_ec_balcon.default_deposit_product_id',
        help='Default product used for payment advances')



    module_product_email_template = fields.Boolean("Specific Email")

    automatic_invoice = fields.Boolean(
        string="Automatic Invoice",
        help="The invoice is generated automatically and available in the customer portal when the "
             "transaction is confirmed by the payment acquirer.\nThe invoice is marked as paid and "
             "the payment is registered in the payment journal defined in the configuration of the "
             "payment acquirer.\nThis mode is advised if you issue the final invoice at the order "
             "and not after the delivery.",
        config_parameter='l10n_ec_balcon.automatic_invoice',
    )
    invoice_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Invoice Email Template',
        domain="[('model', '=', 'account.move')]",
        config_parameter='l10n_ec_balcon.default_invoice_email_template',
        default=lambda self: self.env.ref('account.email_template_edi_invoice', False)
    )
    confirmation_mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Confirmation Email Template',
        domain="[('model', '=', 'balcon.order')]",
        config_parameter='l10n_ec_balcon.default_confirmation_template',
        help="Email sent to the customer once the order is paid."
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.default_invoice_policy != 'order':
            self.env['ir.config_parameter'].set_param('l10n_ec_balcon.automatic_invoice', False)

    @api.onchange('use_balcon_order_validity_days')
    def _onchange_use_balcon_order_validity_days(self):
        if self.balcon_order_validity_days <= 0:
            self.balcon_order_validity_days = self.env['res.company'].default_get(['balcon_order_validity_days'])['balcon_order_validity_days']

    @api.onchange('balcon_order_validity_days')
    def _onchange_balcon_order_validity_days(self):
        if self.balcon_order_validity_days <= 0:
            self.balcon_order_validity_days = self.env['res.company'].default_get(['balcon_order_validity_days'])['balcon_order_validity_days']
            return {
                'warning': {'title': "Warning", 'message': "Quotation Validity is required and must be greater than 0."},
            }

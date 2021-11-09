# -*- coding: utf-8 -*-
# from odoo import http


# class L10nEcInvoice(http.Controller):
#     @http.route('/l10n_ec_invoice/l10n_ec_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_ec_invoice/l10n_ec_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_ec_invoice.listing', {
#             'root': '/l10n_ec_invoice/l10n_ec_invoice',
#             'objects': http.request.env['l10n_ec_invoice.l10n_ec_invoice'].search([]),
#         })

#     @http.route('/l10n_ec_invoice/l10n_ec_invoice/objects/<model("l10n_ec_invoice.l10n_ec_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_ec_invoice.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
# from odoo import http


# class DpngBase(http.Controller):
#     @http.route('/dpng_base/dpng_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dpng_base/dpng_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dpng_base.listing', {
#             'root': '/dpng_base/dpng_base',
#             'objects': http.request.env['dpng_base.dpng_base'].search([]),
#         })

#     @http.route('/dpng_base/dpng_base/objects/<model("dpng_base.dpng_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dpng_base.object', {
#             'object': obj
#         })

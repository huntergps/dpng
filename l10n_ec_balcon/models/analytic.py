# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _default_balcon_line_domain(self):
        """ This is only used for delivered quantity of SO line based on analytic line, and timesheet
            (see balcon_timesheet). This can be override to allow further customization.
        """
        return [('qty_delivered_method', '=', 'analytic')]

    bo_line = fields.Many2one('balcon.order.line', string='Balcon Order Item', domain=lambda self: self._default_balcon_line_domain())

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class OnboardingController(http.Controller):

    @http.route('/l10n_ec_balcon/balcon_order_onboarding_panel', auth='user', type='json')
    def balcon_quotation_onboarding(self):
        """ Returns the `banner` for the sale onboarding panel.
            It can be empty if the user has closed it or if he doesn't have
            the permission to see it. """

        company = request.env.company
        if not request.env.is_admin() or \
           company.balcon_quotation_onboarding_state == 'closed':
            return {}

        return {
            'html': request.env.ref('l10n_ec_balcon.balcon_order_onboarding_panel')._render({
                'company': company,
                'state': company.get_and_update_balcon_quotation_onboarding_state()
            })
        }

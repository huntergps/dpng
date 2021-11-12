# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta, date

from odoo import fields, models, api
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP

marital_status_registro_civil={
'CASADO':'married',
'SOLTERO': 'single',
'DIVORCIADO': 'divorced',
'VIUDO':'widover'
}

gender_registro_civil={
'HOMBRE':'male',
'MUJER': 'femenine',
'OTRO': 'other',
}

def calculate_age(dtob):
    today = date.today()
    return today.year - dtob.year - ((today.month, today.day) < (dtob.month, dtob.day))



class ResPartner(models.Model):
    _inherit = 'res.partner'


    gender = fields.Selection([
        ('male', 'Male'),
        ('femenine', 'Femenine'),
        ('indeterminate', 'Indeterminate')
        ], string='Gender',  default='male')

    birth_date = fields.Date(string='Birth Date')
    age_years = fields.Integer(string='Age', compute='_compute_age', store=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widover', 'Widover'),
        ('free_union', 'Free Union'),
        ('indeterminate', 'Indeterminate')
        ], string='Marital Status', default='indeterminate')

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            hoy=fields.Date.today()
            if rec.birth_date:
                age_years =  calculate_age(rec.birth_date)
                rec.age_years=age_years
            else:
                rec.age_years=0

    balcon_order_count = fields.Integer(compute='_compute_balcon_order_count', string='Sale Order Count')
    balcon_order_ids = fields.One2many('balcon.order', 'partner_id', 'Balcon Order')
    balcon_warn = fields.Selection(WARNING_MESSAGE, 'Sales Warnings', default='no-message', help=WARNING_HELP)
    balcon_warn_msg = fields.Text('Message for Balcon Order')

    def _compute_balcon_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        balcon_order_groups = self.env['balcon.order'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        partners = self.browse()
        for group in balcon_order_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.balcon_order_count += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).balcon_order_count = 0

    def can_edit_vat(self):
        ''' Can't edit `vat` if there is (non draft) issued SO. '''
        can_edit_vat = super(ResPartner, self).can_edit_vat()
        if not can_edit_vat:
            return can_edit_vat
        BalconOrder = self.env['balcon.order']
        has_so = BalconOrder.search([
            ('partner_id', 'child_of', self.commercial_partner_id.id),
            ('state', 'in', ['sent', 'sale', 'done'])
        ], limit=1)
        return can_edit_vat and not bool(has_so)

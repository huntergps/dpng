# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError, ValidationError

from datetime import date


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    debit_main_id = fields.Many2one('account.move', 'debit_lines_ids', related='debit_move_id.move_id', copy=False, readonly=True, auto_join=True)
    debit_main_name = fields.Char("Detalle Debito", related='debit_main_id.name', copy=False, readonly=True,)
    debit_main_journal_name = fields.Char("Diario Débito", related='debit_main_id.journal_id.name', copy=False, readonly=True,)
    debit_main_journal_type = fields.Selection(string="Tipo Débito", related='debit_main_id.journal_id.type')
    debit_main_date = fields.Date("Fecha Debito", related='debit_main_id.date', copy=False, readonly=True,)
    credit_main_id = fields.Many2one('account.move', 'credit_lines_ids', related='credit_move_id.move_id', copy=False, readonly=True, auto_join=True)
    credit_main_name = fields.Char("Detalle Credito", related='credit_main_id.name', copy=False, readonly=True,)
    credit_main_journal_name = fields.Char("Diario Crédito", related='credit_main_id.journal_id.name', copy=False, readonly=True,)
    credit_main_journal_type = fields.Selection(string="Tipo Credito", related='credit_main_id.journal_id.type')
    credit_main_date = fields.Date("Fecha Credito", related='credit_main_id.date', copy=False, readonly=True,)

# -*- coding: utf-8 -*-

from odoo import fields
from odoo.fields import apply_required

_super = apply_required
def patched_apply_required(model, field_name):
    """
    not set that
    :param model: 
    :param field_name: 
    :return: 
    """
    if model._name in ["res.users", "res.company"] and field_name == "setting_id":
        return 
    _super(model, field_name)
fields.apply_required = patched_apply_required

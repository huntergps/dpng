# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import json
from odoo.modules.module import get_resource_path
from odoo.tools import ormcache


class AnitaModeTemplate(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.mode_template'
    _description = 'Anita Mode Template'

    name = fields.Char(string="Name", required=True)
    template = fields.Text(string="Template", required=True)
    color_vars = fields.Text(string="Color Vars")

    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Name Must Be Unique!")]

    @ormcache()
    def get_templates(self):
        """
        get templates
        :return:
        """
        records = self.search([])
        return {record.name: record for record in records}

    def get_template(self):
        """
        get template
        :return:
        """
        return json.loads(self.template)

    def get_color_vars(self):
        """
        get vars
        :return:
        """
        return json.loads(self.color_vars)

    @api.model
    def install_template(self, name, module_path, file_path, color_vars):
        """
        install mode
        :return:
        """
        tmp_path = get_resource_path(module_path, file_path)

        with open(tmp_path, 'r') as fd:

            template = fd.read()

            if not name:
                raise exceptions.ValidationError(
                    'Template {template} must has a name!'.format(template=file_path))

            old_model = self.search([('name', '=', name)])
            if not old_model:
                self.create([{
                    "name": name,
                    "template": template,
                    "color_vars": color_vars
                }])
            else:
                old_model.write({
                    "name": name,
                    "template": template,
                    "color_vars": color_vars
                })

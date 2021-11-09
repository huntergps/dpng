# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.tools import ormcache
import json
from odoo.modules.module import get_resource_path


class AnitaDefaultMode(models.Model):
    '''
    default mode
    '''
    _name = 'anita_theme_setting.default_mode_data'
    _description = 'Anita Theme Setting Mode Template'

    name = fields.Char(string="Name", required=True)
    data = fields.Text(string="Content", required=True)
    version = fields.Char(string="Version", required=True)

    _sql_constraints = [('name_unique', 'UNIQUE(name)', "Name Must Be Unique!")]

    def get_mode_data(self):
        """
        get mode
        :return:
        """
        self.ensure_one()
        mode_data = json.loads(self.data)
        mode_data.update({
            "name": self.name,
            "version": self.version
        })
        return mode_data

    @ormcache()
    def get_default_modes(self):
        """
        get default modes
        :return:
        """
        records = self.search([])
        default_models = []
        for record in records:
            default_models.append(record.get_mode_data())
        return default_models

    @api.model
    def install_mode(self, name, version,  module_path, file_path):
        """
        install mode
        :return:
        """
        tmp_path = get_resource_path(module_path, file_path)

        with open(tmp_path, 'r') as fd:

            mode_text = fd.read()

            if not name:
                raise exceptions.ValidationError(
                    'Template {template} must has a name!'.format(template=file_path))

            if not version:
                raise exceptions.ValidationError(
                    'Template {template} must has version info!'.format(template=file_path))

            old_model = self.search([('name', '=', name)])
            if not old_model:
                self.create([{
                    "name": name,
                    "data": mode_text,
                    "version": version,
                }])
            else:
                old_model.write({
                    "name": name,
                    "data": mode_text,
                    "version": version
                })

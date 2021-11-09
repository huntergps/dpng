# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import json


class ColorVar(models.TransientModel):
    """
    color item
    """
    _name = 'anita_theme_setting.color_var'
    _description = 'color var'

    wizard = fields.Many2one(
        'anita_theme_setting.theme_mode_wizard', string='wizard', ondelete='cascade')

    name = fields.Char(string='name', required=True)
    val = fields.Char(string='val')


class AnitaThemeModeWizard(models.TransientModel):
    """
    akl theme mode wizard
    """
    _name = 'anita_theme_setting.theme_mode_wizard'
    _description = 'file replace wizard'

    name = fields.Char(string="Name", required=True)
    owner = fields.Char(string="Owner")

    template = fields.Many2one(
        comodel_name="anita_theme_setting.mode_template", string="Template")

    theme_mode = fields.Many2one(
        comodel_name="anita_theme_setting.theme_mode", string="Theme Mode")

    apply_vars_to_styles = fields.Boolean(
        string="Apply Vars to Styles", default=False)

    color_vars = fields.One2many(
        comodel_name='anita_theme_setting.color_var',
        inverse_name="wizard")

    @api.onchange('template')
    def on_change_template(self):
        """
        onchange template
        :return:
        """
        if self.template:
            color_vars = self.template.get_color_vars()
            self.color_vars = [(0, 0, {
                'name': name, 'val': color_vars[name]}) for name in color_vars]

    def create_mode(self):
        """
        btn action
        """
        self.ensure_one()

        if not self.template:
            raise exceptions.ValidationError('Please Select A template!')

        template = self.template.template
        color_vars = self.template.get_color_vars()

        # css template data
        template = template.replace('$mode_name', self.name)
        for tmp_var in color_vars:
            template = str(template).replace(tmp_var.name, tmp_var.val)

        # create mode data
        data = json.loads(template)
        owner = self.env["anita_theme_setting.setting_manager"].get_current_owner()
        record = self.env["anita_theme_setting.theme_mode"].create_mode({
            "theme_styles": [data],
            "name": self.name,
            "version": '1.0.0.1',
            "owner": owner,
            "is_default": False
        })

        # set mode json text
        record.mode_style_css = template

        # save mode vars
        var_dict = {tmp_var.name: tmp_var.val for tmp_var in color_vars}
        record.vars = json.dumps(var_dict)

        # return the mode data
        return record.get_mode_data()

    def update_mode(self):
        """
        btn action
        """
        color_vars = self.color_vars
        template = self.template.template

        # css template data
        template = template.replace('$mode_name', self.name)
        template = template.replace('__mode_name__', self.name)
        for tmp_var in color_vars:
            template = str(template).replace(tmp_var.name, tmp_var.val)
        self.theme_mode.mode_style_css = template
        self.theme_mode.compute_mode_style()

        mode_vars = {tmp_var.name: tmp_var.val for tmp_var in color_vars}
        self.theme_mode.vars = json.dumps(mode_vars)

        # return the mode data
        return self.theme_mode.get_mode_data()

    def preview_mode(self):
        """
        btn action
        """
        color_vars = self.color_vars

        if not self.template:
            raise exceptions.ValidationError('Please Select A Template')

        # css template data
        mode_style_txt = self.template.template.replace('$mode_name', "mode_preview")
        for tmp_var in color_vars:
            mode_style_txt = str(mode_style_txt).replace(tmp_var.name, tmp_var.val)

        mode_style_txt = \
            self.env["anita_theme_setting.theme_mode"]._compile_scss(mode_style_txt)
        mode_style_txt = mode_style_txt.replace(
            'body.{name}'.format(name=self.name), "body.mode_preview")

        # return the mode data
        return mode_style_txt

    @api.model
    def get_change_mode_setting_wizard(self, mode_id):
        """
        get change mode setting wizard
        :return:
        """
        theme_mode = self.env["anita_theme_setting.theme_mode"].browse(mode_id)
        template_vars = theme_mode.template_vars
        template_vars = json.loads(template_vars or "{}")
        default_vars = [(0, 0, {'name': name, 'val': template_vars[name]}) for name in template_vars]

        return {
            "type": "ir.actions.act_window",
            "res_model": "anita_theme_setting.theme_mode_wizard",
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': theme_mode.name,
                'default_color_vars': default_vars,
                'default_theme_mode': mode_id
            },
            "views": [[self.env.ref('anita_theme_setting.theme_mode_wizard').id, "form"]]
        }


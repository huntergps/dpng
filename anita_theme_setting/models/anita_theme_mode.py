# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import json
import re
from odoo.tools.config import config

try:
    import sass as libsass
except ImportError:
    libsass = None


class AnitaThemeMode(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.theme_mode'
    _description = 'anita theme mode'

    name = fields.Char(string="Name", required=True)

    sequence = fields.Integer(string="Mode Sequence", default=0)

    theme_styles = fields.One2many(
        string="Theme Styles",
        comodel_name="anita_theme_setting.theme_style",
        inverse_name="theme_mode")

    mode_template = fields.Many2one(
        comodel_name="anita_theme_setting.mode_template",
        string="Default Mode")
    template_vars = fields.Text(string="Template vars")

    # if owner is False, so the style own to global
    owner = fields.Reference(
        string="owner",
        selection=[('res.company', 'res.company'),
                   ('res.users', 'res.users')],
        default=False,
        help="owner which this theme is create by, if it is false, it mean it is owned to the system!")

    mode_style_css = fields.Text(string="Mode Style Css")
    compiled_mode_style_css = \
        fields.Text(string="Compiled mode style css", compute="compute_mode_style", store=True)

    is_default = fields.Boolean(string="Is Default", default=True)
    version = fields.Char(string="Version")

    _sql_constraints = [('theme_mode_name_unique', 'UNIQUE(name, owner)', "Theme mode name and owner must unique")]

    def get_mode_preview_data(self):
        """
        get mode preview data
        :return:
        """
        if self.mode_template:
            if not self.compiled_mode_style_css:
                self.compute_mode_style()
            mode_style_css = self.compiled_mode_style_css.replace(
                'body.{name}'.format(name=self.name), "body.mode_preview")
            return mode_style_css
        else:
            return ""

    @api.depends('mode_template')
    def compute_mode_style(self):
        """
        compute mode style
        :return:
        """
        for record in self:
            if record.mode_template:
                record.compiled_mode_style_css = record._compile_scss()

    def check_template_vars(self):
        """
        check style css
        :return:
        """
        template = self.mode_template.template
        if not template:
            return

        self.compiled_mode_style_css = self._compile_scss()
        tmp_re = re.compile(r'\s*$[\d\w]+[\s\n\r]*?]')
        template_vars = json.loads(self.template_vars)
        results = tmp_re.findall(template)
        for result in results:
            if result not in template_vars:
                raise exceptions.ValidationError(
                    '{tmp_var} not in vars!'.format(tmp_var=result))

    def _compile_scss(self):
        """
        This code will compile valid scss into css.
        Simply copied and adapted slightly
        """
        template = self.mode_template.template
        scss_source = template.strip()
        mode_name = "body.{name}".format(name=self.name)
        scss_source = scss_source.replace('body.__mode_name__', mode_name)
        scss_source = scss_source.replace(
            'body.$mode_name', "body.{name}".format(name=self.name))
        if not scss_source:
            return ""

        template_vars = json.loads(self.template_vars or "{}")
        for name, value in template_vars.items():
            scss_source = scss_source.replace(name, value)

        precision = 8
        output_style = 'expanded'

        from odoo.modules.module import get_resource_path

        bootstrap_scss_path = get_resource_path('web', 'static', 'lib', 'bootstrap', 'scss')
        awsome_mixins = get_resource_path('anita_theme_base', 'static', 'css')

        try:
            result = libsass.compile(
                string=scss_source,
                include_paths=[bootstrap_scss_path, awsome_mixins],
                output_style=output_style,
                precision=precision)
            index = result.find(mode_name)
            result = result[index:]
            return result
        except libsass.CompileError as e:
            raise libsass.CompileError(e.args[0])

    @api.model
    def compute_mode_style_url(self):
        """
        compute mode style url
        :return:
        """
        for record in self:
            record.mode_style_url = \
                '/web/image/anita_theme_setting.anita_theme_setting/{var_id}/icon128x128'.format(
                    var_id=record.id)

    def get_default_mode_style_text(self, theme_mode_info):
        """
        get default mode data
        :return:
        """
        if self.name == 'normal':
            return

        color_vars = theme_mode_info["template_vars"]
        mode_template = theme_mode_info["mode_template"]
        if not mode_template:
            raise exceptions.ValidationError('Can not find the theme template!')

        template = mode_template.template
        # css template data
        template = template.replace('$mode_name', self.name)

        # replace the var
        for var_nam in color_vars:
            template = str(template).replace(var_nam, color_vars[var_nam])

        return template

    @api.model
    def check_default_mode_data(self, owner=False):
        '''
        check default mode data
        :return:
        '''
        modes = self.search([('owner', '=', owner)])
        mode_cache = {mode.name: mode for mode in modes}

        default_modes = \
            self.env["anita_theme_setting.default_mode_data"].search([])

        # create new mode if the mode do not exits
        for default_mode in default_modes:
            mode_data = default_mode.get_mode_data()
            if default_mode.name not in mode_cache:
                mode_data["name"] = default_mode["name"]

                # create new mode use the mode data
                record = self.create_mode(mode_data, owner)
                if not record.mode_template:
                    continue

                # check the templates
                templates = self.env["anita_theme_setting.mode_template"].get_templates()
                template = mode_data.get('mode_template', False)
                if template and template not in templates:
                    raise exceptions.ValidationError(
                        '{template} do not exits!'.format(template=mode_data["template"]))

                template = templates[mode_data["mode_template"]]
                record.mode_template = template.id

                # save mode vars
                color_vars = mode_data["template_vars"]
                record.template_vars = json.dumps(color_vars)

                # check vars
                record.check_template_vars()
            else:
                # check version, if the version is different
                debug = config.get('debug', False)
                mode = mode_cache[default_mode.name]
                if debug or mode.version != mode_data["version"]:
                    color_vars = mode_data["template_vars"]
                    mode.template_vars = json.dumps(color_vars)
                    # recompile the template
                    mode.compiled_mode_style_css = False
                    mode.check_style_css()
                    mode_templates = self.env["anita_theme_setting.mode_template"].get_templates()
                    if mode_data.get("mode_template", False):
                        mode.mode_template = \
                            mode_templates.get(mode_data["mode_template"], False)
                    mode.version = mode_data["version"]
                    mode.check_mode_data()

    def create_mode(self, mode_data, owner=False, is_default=True):
        '''
        create mode
        :param mode style txt:
        :param mode_data:
        :param owner:
        :param is_default:
        :return:
        '''
        mode_templates = \
            self.env["anita_theme_setting.mode_template"].get_templates()
        mode_template = mode_data.get('mode_template', False)
        if mode_template and mode_template not in mode_templates:
            raise exceptions.ValidationError('Can not find mode template {mode_template}'.format(
                mode_template=mode_template))
        theme_styles = mode_data['theme_styles']
        theme_style_array = []
        for theme_style in theme_styles:
            groups = theme_style["groups"]
            group_datas = []
            for group_index, group in enumerate(groups):
                sub_groups = group["sub_groups"]
                sub_group_array = []
                for sub_group_index, sub_group in enumerate(sub_groups):
                    # create sub group
                    item_array = []
                    style_items = sub_group["style_items"]
                    for item_index, style_item in enumerate(style_items):
                        var_val_array = []
                        var_infos = style_item["vars"]
                        for var_index, var_info in enumerate(var_infos):
                            var_val_array.append((0, 0, {
                                "name": var_info["name"],
                                "type": var_info["type"],
                                "sequence": var_index,
                                "is_default": is_default,
                                "color": var_info.get('color', False),
                                "image": var_info.get('image', False),
                                "image_url": var_info.get('image_url', False),
                                "svg": var_info.get('svg', False),
                                "identity": var_info.get('identity', False)
                            }))
                        item_array.append((0, 0, {
                            "name": style_item["name"],
                            "is_default": is_default,
                            "sequence": item_index,
                            "val_template": style_item["val_template"],
                            "sub_group": sub_group["name"],
                            "vars": var_val_array,
                            "selectors": json.dumps(style_item["selectors"])
                        }))
                    sub_group_array.append((0, 0, {
                        "name": sub_group["name"],
                        "sequence": sub_group_index,
                        "style_items": item_array,
                        "is_default": is_default
                    }))
                group_datas.append((0, 0, {
                    "name": group["name"],
                    "sequence": group_index,
                    "is_default": is_default,
                    "sub_groups": sub_group_array
                }))

            theme_style_array.append((0, 0, {
                "name": theme_style["name"],
                "is_default": is_default,
                "groups": group_datas
            }))

        mode_template = mode_data.get("mode_template", False)
        return self.env["anita_theme_setting.theme_mode"].create([{
            "name": mode_data["name"],
            "theme_styles": theme_style_array,
            "is_default": is_default,
            "version": mode_data["version"],
            "mode_template": mode_templates[mode_template].id if mode_template else False,
            "owner": owner
        }])

    def get_mode_data(self):
        '''
        get the mode data
        :return:
        '''
        rst = []
        for record in self:
            tmp_data = record.read(['name', 'is_default', 'sequence', 'version'])[0]
            tmp_data['theme_styles'] = record.theme_styles.get_styles()
            rst.append(tmp_data)

        return rst

    def delete_mode(self):
        """
        delete the mode
        :return:
        """
        self.unlink()

    def check_style_css(self):
        """
        check style css
        :return:
        """
        if self.mode_template:
            self.compiled_mode_style_css = self._compile_scss()

    def check_mode_data(self):
        '''
        check the mode data
        :return:
        '''
        self.ensure_one()

        default_modes = self.env[
            "anita_theme_setting.default_mode_data"].search([])
        default_mode_cache = {default_mode.name: default_mode for default_mode in default_modes}

        mode_name = self.name
        if mode_name not in default_mode_cache:
            return

        theme_styles = self.theme_styles
        theme_style_cache = {theme_style.name: theme_style for theme_style in theme_styles if theme_style.is_default}

        default_mode = default_mode_cache[mode_name]
        default_mode_data = default_mode.get_mode_data()
        theme_styles = default_mode_data['theme_styles']
        for theme_style in theme_styles:
            # create new style
            style_name = theme_style['name']
            if style_name not in theme_style_cache:
                self.env["anita_theme_setting.theme_style"].create_style_from_default_data(
                    self.id, theme_style)
            else:
                # check the style data, may be one more style with the same name
                tmp_style = theme_style_cache[style_name]
                tmp_style.check_groups(theme_style["groups"])

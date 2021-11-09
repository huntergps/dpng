# -*- coding: utf-8 -*-

from odoo import models, fields


class AnitaThemeSettingBase(models.Model):
    '''
    user theme style setting
    '''
    _name = 'anita_theme_setting.setting_base'
    _description = 'User Setting Base'

    res_id = fields.Reference(
        selection=[('res.users', 'user'),
                   ('res.company', 'company')],
        string="Res Id",
        help="If it is system, Res id is false")

    first_visited = fields.Boolean(string="inited", default=False)

    layout_mode = fields.Selection(
        string="layout mode",
        selection=[('layout_mode1', 'layout_mode1'),
                   ('layout_mode2', 'layout_mode2'),
                   ('layout_mode3', 'layout_mode3')],
        default="layout_mode1")

    login_style = fields.Selection(
        string="login style",
        selection=[('login_style1', 'login_style1'),
                   ('login_style2', 'login_style2'),
                   ('login_style3', 'login_style3'),
                   ('login_style4', 'login_style4')],
        default='login_style1')

    control_panel_mode = fields.Selection(
        string="Control Panel Mode",
        selection=[('mode1', 'mode1'),
                   ('mode2', 'mode2'),
                   ('mode3', 'mode3')],
        default="mode1")

    app_tab_selected_style = fields.Selection(
        selection=[('style1', 'style1'),
                   ('style2', 'style2')],
        default='style1')

    current_theme_mode = fields.Many2one(
        comodel_name='anita_theme_setting.theme_mode',
        string="Current Theme Mode")

    current_theme_style = fields.Many2one(
        string="Current Theme Style",
        comodel_name="anita_theme_setting.theme_style",
        domain="[('theme_mode', '=', current_theme_mode)]",
        help="just use when theme style mode is system")

    dialog_pop_style = fields.Selection(
        string="dialog pop up style",
        selection=[('normal', 'normal'),
                   ('awesome-effect-scale', 'scale'),
                   ('awesome-effect-slide-in-right', 'slide-in-right'),
                   ('awesome-effect-slide-in-bottom', 'slide-in-bottom'),
                   ('awesome-effect-fall', 'awesome-fall'),
                   ('awesome-effect-flip-horizontal', 'flip-horizontal'),
                   ('awesome-effect-effect-flip-vertical', 'flip-vertical'),
                   ('awesome-effect-super-scaled', 'super-scaled'),
                   ('awesome-effect-sign-in', 'sign-in'),
                   ('awesome-effect-effect-newspaper', 'effect-newspaper'),
                   ('awesome-effect-rotate-bottom', 'rotate-bottom'),
                   ('awesome-effect-rotate-left', 'rotate-left')],
        default='normal')

    button_style = fields.Selection(
        string="Button Style",
        selection=[("btn-style-normal", "btn-style-normal"),
                   ("btn-round", "btn-round"),
                   ("btn-style-slant", "btn-style-slant")],
        default="btn-style-normal")

    table_style = fields.Selection(
        string="table style",
        selection=[('normal', 'normal'),
                   ('bordered', 'bordered')],
        default="normal")

    font_name = fields.Selection(
        string="Font Name",
        selection=[('Roboto', 'Roboto'),
                   ('sans-serif', 'sans-serif'),
                   ('Helvetica', 'Helvetica'),
                   ('Arial', 'Arial'),
                   ('Verdana', 'Verdana'),
                   ('Tahoma', 'Tahoma'),
                   ('Trebuchet MS', 'Trebuchet MS')],
        default="Roboto")

    show_app_name = fields.Boolean(string="Show App Name", default=True)
    rtl_mode = fields.Boolean(string="RTL MODE", default=False)
    allow_debug = fields.Boolean(string="Allow Debug", default=True)

    system = fields.Boolean(string="system", default=False)

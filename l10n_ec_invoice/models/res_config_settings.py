from ast import literal_eval
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    driver_id = fields.Many2one('res.partner', string="Chofer para Guias de Remision",
            company_dependent=True)

    sale_customer_id = fields.Many2one('res.partner', string="Cliente en Ventas",
            company_dependent=True)

    placa_vehiculo = fields.Char("Chofer para Guias de Remision", company_dependent=True)

    # sale_acuerdo_id = fields.Many2one('sale.order.agreement', string='Acuerdo de Pago',
    #         company_dependent=True)

    #IVA

    product_sale_tax_id = fields.Many2one('account.tax', string="Impuesto de Ventas para Productos",
            company_dependent=True)
    product_purchase_tax_id = fields.Many2one('account.tax', string="Impuesto de Compras para Productos",
            company_dependent=True)
    service_sale_tax_id = fields.Many2one('account.tax', string="Impuesto de Ventas para Servicios",
        company_dependent=True)
    service_purchase_tax_id = fields.Many2one('account.tax', string="Impuesto de Compras para Servicios",
        company_dependent=True)

    consu_sale_tax_id = fields.Many2one('account.tax', string="Impuesto de Ventas para Consumibles",
        company_dependent=True)
    consu_purchase_tax_id = fields.Many2one('account.tax', string="Impuesto de Compras para Consumibles",
        company_dependent=True)

    #IVA 0
    product0_sale_tax_id = fields.Many2one('account.tax', string="Impuesto de Ventas IVA 0 para Productos",
        company_dependent=True)
    product0_purchase_tax_id = fields.Many2one('account.tax', string="Impuesto de Compras IVA 0 para Productos",
        company_dependent=True)

    service0_sale_tax_id = fields.Many2one('account.tax', string="Impuesto de Ventas IVA 0 para Servicios",
        company_dependent=True)
    service0_purchase_tax_id = fields.Many2one('account.tax', string="Impuesto de Compras IVA 0 para Servicios",
        company_dependent=True)

    consu0_sale_tax_id = fields.Many2one('account.tax', string="Impuesto de Ventas IVA 0 para Consumibles",
        company_dependent=True)
    consu0_purchase_tax_id = fields.Many2one('account.tax', string="Impuesto de Compras IVA 0 para Consumibles",
        company_dependent=True)


    product_categ_id = fields.Many2one(
        'product.category', 'Categoria para Productos')
    consu_categ_id = fields.Many2one(
        'product.category', 'Categoria para Consumibles')
    service_categ_id = fields.Many2one(
        'product.category', 'Categoria para Servicios')

    tipo_homologacion = fields.Selection(
        [
            ('auto', 'Homologación automática'),
            ('manual', 'Homologación manual')
            ],
        'Tipo de Homologación',default='manual')

    metodo_importacion = fields.Selection(
        [
            ('new', 'Crear Orden de Compra'),
            #('compare', 'Comparar Orden de Compra')
            ],
        'Método de Importación',default='new')

    state_purchase_orders = fields.Selection(
        [
            ('draft', 'En borrador'),
            ('done', 'Procesar')
            ],
        'Estado de Ordenes de Compras',default='draft')

    email_sri = fields.Char("Email para Documentos electronicos", company_dependent=True)
    email_cobros = fields.Char("Email para Cobros", company_dependent=True)
    email_contabilidad = fields.Char("Email para Contabilidad", company_dependent=True)
    email_soporte = fields.Char("Email para HelpDesk", company_dependent=True)
    nota_proforma = fields.Text("Nota para Impresion de Ventas", company_dependent=True)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        email_sri  = ICPSudo.get_param('email_sri')
        email_cobros  = ICPSudo.get_param('email_cobros')
        email_contabilidad  = ICPSudo.get_param('email_contabilidad')
        email_soporte  = ICPSudo.get_param('email_soporte')
        nota_proforma  = ICPSudo.get_param('nota_proforma')
        placa_vehiculo  = ICPSudo.get_param('placa_vehiculo')


        sale_customer_id  = literal_eval(ICPSudo.get_param('sale_customer_id', default='False'))
        driver_id = literal_eval(ICPSudo.get_param('driver_id', default='False'))
        # sale_acuerdo_id  = literal_eval(ICPSudo.get_param('sale_acuerdo_id', default='False'))

        #IVA
        product_sale_tax_id = literal_eval(ICPSudo.get_param('product_sale_tax_id', default='False'))
        product_purchase_tax_id = literal_eval(ICPSudo.get_param('product_purchase_tax_id', default='False'))
        service_sale_tax_id = literal_eval(ICPSudo.get_param('service_sale_tax_id', default='False'))
        service_purchase_tax_id = literal_eval(ICPSudo.get_param('service_purchase_tax_id', default='False'))
        consu_sale_tax_id = literal_eval(ICPSudo.get_param('consu_sale_tax_id', default='False'))
        consu_purchase_tax_id = literal_eval(ICPSudo.get_param('consu_purchase_tax_id', default='False'))
        #IVA 0
        product0_sale_tax_id = literal_eval(ICPSudo.get_param('product0_sale_tax_id', default='False'))
        product0_purchase_tax_id = literal_eval(ICPSudo.get_param('product0_purchase_tax_id', default='False'))
        service0_sale_tax_id = literal_eval(ICPSudo.get_param('service0_sale_tax_id', default='False'))
        service0_purchase_tax_id = literal_eval(ICPSudo.get_param('service0_purchase_tax_id', default='False'))
        consu0_sale_tax_id = literal_eval(ICPSudo.get_param('consu0_sale_tax_id', default='False'))
        consu0_purchase_tax_id = literal_eval(ICPSudo.get_param('consu0_purchase_tax_id', default='False'))

        product_categ_id = literal_eval(ICPSudo.get_param('product_categ_id', default='False'))
        service_categ_id = literal_eval(ICPSudo.get_param('service_categ_id', default='False'))
        consu_categ_id = literal_eval(ICPSudo.get_param('consu_categ_id', default='False'))

        tipo_homologacion = ICPSudo.get_param('tipo_homologacion', default='manual')
        metodo_importacion = ICPSudo.get_param('metodo_importacion', default='new')
        state_purchase_orders = ICPSudo.get_param('state_purchase_orders', default='draft')


        res.update(
            sale_customer_id = sale_customer_id,
            driver_id = driver_id,
            # sale_acuerdo_id = sale_acuerdo_id,

            email_sri = email_sri,
            email_cobros = email_cobros,
            email_contabilidad = email_contabilidad,
            email_soporte = email_soporte,
            nota_proforma =nota_proforma,
            placa_vehiculo = placa_vehiculo,

            #IVA
            product_sale_tax_id=product_sale_tax_id,
            product_purchase_tax_id=product_purchase_tax_id,
            service_sale_tax_id=service_sale_tax_id,
            service_purchase_tax_id=service_purchase_tax_id,
            consu_sale_tax_id=consu_sale_tax_id,
            consu_purchase_tax_id=consu_purchase_tax_id,
            #IVA 0
            product0_sale_tax_id=product0_sale_tax_id,
            product0_purchase_tax_id=product0_purchase_tax_id,
            service0_sale_tax_id=service0_sale_tax_id,
            service0_purchase_tax_id=service0_purchase_tax_id,
            consu0_sale_tax_id=consu0_sale_tax_id,
            consu0_purchase_tax_id=consu0_purchase_tax_id,

            product_categ_id=product_categ_id,
            service_categ_id=service_categ_id,
            consu_categ_id=consu_categ_id,

            tipo_homologacion = tipo_homologacion,
            metodo_importacion = metodo_importacion,
            state_purchase_orders = state_purchase_orders,
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        ICPSudo.set_param("email_sri", self.email_sri)
        ICPSudo.set_param("email_cobros", self.email_cobros)
        ICPSudo.set_param("email_contabilidad", self.email_contabilidad)
        ICPSudo.set_param("email_soporte", self.email_soporte)
        ICPSudo.set_param("nota_proforma", self.nota_proforma)
        ICPSudo.set_param("placa_vehiculo", self.placa_vehiculo)


        ICPSudo.set_param("sale_customer_id", self.sale_customer_id.id)
        ICPSudo.set_param("driver_id", self.driver_id.id)

        # ICPSudo.set_param("sale_acuerdo_id", self.sale_acuerdo_id.id)

        #IVA
        ICPSudo.set_param("product_sale_tax_id", self.product_sale_tax_id.id)
        ICPSudo.set_param("product_purchase_tax_id", self.product_purchase_tax_id.id)
        ICPSudo.set_param("service_sale_tax_id", self.service_sale_tax_id.id)
        ICPSudo.set_param("service_purchase_tax_id", self.service_purchase_tax_id.id)
        ICPSudo.set_param("consu_sale_tax_id", self.consu_sale_tax_id.id)
        ICPSudo.set_param("consu_purchase_tax_id", self.consu_purchase_tax_id.id)
        #IVA 0
        ICPSudo.set_param("product0_sale_tax_id", self.product0_sale_tax_id.id)
        ICPSudo.set_param("product0_purchase_tax_id", self.product0_purchase_tax_id.id)
        ICPSudo.set_param("service0_sale_tax_id", self.service0_sale_tax_id.id)
        ICPSudo.set_param("service0_purchase_tax_id", self.service0_purchase_tax_id.id)
        ICPSudo.set_param("consu0_sale_tax_id", self.consu0_sale_tax_id.id)
        ICPSudo.set_param("consu0_purchase_tax_id", self.consu0_purchase_tax_id.id)

        ICPSudo.set_param("product_categ_id", self.product_categ_id.id)
        ICPSudo.set_param("service_categ_id", self.service_categ_id.id)
        ICPSudo.set_param("consu_categ_id", self.consu_categ_id.id)

        ICPSudo.set_param("tipo_homologacion", self.tipo_homologacion)
        ICPSudo.set_param("metodo_importacion", self.metodo_importacion)
        ICPSudo.set_param("state_purchase_orders", self.state_purchase_orders)

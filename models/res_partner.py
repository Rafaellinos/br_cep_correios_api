from openerp import models, fields, api
import requests
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zip = fields.Char(string=u'CEP')
    street = fields.Char(string=u'Endereço')

    @api.multi
    @api.onchange('zip')
    def search_cep(self):
        if len(zip)== 8:
            #raise Warning(str(dados))
            #cep = '03072000'
            url_api = ('https://viacep.com.br/ws/%s/json' % self.zip)
            r = requests.get(url_api)
            dados = json.loads(r.text)
            self.street = str(dados)
from openerp import models, fields, api, _
import requests
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zip = fields.Char(string=u'CEP')
    street = fields.Char(string=u'Endereço')
    street2 = fields.Char(string=u'Bairro')
    city = fields.Char(string=u'Cidade')
    state_id = fields.Many2one(
        string=u'Estado',
        comodel_name='res.country.state',
        ondelete='restrict',
        domain="[('country_id', '=?', country_id)]")


    @api.onchange('zip')
    def search_cep(self):
        if self.zip:
            if len(self.zip) == 8:
                #raise Warning(str(dados))
                #cep = '03072000'
                url_api = ('https://viacep.com.br/ws/%s/json' % self.zip)
                response = requests.get(url_api)
                if response.status_code == 200:
                    dict_api = json.loads(response.text)
                    #raise Warning(dict_api['logradouro'])
                    state = self.env['res.country.state'].search([('code','=', dict_api['uf'])], limit=1)
                    if state:
                        self.state_id = state.id
                    self.street = dict_api['logradouro']
                    self.city = dict_api['localidade']
                    self.street2 = dict_api['bairro']

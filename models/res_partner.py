from odoo import models, fields, api
from odoo.exceptions import ValidationError
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
            zip_last = self.zip.replace('-','').replace(';','').replace('--','').replace(')','').replace('(','').replace(' ','')
            if len(zip_last) == 8:
                url_api = ('https://viacep.com.br/ws/%s/json' % zip_last)
                response = requests.get(url_api)
                if response.status_code == 200:
                    dict_api = json.loads(response.text)
                    if 'erro' in dict_api.keys():
                        raise ValidationError(('CEP inválido ou não encontrado'))
                    else:
                        br_country = self.env['res.country'].search([('name','=', 'Brasil')], limit=1)
                        state = self.env['res.country.state'].search([('code','=', dict_api['uf']),('country_id','=',br_country.id)], limit=1)
                        if state:
                            self.state_id = state.id
                        self.street = dict_api['logradouro']
                        self.city = dict_api['localidade']
                        self.street2 = dict_api['bairro']

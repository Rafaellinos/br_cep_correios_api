from odoo import models, api
import requests


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_cep_endpoint(self):
        return self.env['ir.config_parameter'].sudo().get_param('viacep_endpoint', default=False)

    def _get_cep(self, cep):
        endpoint = self._get_cep_endpoint()
        try:
            r = requests.get(f"{endpoint}/ws/{cep}/json")
            if r.status_code == 200:
                if not 'err' in dict(r.json()).keys():
                    return r.json()
                return None
            return None
        except Exception as err:
            print(f"ERROR API VIACEP: {err}")
            return None


    @api.onchange('zip')
    def search_cep(self):
        for record in self:
            
            zip_code = record.zip
            if not zip_code:
                return 

            to_replece = [('-',''),(';',''),('--',''),(')',''),(')','')]
            for i in to_replece:
                zip_code = zip_code.replace(i[0],i[1])

            if not all(x.isdigit() for x in zip_code):
                return
            
            cep = self._get_cep(zip_code)
            if cep:
                br_country = self.env['res.country'].search([('name','=', 'Brasil')], limit=1).id
                state = self.env['res.country.state'].search([('code','=', cep.get('uf'))], limit=1).id
                record.write({
                    'street': cep.get('logradouro'),
                    'street2': cep.get('bairro'),
                    'country_id': br_country,
                    'state_id': state,
                    'city': cep.get('localidade')})

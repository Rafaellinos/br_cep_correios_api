
import requests
from requests.exceptions import Timeout, InvalidSchema
import logging
import re

from odoo import models, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_cep_endpoint(self):
        return self.env['ir.config_parameter'].sudo().get_param('viacep_endpoint', default=False)

    def _get_cep(self, cep):
        endpoint = self._get_cep_endpoint()
        if not endpoint:
            raise ValidationError(_("The param \"viacep_endpoint\" is mandatory!"))
        try:
            r = requests.get(f"{endpoint}/ws/{cep}/json", timeout=5)
            if r.status_code == 200:
                if 'err' not in dict(r.json()).keys():
                    return r.json()
        except Timeout:
            _logger.error(_("timeout viacep connection"))
        except InvalidSchema:
            _logger.error(_("invalid url scheme for viacep param"))


    @api.onchange('zip')
    def search_cep(self):
        for record in self:
            
            zip_code = record.zip
            if not zip_code:
                return 

            cep = self._get_cep(re.sub(r'[^0-9]+', r'', zip_code))
            if cep:
                br_country = self.env['res.country'] \
                    .with_context(lang='en_US') \
                    .search([('name','=', 'Brazil')], limit=1)

                state = self.env['res.country.state'] \
                    .search([('code','=', cep.get('uf'))], limit=1)

                record.write({
                    'street': cep.get('logradouro'),
                    'street2': cep.get('bairro'),
                    'country_id': getattr(br_country, "id", False),
                    'state_id': getattr(state, "id", False),
                    'city': cep.get('localidade')})

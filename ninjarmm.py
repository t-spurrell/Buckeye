from requests import get, post, put, patch
from configuration import load_config


class Ninjarmm:

    def __init__(self, host, client_id, client_secret):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.creds = client_id, client_secret
        self.token = self.get_token()

    def get_token(self):
        auth_url = f'{self.host}/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'scope': 'monitoring management'
        }
        response = post(url=auth_url, auth=self.creds, data=data)
        access_token = response.json()['access_token']
        #print(json.dumps(response.json(),indent=4))
        return access_token

    def post_data(self, endpoint, data):
        url = f'{self.host}/{endpoint}'
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        return post(url, json=data, headers=headers)

    def patch_data(self, endpoint, data):
        url = f'{self.host}/{endpoint}'
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        return patch(url, json=data, headers=headers)

    def create_new_org(self, name, halo_id):
        payload = {
            "name": name,
            "description": str(halo_id)
                  }
        result = self.post_data('api/v2/organizations', payload)
        return result

    def update_org(self, name, halo_id):
        orgs = self.get_orgs()
        for org in orgs:
            if 'description' in org and org['description'] == str(halo_id):
                ninja_id = org['id']
                payload = {
                    "name": name
                          }
                result = self.patch_data(f'api/v2/organization/{ninja_id}', payload)
                return result

    def get_orgs(self):
        url = f'{self.host}/v2/organizations'
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        #print(response.json())
        if response.ok:
            org_data = response.json()
            #print(org_data)
            return org_data

# CONFIG = load_config()
# t = Ninjarmm('https://app.ninjarmm.com', CONFIG['ninjarmm']['id'], CONFIG['ninjarmm']['secret'])
#
# t.update_org('trevor',123)


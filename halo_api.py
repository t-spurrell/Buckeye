from requests import get, post, put, patch
from configuration import load_config

CONFIG = load_config()


class HaloAPI:

    def __init__(self, host, client_id, client_secret):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.creds = client_id, client_secret
        self.token = self.get_token()

    def get_token(self):
        auth_url = 'https://buckeyecloud.halopsa.com/auth/token'
        data = {
            'grant_type': 'client_credentials',
            'scope': 'all'
        }
        response = post(url=auth_url, auth=self.creds, data=data)
        access_token = response.json()['access_token']
        return access_token

    def post_data(self, endpoint, data):
        url = f'{self.host}/{endpoint}'
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        return post(url, json=data, headers=headers)

    def get_clients(self):
        url = f"{self.host}/client"
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        if response.ok:
            client_data = response.json()
            return client_data['clients']

    def get_user_email(self, user_id):
        print('GET EMAIL FUNCTION CALLED')
        url = f"{self.host}/users/{user_id}"
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        if response.ok:
            user_data = response.json()
            email = (user_data['emailaddress'])
            return email

    def get_site_details(self, site_id):
        url = f"{self.host}/site/{site_id}"
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        if response.ok:
            site_data = response.json()
            phone_num = site_data['phonenumber']
            address = {
                'street': site_data['delivery_address']['line1'],
                'city': site_data['delivery_address']['line2'],
                'state': site_data['delivery_address']['line3'],
                'zip_code': site_data['delivery_address']['postcode']
            }
            return phone_num, address

    def get_id_from_name(self, client_name):
        client_list = self.get_clients()
        for client in client_list:
            if client["name"] == client_name:
                return client['id']
        return None


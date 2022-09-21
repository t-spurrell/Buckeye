from requests import get,post,put
from configuration import load_config

CONFIG = load_config()


class InvoiceNinja:

    def __init__(self, host):
        self.host = host
        self.token = CONFIG['invoice_ninja']['token']

    def post_data(self, endpoint, data):
        url = f'{self.host}/{endpoint}'
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        return post(url, json=data, headers=headers)

    def put_data(self, endpoint, data):
        url = f'{self.host}/{endpoint}'
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        return put(url, json=data, headers=headers)

    def create_new_client(self, name, halo_id, website, address, phone):
        # if ' ' in main_contact.strip():
        #     first_name, last_name = main_contact.split()
        # else:
        #     first_name = main_contact
        #     last_name = ' '
        payload = {
            "name": name,
            "website": website,
            "address1": address['street'],
            "city": address['city'],
            "state": address['state'],
            "postal_code": address['zip_code'],
            "phone": phone,
            "private_notes": str(halo_id),
            "settings": {
                "send_reminders": True
            }
                  }
        result = self.post_data('clients', payload)
        return result

    def update_client(self, invoice_ninja_client_id, name, website, address, phone, main_contact, email):
        # active_clients = self.get_clients()
        # for client in active_clients:
        #     if client['private_notes'] == str(halo_id):
        #         invoice_ninja_client_id = client['id']
        if ' ' in main_contact.strip():
            first_name, last_name = main_contact.split()
        else:
            first_name = main_contact
            last_name = ' '
        payload = {
            "name": name,
            "website": website,
            "address1": address['street'],
            "city": address['city'],
            "state": address['state'],
            "postal_code": address['zip_code'],
            "phone": phone,
            "contacts": [
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone
                }
            ]
        }
        result = self.put_data(f'clients/{invoice_ninja_client_id}', payload)
        return result

    def create_user(self, invoice_ninja_id, first_name, last_name, email, phone):
        payload = {
            "contacts": [
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone
                }
            ]
        }
        result = self.put_data(f'clients/{invoice_ninja_id}', payload)
        return result

    def get_invoice_ninja_id(self, halo_id):
        active_clients = self.get_clients()
        #print(active_clients)
        for client in active_clients:
            if client['private_notes'] == str(halo_id):
                #print(client['id'])
                return client['id']
        return None

    def get_clients(self):
        url = f'{self.host}/clients'
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        #print(response)
        if response.ok:
            data = response.json()
            clients = data['data']
            active_clients = [client for client in clients if client['is_deleted'] is False]
            return active_clients



# t = InvoiceNinja(CONFIG['invoice_ninja']['base_url'])
# print(t.get_invoice_ninja_id('21'))
#
# client = t.get_invoice_ninja_id()
# if client is not None:
#     print(client)
# else:
#     print('no such client')



# f = t.create_new_client('test1','101010','testweb.com',{'street':'1212 my street','city':'test city','state':'MD','zip_code':'21784'},'1128553498','Bruce','bruce@main.com')
# print(f)
#t.update_client(20)
# a = t.get_clients()
# for i in a:
#     print(i)
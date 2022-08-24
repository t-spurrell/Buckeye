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

    def create_new_client(self, name, halo_id, website, address, phone, main_contact, email):
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
            "private_notes": str(halo_id),
            "settings": {
                "send_reminders": True
            },
            "contacts": [
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone
                }
            ]
                  }
        result = self.post_data('clients', payload)
        return result

    def update_client(self, halo_id, name, website, address, phone, main_contact, email):
        clients = self.get_clients()
        for client in clients:
            if client['private_notes'] == str(halo_id):
                invoice_ninja_client_id = client['id']
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



#t = InvoiceNinja('https://invoicing.co/api/v1')
# f = t.create_new_client('test1','101010','testweb.com',{'street':'1212 my street','city':'test city','state':'MD','zip_code':'21784'},'1128553498','Bruce','bruce@main.com')
# print(f)
#t.update_client(20)
# a = t.get_clients()
# for i in a:
#     print(i)
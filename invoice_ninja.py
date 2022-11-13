from requests import get, post, put
from configuration import load_config
import json

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

    def update_client(self, invoice_ninja_client_id, name, website, address, phone, main_contact=None, email=None):
        # if ' ' in main_contact.strip():
        #     first_name, last_name = main_contact.split()
        # else:
        #     first_name = main_contact
        #     last_name = ' '
        users = self.get_users_for_client(invoice_ninja_client_id)
        payload = {
            "name": name,
            "website": website,
            "address1": address['street'],
            "city": address['city'],
            "state": address['state'],
            "postal_code": address['zip_code'],
            "phone": phone,
            "contacts": users

        }
        result = self.put_data(f'clients/{invoice_ninja_client_id}', payload)
        return result

    def create_user(self, invoice_ninja_id, first_name, last_name, email, phone, halo_user_id):
        users = self.get_users_for_client(invoice_ninja_id)
        new_user = {'first_name': first_name, 'last_name': last_name, 'email': email,
                    'phone': phone, 'custom_value1': halo_user_id}
        users.append(new_user)
        payload = {
            "contacts": users
        }
        result = self.put_data(f'clients/{invoice_ninja_id}', payload)
        return result

    def update_user(self, invoice_ninja_id, first_name, last_name, email, phone, halo_user_id):
        users = self.get_users_for_client(invoice_ninja_id)
        user_exist = False
        for user in users:
            if user['custom_value1'] == halo_user_id:
                user_exist = True
                user['first_name'] = first_name
                user['last_name'] = last_name
                user['email'] = email
                user['phone'] = phone
        if not user_exist:
            print(f'the user trying to be updated: {first_name} is not in invoiceninja')
            new_user = {'first_name': first_name, 'last_name': last_name, 'email': email,
                        'phone': phone, 'custom_value1': halo_user_id}
            users.append(new_user)
        payload = {"contacts": users}
        result = self.put_data(f'clients/{invoice_ninja_id}', payload)
        return result

    def delete_user(self, invoice_ninja_id, halo_user_id):
        print("Inside ninja delete function")
        users = self.get_users_for_client(invoice_ninja_id)
        print(users)
        user_exist = False
        for i, user in enumerate(users):
            if user['custom_value1'] == str(halo_user_id):
                user_exist = True
                print(f'removing user {user["first_name"]}')
                users.pop(i)
                break
        if not user_exist:
            print(f'user {halo_user_id} does not exist in invoice ninja for client {invoice_ninja_id}')
        payload = {"contacts": users}
        result = self.put_data(f'clients/{invoice_ninja_id}', payload)
        return result

    def get_invoice_ninja_id(self, halo_id):
        active_clients = self.get_clients()
        for client in active_clients:
            if client['private_notes'] == str(halo_id):
                return client['id']
        return None

    def get_clients(self):
        url = f'{self.host}/clients'
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        if response.ok:
            data = response.json()
            clients = data['data']
            active_clients = [client for client in clients if client['is_deleted'] is False]
            return active_clients

    def get_users_for_client(self, invoice_id):
        url = f'{self.host}/clients/{invoice_id}'
        headers = {'X-API-Token': self.token, 'Content-Type': 'application/json'}
        response = get(url=url, headers=headers)
        if response.ok:
            data = response.json()
            users = data['data']['contacts']
            return users



# t = InvoiceNinja(CONFIG['invoice_ninja']['base_url'])
# u = t.get_users_for_client('1aKrGVyReQ')
# print(u)



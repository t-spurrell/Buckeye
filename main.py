import secrets
from fastapi import FastAPI,Response,Request,Body,status,Depends,HTTPException
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from configuration import load_config
from invoice_ninja import InvoiceNinja
from ninjarmm import Ninjarmm
from halo_api import HaloAPI


CONFIG = load_config()

#Auth to NinjaRMM api
ninja_rmm_conn = Ninjarmm(CONFIG['ninjarmm']['base_url'], CONFIG['ninjarmm']['id'], CONFIG['ninjarmm']['secret'])
#Auth to Halo api
halo_api_conn = HaloAPI(CONFIG['halo_api']['base_url'], CONFIG['halo_api']['id'], CONFIG['halo_api']['secret'])
#Auth to InvoiceNinja api
invoice_ninja_conn = InvoiceNinja(CONFIG['invoice_ninja']['base_url'])


app = FastAPI()
security = HTTPBasic()


@app.get('/')
def root():
    print("hit the root")
    return {"message": "Welcome to the root!"}


@app.post("/create_client", status_code=status.HTTP_201_CREATED)
async def create_client(request: dict = Body(), credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, CONFIG['halo_webhook']['username'])
    correct_password = secrets.compare_digest(credentials.password, CONFIG['halo_webhook']['password'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    print("landed at the create_client endpoint!")
    client_name = request['client']['name']
    halo_id = int(request['client']['id'])
    website = request['client']['website']
    site_id = request['client']['main_site_id']

    #create acct in ninjaRMM
    rmm_result = ninja_rmm_conn.create_new_org(client_name, halo_id)
    print(rmm_result)

    #create acct in InvoiceNinja
    invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)
    if invoice_ninja_id is None:
        phone_num, address = halo_api_conn.get_site_details(site_id)
        invoice_result = invoice_ninja_conn.create_new_client(client_name, halo_id, website, address, phone_num)
        print(invoice_result)


@app.post("/update_client", status_code=status.HTTP_201_CREATED)
async def update_client(request: dict = Body(), credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, CONFIG['halo_webhook']['username'])
    correct_password = secrets.compare_digest(credentials.password, CONFIG['halo_webhook']['password'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    print('update client endpoint')
    if request['event'] == 'client updated':
        print('event = client update')
        client_name = request['client']['name']
        halo_id = int(request['client']['id'])
        website = request['client']['website']
        site_id = request['client']['main_site_id']
        #phone_num, main_contact_user_id, main_contact_name, address = halo_api_conn.get_site_details(site_id)
        phone_num, address = halo_api_conn.get_site_details(site_id)
        #email = halo_api_conn.get_user_email(main_contact_user_id)
    if request['event'] == 'site updated':
        print('event = site update')
        client_name = request['site']['client']['name']
        halo_id = int(request['site']['client']['id'])
        website = request['site']['client']['website']
        address = {
            'street': request['site']['delivery_address']['line1'],
            'city': request['site']['delivery_address']['line2'],
            'state': request['site']['delivery_address']['line3'],
            'zip_code': request['site']['delivery_address']['postcode']
        }
        phone_num = request['site']['phonenumber']

    #Update NinjaRMM
    rmm_result = ninja_rmm_conn.update_org(client_name, halo_id)
    print(rmm_result)

    #Update Invoice Ninja
    invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)
    if invoice_ninja_id is not None:
        invoice_result = invoice_ninja_conn.update_client(invoice_ninja_id, client_name, website, address, phone_num)
        print(invoice_result)
    else:
        print(f'Error no such client with halo id of {halo_id} found in InvoiceNinja')


@app.post("/delete_client", status_code=status.HTTP_201_CREATED)
async def delete_client(request: dict = Body(), credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, CONFIG['halo_webhook']['username'])
    correct_password = secrets.compare_digest(credentials.password, CONFIG['halo_webhook']['password'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    if request['event'] == 'client deleted':
        halo_id = request['object_id']
        invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)
        if invoice_ninja_id is not None:
            print("deleting client")
            invoice_ninja_conn.delete_client(invoice_ninja_id)


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(request: dict = Body(), credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, CONFIG['halo_webhook']['username'])
    correct_password = secrets.compare_digest(credentials.password, CONFIG['halo_webhook']['password'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    if request['user']['name'] != 'General User':
        halo_id = int(request['user']['site']['client_id'])
        halo_user_id = str(request['user']['id'])
        first_name = request['user']['firstname']
        if request['user']['surname'] is not None:
            last_name = request['user']['surname']
        else:
            last_name = ''
        email = request['user']['emailaddress']
        phone = request['user']['phonenumber_preferred']

        invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)
        preexisting_client = True
        if invoice_ninja_id is None:
            preexisting_client = False
            print('Got webhook to add user, but client does not exist in invoiceninja. Adding client now!')
            client_name = request['user']['site']['client']['name']
            website = request['user']['site']['client']['website']
            address = {
                    'street': request['user']['site']['delivery_address']['line1'],
                    'city': request['user']['site']['delivery_address']['line2'],
                    'state': request['user']['site']['delivery_address']['line3'],
                    'zip_code': request['user']['site']['delivery_address']['postcode']
            }
            phone_num = request['user']['sitephonenumber']
            invoice_result = invoice_ninja_conn.create_new_client(client_name, halo_id, website, address, phone_num)
            print(invoice_result)
            invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)
            print('client created in invoiceninja')
            #print(f'creating client {client_name} {halo_id} {website} {address} {phone_num}')
        invoice_add_user_result = invoice_ninja_conn.create_user(invoice_ninja_id, first_name,
                                                                 last_name, email, phone, halo_user_id)
        print(invoice_add_user_result)
        if not preexisting_client:
            #remove default blank user created when a new client is made in invoice ninja
            print('removing blank user from client creation')
            invoice_ninja_conn.remove_blank_user(invoice_ninja_id)


@app.post("/update_user", status_code=status.HTTP_201_CREATED)
async def update_user(request: dict = Body(), credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, CONFIG['halo_webhook']['username'])
    correct_password = secrets.compare_digest(credentials.password, CONFIG['halo_webhook']['password'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    if request['user']['name'] != 'General User':
        halo_id = int(request['user']['site']['client_id'])
        halo_user_id = str(request['user']['id'])
        first_name = request['user']['firstname']
        if request['user']['surname'] is not None:
            last_name = request['user']['surname']
        else:
            last_name = ''
        email = request['user']['emailaddress']
        phone = request['user']['phonenumber_preferred']
        invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)

        invoice_update_user_result = invoice_ninja_conn.update_user(invoice_ninja_id, first_name,
                                                                    last_name, email, phone, halo_user_id)
        print(invoice_update_user_result)


@app.post("/delete_user", status_code=status.HTTP_201_CREATED)
async def delete_user(request: dict = Body(), credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, CONFIG['halo_webhook']['username'])
    correct_password = secrets.compare_digest(credentials.password, CONFIG['halo_webhook']['password'])
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    deleted_user_id = request['object_id']
    details = request['message']
    client_name = details[details.find("(")+1:details.find(")")].split(':')[0]
    halo_id = halo_api_conn.get_id_from_name(client_name)
    invoice_ninja_id = invoice_ninja_conn.get_invoice_ninja_id(halo_id)
    if invoice_ninja_id is not None:
        invoice_ninja_conn.delete_user(invoice_ninja_id, deleted_user_id)

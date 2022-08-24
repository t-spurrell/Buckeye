import secrets
from fastapi import FastAPI,Response,Request,Body,status,Depends,HTTPException
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from configuration import load_config
from invoice_ninja import InvoiceNinja
from ninjarmm import Ninjarmm
from halo_api import HaloAPI
import json

CONFIG = load_config()

#Auth to NinjaRMM api
ninja_rmm_conn = Ninjarmm(CONFIG['ninjarmm']['base_url'], CONFIG['ninjarmm']['id'], CONFIG['ninjarmm']['secret'])
#Auth to Halo api
halo_api_conn = HaloAPI(CONFIG['halo_api']['base_url'], CONFIG['halo_api']['id'], CONFIG['halo_api']['secret'])
#Auth to InvoiceNinja
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
    print("landed at the create endpoint!")
    client_name = request['client']['name']
    halo_id = request['client']['id']
    website = request['client']['website']
    site_id = request['client']['main_site_id']
    phone_num, main_contact_user_id, main_contact_name, address = halo_api_conn.get_site_details(site_id)
    email = halo_api_conn.get_user_email(main_contact_user_id)

    #create acct in ninjaRMM
    rmm_result = ninja_rmm_conn.create_new_org(client_name, halo_id)
    print(rmm_result)

    #create acct in InvoiceNinja
    invoice = invoice_ninja_conn.create_new_client(client_name, halo_id, website, address, phone_num, main_contact_name, email)
    print(invoice)
    # string = json.dumps(request,indent=4)
    # print(string)


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
    client_name = request['client']['name']
    halo_id = request['client']['id']
    website = request['client']['website']
    site_id = request['client']['main_site_id']
    phone_num, main_contact_user_id, main_contact_name, address = halo_api_conn.get_site_details(site_id)
    email = halo_api_conn.get_user_email(main_contact_user_id)

    #Update NinjaRMM
    rmm_result = ninja_rmm_conn.update_org(client_name, halo_id)
    print(rmm_result)

    #Update Invoice Ninja
    invoice = invoice_ninja_conn.update_client(halo_id, client_name, website, address, phone_num, main_contact_name, email)
    print(invoice)


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
    print(request)


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
    print(request)

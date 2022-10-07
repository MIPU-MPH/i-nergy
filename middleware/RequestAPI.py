#Esempio di chiamata REST APi di Rebecca with request python library
from urllib.error import HTTPError
import requests
from requests.auth import HTTPBasicAuth


try:
    api_url = "https://training.rebecca.mipu.eu/api/targeting/client/v1/client_operative_instance/using_predictive_model/?predictive_model_id=101"
    headers =  {"Content-Type":"application/json"}
    response = requests.get(api_url, auth=HTTPBasicAuth('Admin', 'inspiring'), headers=headers)
    response.raise_for_status()
    print(response.json())
    print(response.status_code)
    print(response.headers)
    jsonresp = response.json()
    print("Print each key-value pair from JSON response")
    for lkey in jsonresp:
        for key in lkey:
            print(key, ":", lkey[key])

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')


# Come fare il parsing del json ?
#Post request example:

#todo = {"userId": 1, "title": "Buy milk", "completed": False}
#response = requests.post(api_url, json=todo)
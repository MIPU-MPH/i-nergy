#from asyncio.windows_events import NULL
from logging import getLogger
from threading import TIMEOUT_MAX

from numpy import NaN
from baseviews import BaseView
from tornado import web
from urllib.error import HTTPError
import requests
from requests.auth import HTTPBasicAuth
import sys
import json
import base64
from tornado_http_auth import auth_required
from pvlib.location import Location
import pandas as pd
from ConfigParam import ConfigParam

#Verificare come rendere parametrici in un file
PROT = "https"
HOST = "training.rebecca.mipu.eu"
API_POST = "api/targeting/multiai/v1/predictive_model/predict/"
#Credenziali Rebecca
USER = 'api_user'   # !!!!!!!!!!!!!!!!!!!!!! da cryptare
PWD = 'platoon#2022'  # !!!!!!!!!!!!!!!!!!!!!! da cryptare


logger=getLogger('middlelayer')
#Credenziali Middleware
credentials = {
    'user1': 'pass1',
    'user-inergy': 'pass1',
}

class TRPredictView(BaseView):

    class SendChallenge(Exception):
        pass

    def send_auth_challenge(self, realm):
        hdr = 'Basic realm="%s"' % realm.replace('\\', '\\\\').replace('"', '\\"')
        self.set_status(401)
        self.set_header('www-authenticate', hdr)
        self.finish()
        return False

    def get_authenticated_user(self, check_credentials_func, realm):
        try:
            return self.authenticate_user(check_credentials_func, realm)
        except self.SendChallenge:
            self.send_auth_challenge(realm)

            
    def authenticate_user(self, check_credentials_func, realm):
        #print('Authorization')
        auth_header = self.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            raise self.SendChallenge()

        auth_data = auth_header.split(None, 1)[-1]
        auth_data = base64.b64decode(auth_data).decode('ascii')
        username, password = auth_data.split(':', 1)
        #print('Authorization: ' + username + ':'+password)
        challenge = check_credentials_func(username)
        if not challenge:
            raise self.SendChallenge()

        if challenge == password:
            self._current_user = username
            return True
        else:
            raise self.SendChallenge()
        return False


    def get_current_user(self):
        logger.debug('Logged user:' + self.current_user)
        return self.get_secure_cookie("user")

    def postPredictRequest(self, jsonreq):

        logger.debug('Post Predict: ')
        try:
            jsonresp=""
            conf = ConfigParam()
            api_url = conf.getProtocol() +'://' + conf.getHost() + '/' + conf.getApiPredict()  #PROT + '://'+HOST+'/'+API_POST
            logger.debug('URL: ' + api_url)
            print('URL: ' + api_url)
            #Eventuale parametro
            logger.debug('Json to pass: ' + json.dumps(jsonreq))
            headers =  {"Content-Type":"application/json"}
            #how to pass json ?
            user,pwd = conf.getUserApiRebecca()
            response = requests.post(api_url, auth=HTTPBasicAuth(user, pwd), headers=headers, data = json.dumps(jsonreq))
            #response.raise_for_status()
            logger.debug(response.json())
            logger.info(response.status_code)
            #print(response.headers)
            jsonresp = response.json()
            return jsonresp

        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err}')
            return jsonresp
        except Exception as err:
            logger.error(f'Other error occurred: {err}')
            return jsonresp

    @auth_required(realm='Protected', auth_func=credentials.get)
    def _get(self, *args, **kwargs):
        logger.debug('Hello %s' % self._current_user)
        try:
            print('Get Method: not supported')
            self.write(json.dumps("Get Method: not Supported"))
            return True
        except web.HTTPError as why:
            msg = '{}'.format(why)
            self.logger.warning(msg)
            self.set_status(why.status_code, msg)
            return False
        except Exception as why:
            exctype, excmsg, exctb = sys.exc_info()
            excmsg = '{} in {} view: {}'.format(
                exctype.__name__,
                self.__class__.__name__,
                why,
                )
            logger.error(excmsg)
            self.send_error()
            return False

    @auth_required(realm='Protected', auth_func=credentials.get)    
    def _post(self, *args, **kwargs):
        logger.info('Hello %s' % self._current_user)
        print('Hello %s, Start Predict' % self._current_user)
        try:
            logger.info(" TR Predict Method called")
            dictrec = json.loads(self.request.body)
 
            timesrec = dictrec.get("times")

            lent = len(timesrec)
            #riempire struttura json con dati recuperati
            ##
            f = open ('./TRPredictRequestA.json', "r")
            #Costruzione json da inviare a API Rebecca per la predict
            #oppure è il cihamante che ci passa questa struttura
            jsonreq = json.load(f)
            print(jsonreq.keys())
            #dict_keys(['predictive_model_id', 'data', 'times', 'orient'])
            data = jsonreq.get("data")
            #dict_keys(['temperature', 'solar_radiation_0', 'solar_radiation_30', 'pressure', 'precipitation', 'cloud_cover', 'ghi', 'dhi', 'dni', 'wind_speed', 'wind_direction', 'H', 'L', '
            data_rec = dictrec.get("data", NaN)
            l = len(data_rec)
            #model = jsonreq.get("predictive_model_id")
            #times = jsonreq.get("times")
            jsonreq["times"] = timesrec
            i=0
            for d in data_rec:
                #print(d.get("temperature", 0))    
                dr = {}
                #dr = data[i]
                #dr['Temperature_A'] = d["Temperature_A"]
                dr['Temperature_B'] = d["Temperature_B"]
                dr['Temperature_C'] = d["Temperature_C"]
                dr['Temperature_D'] = d["Temperature_D"]
                dr['hour'] = d["hour"]

                if (i > 0):
                    data.append(dr) 
                else:
                    data[i] = dr
                i+=1
            jsonreq["data"] = data
            print("json di risposta: " + json.dumps(jsonreq))
            logger.debug("Json da inviare:" + json.dumps(jsonreq))
            #else:

            resp = self.postPredictRequest(jsonreq)
            #prima risposta (modello predizione tempA)
            self.write(json.dumps(resp))

            #Modello Predizione Temp B
            f = open ('./TRPredictRequestB.json', "r")
            #Costruzione json da inviare a API Rebecca per la predict
            #oppure è il cihamante che ci passa questa struttura
            jsonreq = json.load(f)
            print(jsonreq.keys())
            #dict_keys(['predictive_model_id', 'data', 'times', 'orient'])
            data = jsonreq.get("data")
            #dict_keys(['temperature', 'solar_radiation_0', 'solar_radiation_30', 'pressure', 'precipitation', 'cloud_cover', 'ghi', 'dhi', 'dni', 'wind_speed', 'wind_direction', 'H', 'L', '
            data_rec = dictrec.get("data", NaN)
            l = len(data_rec)
            #model = jsonreq.get("predictive_model_id")
            #times = jsonreq.get("times")
            jsonreq["times"] = timesrec
            i=0
            for d in data_rec:
                #print(d.get("temperature", 0))    
                dr = {}
                #dr = data[i]
                dr['Temperature_A'] = d["Temperature_A"]
                #dr['Temperature_B'] = d["Temperature_B"]
                dr['Temperature_C'] = d["Temperature_C"]
                dr['Temperature_D'] = d["Temperature_D"]
                dr['hour'] = d["hour"]

                if (i > 0):
                    data.append(dr) 
                else:
                    data[i] = dr
                i+=1
            jsonreq["data"] = data
            print("json di risposta: " + json.dumps(jsonreq))
            logger.debug("Json da inviare:" + json.dumps(jsonreq))
            #else:

            resp = self.postPredictRequest(jsonreq)
            #seconda risposta (modello predizione tempB)
            self.write(json.dumps(resp))

            #preparare DataFrame completo con le 2 predizioni 

            

        except web.HTTPError as why:
            msg = '{}'.format(why)
            self.logger.warning(msg)
            self.set_status(why.status_code, msg)
            print(msg)
            return False
        except Exception as why:
            exctype, excmsg, exctb = sys.exc_info()
            excmsg = '{} in {} view: {}'.format(
                exctype.__name__,
                self.__class__.__name__,
                why,
                )
            logger.error(excmsg)
            self.send_error()
            return False
    
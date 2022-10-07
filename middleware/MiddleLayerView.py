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
USER = 'api_user'   # !!!!!!!!!!!!!!!!!!!!!! da cryptare
PWD = 'platoon#2022'  # !!!!!!!!!!!!!!!!!!!!!! da cryptare


logger=getLogger('middlelayer')
#funziona se le crediznali sono giuste, altrimenti dà errore
credentials = {
    'polimiuser':'platoon_polimi',
    'user1': 'pass1',
}

class MiddleLayerView(BaseView):

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

    # Attenzione, i valori di start_time e end_time devono esser ein ordine 
    def get_clearsky_from_coordinates(self, lat : float, lon: float, location_name : str, timezone: str, altitude: float, turbidity : int, start_time, end_time):
            
        start_time_ts = pd.to_datetime(start_time)
        end_time_ts = pd.to_datetime(end_time)
       

        geographical_location = Location(lat, lon, timezone, altitude, location_name) 
        
        time_range = pd.date_range(start = start_time_ts, end = end_time_ts, freq = '1H', tz = geographical_location.tz)

        clearsky = geographical_location.get_clearsky(time_range, model = 'ineichen', linke_turbidity = turbidity)
        
        clearsky['Time'] = clearsky.index
        
        clearsky['year'] = clearsky['Time'].dt.year
        clearsky['month'] = clearsky['Time'].dt.month
        clearsky['day'] = clearsky['Time'].dt.dayofyear
        clearsky['hour'] = clearsky['Time'].dt.hour

        return clearsky
    
    def cloud_type_to_dummies_one_row(self, df):
        if isinstance(df, pd.DataFrame):
            if 'cloud_type' not in df.columns:
                raise KeyError("'cloud_type' not present in the DataFrame: insert 'cloud_type' column or rename an existing column accordingly")
            else:
                cloud_type_present = df['cloud_type'][0]
                cloud_type_general = {'H', 'M', 'L'}
                cloud_type_missing = cloud_type_general - set(cloud_type_present)    
                df_dummies = pd.DataFrame(columns = ['H', 'M', 'L'])
                df_with_dummies = pd.concat([df, df_dummies], axis = 1)
                df_with_dummies[cloud_type_present] = 1
                for col in cloud_type_missing:
                    df_with_dummies[col] = 0
                return df_with_dummies
        
        elif isinstance(df, pd.Series):
            if 'cloud_type' not in df.index:
                raise KeyError("'cloud_type' not present in the DataFrame: insert 'cloud_type' column or rename an existing column accordingly")
            else:
                cloud_type_present = df['cloud_type']
                cloud_type_general = {'H', 'M', 'L'}
                cloud_type_missing = cloud_type_general - set(cloud_type_present)
                df_with_dummies = df.append(pd.Series(index = cloud_type_general))
                df_with_dummies[cloud_type_present] = 1
                for col in cloud_type_missing:
                    df_with_dummies[col] = 0
                return df_with_dummies
            

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
            logger.info("Predict Method called")
            body = self.request.body
            dictrec = json.loads(self.request.body)
            geo_coord = dictrec.get("geo_coordinates", NaN)
            lat = geo_coord.get("latitude",0)
            lon = geo_coord.get("longitude", 0)
            altitude = geo_coord.get("altitude", 0)
            loc = geo_coord.get("location", 0)
            tz = geo_coord.get("timezone", 0)
            turb = geo_coord.get("turbidity", 0)
            timesrec = dictrec.get("times")
            #cs è un DataFrame contenente per ogni timestamps i dati necessari (ghi, dni, dhi)
            lent = len(timesrec)
            cs = self.get_clearsky_from_coordinates(lat, lon, loc, tz, altitude,  turb, timesrec[0],timesrec[lent-1]  )
            #manca recuperare L,H.M dato il cloudcover
            #riempire struttura json con dati recuperati
            f = open ('./TestPredictRequest.json', "r")
            #Costruzione json da inviare a API Rebecca per la predict
            #oppure è il cihamante che ci passa questa struttura
            jsonreq = json.load(f)
            print(jsonreq.keys())
            #dict_keys(['predictive_model_id', 'data', 'times', 'orient'])
            data = jsonreq.get("data")
            #dict_keys(['temperature', 'solar_radiation_0', 'solar_radiation_30', 'pressure', 'precipitation', 'cloud_cover', 'ghi', 'dhi', 'dni', 'wind_speed', 'wind_direction', 'H', 'L', '
            data_rec = dictrec.get("data", NaN)
            l = len(data_rec)
            model = jsonreq.get("predictive_model_id")
            times = jsonreq.get("times")
            jsonreq["times"] = timesrec
            i=0
            for d in data_rec:
                #print(d.get("temperature", 0))    
                dr = {}
                #dr = data[i]
                dr['temperature'] = d["temperature"]
                dr['pressure'] = d["pressure"]
                dr['solar_radiation_0'] = d["solar_radiation_0"]
                dr['solar_radiation_30'] = d["solar_radiation_30"]
                dr['precipitation'] = d["precipitation"]
                dr['wind_speed'] = d["wind_speed"]
                dr['wind_direction'] = d["wind_direction"]

                #print(cs['ghi'].loc[timesrec[i]])
                dr["ghi"] = cs['ghi'].loc[timesrec[i]]
                dr["dhi"] = cs['dhi'].loc[timesrec[i]]
                dr["dni"] = cs['dni'].loc[timesrec[i]]
                ct= d["cloud_type"]
                dc = [[ct]]
                # Create the pandas DataFrame
                df = pd.DataFrame(dc, columns = ['cloud_type'])
                df = self.cloud_type_to_dummies_one_row(df)
                h =df.iloc[0]['H']
                dr["H"] = 0
                dr["H"] =  int(h) #d["H"] #TBD with function from cloud_type
                dr["L"] = int(df.iloc[0]['L']) #d["L"]#TBD
                dr["M"] = int(df.iloc[0]['M']) #d["M"]#TBD
                dr['cloud_cover'] = d["cloud_cover"]
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
            
            self.write(json.dumps(resp))
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
    
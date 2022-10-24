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
from modello.funzioni2 import train_predict
from modello.funzioni2 import dizionario_modelli
from modello.funzioni2 import tabella
from modello.seconda_funzione import codice #metodo per train
import pandas_bokeh
from bokeh.plotting import figure
import time
from PIL import Image, ImageDraw
import io

logger=getLogger('middlelayer')
#Middleware credentials for Basic Auth
credentials = {
    'user1': 'pass1',
    'user-inergy': 'pass1',
}

class DataObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    def toJSONFile(self, nomefile):
        with open(nomefile, 'w', encoding='utf-8') as f:
            json.dump(self, f, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class TRTrainView(BaseView):

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
            print('Auth')
            return self.authenticate_user(check_credentials_func, realm)
        except self.SendChallenge:
            self.send_auth_challenge(realm)

            
    def authenticate_user(self, check_credentials_func, realm):
        print('Authorization')
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

    @auth_required(realm='Protected', auth_func=credentials.get)
    def _get(self, *args, **kwargs):
        logger.debug('Hello %s' % self._current_user)
        try:
            print('Get Method: not supported')
            filename = "./Web/image.png"
#open image
            f = Image.open(filename)
            #generate Image
            image = Image.new("RGB", (300, 50))
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), "create_images ")
            o = io.BytesIO()
            image.save(o, 'JPEG')

            #store image in reply
            o.seek(0)
            f.save(o, format="JPEG")
            s = o.getvalue()
            self.set_header('Content-type', 'image/jpg')
            self.set_header('Content-length', len(s))
            self.write(s)


            #self.flush()
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

#APi Post per train, tramite modello interno
    @auth_required(realm='Protected', auth_func=credentials.get)    
    def _post(self, *args, **kwargs):
        logger.info('Hello %s' % self._current_user)
        print('Hello %s, Start Predict' % self._current_user)
        try:
            logger.info(" TR Predict Method called")
            dictrec = json.loads(self.request.body)
            timesrec = dictrec.get("times")

            lent = len(dictrec)
            #dictrec: dizionaroi json in input
            data_rec = dictrec.get("data", NaN)
            l = len(data_rec)
            #create  DataFrame starting from dictionary reda from input json

            df = pd.DataFrame(data=None, columns=['Temperature_A', 'Temperature_B', 'Temperature_C','Temperature_D','hour', 'time' ])
            dla = []
            dlb = []
            dlc = []
            dld = []
            dlh = []
            dlt = []
            for d in data_rec:
                #dr = data[i]
                dla.append(d["Temperature_A"])
                dlb.append(d["Temperature_B"])
                dlc.append(d["Temperature_C"])
                dld.append(d["Temperature_D"])
                dlh.append(d["hour"])
                dlt.append(d["time"]) 
            dct = {}
            dct['Temperature_A'] = dla
            dct['Temperature_B'] = dlb
            dct['Temperature_C'] = dlc
            dct['Temperature_D'] = dld
            dct['hour'] = dlh
            dct['time'] = dlt
            
            df = pd.DataFrame(data=dct, columns=['Temperature_A', 'Temperature_B', 'Temperature_C','Temperature_D','hour', 'time' ])

            types_dict = {'Temperature_A': float,'Temperature_B': float, 'Temperature_C': float, 'Temperature_D': float, 'hour': int, 'time': str}
            for col, col_type in types_dict.items():
                df[col] = df[col].astype(col_type)
            df['time']= pd.to_datetime(df['time']).sort_values()
            df.index = df['time']
            logger.debug("Row number to process: %d" % l)
            logger.debug("Start Train + Predict")
            df = df.drop(['time'], axis = 1) 
            #Train of the model, returns to user the code to identify the model in order to pass it in the predict function for async calls
            codice_modello = codice(df)
            #output = DataObject()
            outputdict = DataObject()
           
            outputdict.ModelCode=codice_modello
            #train_predict(df,perc_train = 0.334)
            logger.debug("Stop Train")
            logger.debug("End  Post call: train+Pred")
            self.write(outputdict.toJSON())
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
            print(excmsg)
            self.send_error()
            return False
    
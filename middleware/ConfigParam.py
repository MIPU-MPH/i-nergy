import json
from logging import getLogger
from logging.config import fileConfig

logger=getLogger('ConfigParam')
class ConfigParam():
    fileconfig='./Config.json'
    jsonconfig = None

    def __init__(self):
        jsonconfig = None

    def readConfig(self):
        f = open (self.fileconfig, "r")
        self.jsonconfig = json.load(f)
        #print(self.jsonconfig.values())
        return self.jsonconfig

    def getport(self):
        try:
            if (self.jsonconfig == None):
                self.jsonconfig = self.readConfig()
            port = self.jsonconfig.get("port")
            if (len(port) > 0) and (int(port) > 0):
                return port
            return 0
        except Exception as err:
            print(f'Other error occurred: {err}')
            #logger.error(f'Other error occurred: {err}')
            return 0

    def getHost(self):  
        try:
            if (self.jsonconfig == None):
                self.jsonconfig = self.readConfig()
            return  self.jsonconfig.get("HOST")
        except Exception as err:
            print(f'Other error occurred: {err}')
            #logger.error(f'Other error occurred: {err}')
            return ""

    def getProtocol(self):  
        try:
            if (self.jsonconfig == None):
                self.jsonconfig = self.readConfig()
            return  self.jsonconfig.get("PROT")
        except Exception as err:
            print(f'Other error occurred: {err}')
            #logger.error(f'Other error occurred: {err}')
            return ""

    def getApiPredict(self):  
        try:
            if (self.jsonconfig == None):
                self.jsonconfig = self.readConfig()
            return  self.jsonconfig.get("API_PREDICT")
        except Exception as err:
            print(f'Other error occurred: {err}')
            #logger.error(f'Other error occurred: {err}')
            return ""

    def getUserApiRebecca(self):  
        try:
            if (self.jsonconfig == None):
                self.jsonconfig = self.readConfig()
            return  self.jsonconfig.get("USER_REBECCA"), self.jsonconfig.get("PWD_REBECCA")
        except Exception as err:
            print(f'Other error occurred: {err}')
            #logger.error(f'Other error occurred: {err}')
            return "",""




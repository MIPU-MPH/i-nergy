 #https://www.tornadoweb.org/en/stable/

#from sklearn.manifold import trustworthiness
from tornado.ioloop import IOLoop
#import tornado.web
from tornado.web import Application, RequestHandler
from logging import getLogger
import json
from ConfigParam import ConfigParam
from MiddleLayerView import MiddleLayerView
from TrainView import TrainView
from TRPredictView import TRPredictView
import logging
from logging import getLogger
import datetime
import os
import json
#import tornado.ioloop
#import tornado.web
import tornado
import tornado.httpclient
#import traceback
#import urllib2
import base64
import functools
import hashlib,base64,random
from tornado_http_auth import DigestAuthMixin, BasicAuthMixin, auth_required

items = []
logger=getLogger('middlelayer')
PORT='8889'


def make_app():
    urls = [
        #("/api/predict/([^/]+)", MiddleLayerView),
        ("/inergy/api/v1/TR_mtbt/predict/", TRPredictView)
       # ("/inergy/api/v1/TR_mtbt/train/", TRTrainView)
        ]
    return Application(urls, debug=True)

if __name__ == "__main__":
    #logger.addHandler(logging.FileHandler('restAPI.log'))
    logging.basicConfig(handlers=[logging.FileHandler(filename="./restapi.log", 
                                                 encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
                    #datefmt="%F %A %T", 
                    level=logging.DEBUG)
    #logging.basicConfig(filename='restAPI.log', encoding='utf-8', level=logging.DEBUG, format="%(asctime)s %(levelname)-8s %(name)-15s %(message)s")#, datefmt= '%Y-%m-%d %H:%M:%S')
    logger.info("Mipu Middleware: Start Tornado Loop")
    conf = ConfigParam()
    PORT = conf.getport()
    app = make_app()
    app.listen(PORT)
    print('Mipu Middleware: Start Tornado loop')
    IOLoop.current().start()



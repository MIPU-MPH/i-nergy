import os
import sys
import logging
import argparse
from matplotlib.pyplot import xlabel, ylabel
import requests
import datetime as dt
import pandas as pd
from sqlite3 import Date
from stat import FILE_ATTRIBUTE_COMPRESSED
import pandas as pd
import json
from urllib.error import HTTPError
import requests
from requests.auth import HTTPBasicAuth
import pandas_bokeh


VERSION = "1.0"

output_folder = "./"



def sendPredRequest(api_url, jsonreq, path):
    df = pd.DataFrame()
    try:
       
        headers =  {"Content-Type":"application/json"}
        response = requests.post(api_url, auth=HTTPBasicAuth('user1', 'pass1'), headers=headers, data = json.dumps(jsonreq))
            
        response.raise_for_status()
        print(response.json())
        print(response.status_code)
        print(response.headers)
        jsonresp = response.json()
        fileresp = path +  '/TRPredictResponse.json'
        file = open(fileresp, "w")
        json.dump(jsonresp, file)
        file.close()
 
        p = jsonresp.get("Results")
        preds = p.get("0")
        df = pd.DataFrame(preds.items(), columns=['Temperature_B', 'Temperature_D', 'Temperature_A', 'Temperature_C',
       'hour', 'Temperature_B_pred', 'Temperature_D_pred',
       'Temperature_A_pred', 'Temperature_C_pred',
    #    'Temperature_B_residual',
    #    'Temperature_D_residual', 'Temperature_A_residual',
    #    'Temperature_C_residual', 'Temperature_B Alert semplice',
    #    'Temperature_D Alert semplice', 'Temperature_A Alert semplice',
    #    'Temperature_C Alert semplice', 'Temperature_B Alert strutturale',
    #    'Temperature_D Alert strutturale', 'Temperature_A Alert strutturale','Temperature_C Alert strutturale', 'ALERT INTENSITY',
        'time']) # ho aggiunto tutte le colonne presenti
        df.index = df["time"] # ho messo come indice la colonna time, che però è ancora presente come colonna
        #df.set_index('time',inplace = True) # se la si vuole solo come indice bisogna far girare questa riga al posto della precedente
        print(df)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="TR Predictions", description='A program to predict Transformer data based on.....')
    parser.add_argument("--version", action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--out-format', '-f', type=str, help='The format of downloaded data (same as output file extension).', required=True, metavar='EXTENSION')
    parser.add_argument('--out-folder', '-p', type=str, help='The folder where store all the downloaded data into files.', default="./", required=False, metavar='PATH')

    #args = parser.parse_args()

    datetag = dt.datetime.now().strftime("%Y%m%d%H%M%S")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    if not os.path.exists(os.path.join(os.path.dirname(sys.executable), "logs")):
        os.makedirs(os.path.join(os.path.dirname(sys.executable), "logs"))
    ch = logging.FileHandler(os.path.join(os.path.dirname(sys.executable), "logs", f"{datetag}.log"))
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    session = requests.session()
    try:


        api_url = "https://training.rebecca.mipu.eu:8889/inergy/api/v1/TR_mtbt/predict/"
        #api_url = "http://localhost:8889/platoon/api/v1/PV_power/predict/"
        f = open ('./json_I-Nergy.json', "r")
            #Costruzione json da inviare a API Rebecca per la predict
            #oppure è il cihamante che ci passa questa struttura
        jsonreq = json.load(f)
        df = sendPredRequest(api_url, jsonreq, output_folder)
       
        pandas_bokeh.output_file("./ts_TRPrediction.html")
        title = "Transformer Predictions: " + df['time'].min() + " - "+  df['time'].max()

        """ l'intenzione è quella di generare 4 grafici, ognuno sarebbe il pred vs real di una specifica Temperatura"""
        lista = [0,1,2,3]
        for i,word in enumerate(['_A','_B','_C','_D']):
            lista[i]  = []
            for col in df.columns:
                if word in col:
                    lista[i].append(col)
        for cols in lista:
            df[cols].plot_bokeh(kind='line',
                title = title, 
                xlabel ="Data",
                ylabel="Transformer temperature",
                figsize =(1700,600),
                fontsize_title=20,
                fontsize_label =15,
                colormap = ['blue', 'red', 'purple'],
                rangetool=True) 

        #cancellazione files
        #os.remove(output_path)
        sys.exit(0)
    except Exception as err:
        logger.critical(err)
        sys.exit(1)
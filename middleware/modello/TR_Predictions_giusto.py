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
from bokeh.plotting import figure, output_file, show
from bokeh.models import Title

VERSION = "1.0"

output_folder = "./"



def mipu_colors(N):
    all_colors=['#16679C','#00B398','#C9609F','#FF7F50','#219AE9','#BDD48D','#EE6F90','#FFBD69']
    color=all_colors[N]
    return(color)
all_colors=['#16679C','#00B398','#C9609F','#FF7F50','#219AE9','#BDD48D','#EE6F90','#FFBD69']



def sendPredRequest(api_url, jsonreq, path):
    df_0 = pd.DataFrame(jsonreq['data'])
    df = pd.DataFrame()
    try:
       
        headers =  {"Content-Type":"application/json"}
        response = requests.post(api_url, auth=HTTPBasicAuth('user1', 'pass1'), headers=headers, data = json.dumps(jsonreq))
            
        response.raise_for_status()
        # print(response.json())
        # print(response.status_code)
        # print(response.headers)
        jsonresp = response.json()
        fileresp = path +  '/TRPredictResponse.json'
        file = open(fileresp, "w")
        json.dump(jsonresp, file)
        file.close()
 
        p = jsonresp["Results"]
        
        df = pd.DataFrame(p)
        #df.index = df["time"] # ho messo come indice la colonna time, che però è ancora presente come colonna
        #df.set_index('time',inplace = True) # se la si vuole solo come indice bisogna far girare questa riga al posto della precedente
        # print(df)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    return (df_0, df)


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
        #df = sendPredRequest(api_url, jsonreq, output_folder)
       
        output_file("./ts_TRPrediction.html")
        # title = "Transformer Predictions: " + df['time'].min() + " - "+  df['time'].max()

        """ l'intenzione è quella di generare 4 grafici, ognuno sarebbe il pred vs real di una specifica Temperatura"""
        columns = []
        for col in df_0[df_0.columns[:-2]]:
            columns.append(col)

              
        fig = figure(title= f'Temperature Real',width=1700, height=600)
        fig.title.text_font_size = "25px"
        fig.add_layout(Title(text="Date", align="center"), "below")
        fig.add_layout(Title(text="Transformer temperature", align="center"), "left")
        
        x = range(0,len(df))
        
        for i,col in enumerate(columns):
            y = df[col]
            y_alarm = df[col] * df[f'{col} Alert strutturale']
            y_alarm = y_alarm.values
            y_alarm = [ np.nan if n == 0 else n for n in y_alarm]
            fig.line(x, y, line_color= all_colors[i], line_width = 2, legend_label = col)
            fig.triangle(x, y_alarm, fill_color = 'red', line_color= all_colors[i], size = 6)
        show(fig)
        #cancellazione files
        #os.remove(output_path)
        sys.exit(0)
    except Exception as err:
        logger.critical(err)
        sys.exit(1)
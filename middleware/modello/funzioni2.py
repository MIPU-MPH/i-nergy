#Data analysis
import pdb
import pandas as pd
import os
import matplotlib.pyplot as plt    
import pickle 
import numpy as np
from datetime import datetime, date, timedelta

#Modeling
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score,mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedShuffleSplit, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline


#General
from os import walk
from joblib import dump, load

def split_set(df, perc_train):

    dict_set = {}

    for T in df.columns[:-1]:
        
        dict_set[T] = {}

        XX = df.drop(columns = T)
        X_train = XX.iloc[:round(len(XX)*perc_train), :]
        y_train = df.iloc[:round(len(df)*perc_train), :][T]

        X_validation = XX.iloc[round(len(XX)*perc_train):]
        y_validation = df.iloc[round(len(XX)*perc_train):][T]


        X_test = XX.copy()
        y_test = df[T]

        dict_set[T]['X_train'] = X_train
        dict_set[T]['y_train'] = y_train
        dict_set[T]['X_validation'] = X_validation
        dict_set[T]['y_validation'] = y_validation
        dict_set[T]['X_test'] = X_test
        dict_set[T]['y_test'] = y_test

    return(dict_set)
        
        

def model(X_train, y_train):
    estimator = XGBRegressor()
        
    parameters = {
                    'max_depth': range(8,12,1),
                    'n_estimators': range(180,240,20),
                    'learning_rate':[0.1,0.01,0.05]
                    
                    }

    grid_search = GridSearchCV(
                                estimator = estimator,
                                param_grid = parameters,
                                #n_job = None,
                                cv = 3,
                                verbose = True
                                
                                )

    modello = grid_search.fit(X_train,y_train)
    return(modello)

def dizionario_modelli(df,perc_train = 0.334):

    split_set(df, perc_train)
    dict_modelli = {}

    for T in split_set(df,perc_train):

        X_train = split_set(df,perc_train)[T]['X_train']
        y_train = split_set(df,perc_train)[T]['y_train']
        X_validation = split_set(df,perc_train)[T]['X_validation']
        y_validation = split_set(df,perc_train)[T]['y_validation']
        

        modello = model(X_train, y_train)

        pred_validation = modello.predict(X_validation)
        residui_validation = y_validation - pred_validation
        sigma_residui_validation = residui_validation.std()
        media_residui_validation = residui_validation.mean()

        LCL = media_residui_validation - 6*sigma_residui_validation
        UCL = media_residui_validation + 6*sigma_residui_validation

        dict_modelli[T] = {}
        dict_modelli[T]['model'] = modello
        dict_modelli[T]['sigma'] = sigma_residui_validation
        dict_modelli[T]['LCL'] = LCL
        dict_modelli[T]['UCL'] = UCL
        
    return(dict_modelli)

    
def tabella(dict_modelli,df):

    Tab = df.copy()

    for T in df.columns[:-1]:

        X = df.drop(columns = T)
        new_col = dict_modelli[T]['model'].predict(X)
        Tab[f'{T}_pred'] = new_col
    
    for T in df.columns[:-1]:

        Tab[f'{T}_residual'] = Tab[T] - Tab[f'{T}_pred']

    for T in df.columns[:-1]:
        LCL = dict_modelli[T]['LCL'] 
        UCL = dict_modelli[T]['UCL'] 
        Tab[f'{T} Alert semplice'] = [ 1 if (t > UCL or t < LCL) else 0 for t in Tab[f'{T}_residual'] ]

    for T in df.columns[:-1]:
        sigma = dict_modelli[T]['sigma']
        Rolling_mean = df[T].rolling(6).mean()
        Tab[f'{T} Alert strutturale'] = [ 1 if roll > sigma else 0 for roll in Rolling_mean]
    
    Tab['ALERT INTENSITY'] = Tab[Tab.columns[-4:]].sum(axis = 1)
    return (Tab)


    
def train_predict(df, perc_train):
    dict_modelli = dizionario_modelli(df,perc_train)
    tabella(dict_modelli,df)
    return(tabella)




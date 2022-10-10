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
        
        

def bestmodel(X_train, y_train,X_test, y_test,gridsearch=True):
    """Finds the best pipeline for the data provided within regressors, using gridsearch or randomizedsearch""" 
    # Initialize the estimators
    reg1=ExtraTreesRegressor(random_state=42)
    reg2 = RandomForestRegressor(random_state=42)
    reg3=XGBRegressor(random_state=42,gamma=0,scale_pos_weight=1,validation_fraction=0.1)
    reg4= MLPRegressor(validation_fraction=0.1, n_iter_no_change=10, max_iter=200, tol=0.001)
    
    #Algorithm settings
    settings1={'regressor__n_estimators':[50,100,150,200],'regressor__max_depth':[8,9,10,11,12], 'regressor__min_samples_split':[3, 5, 7],'regressor':[reg1]}
    settings2 = {'regressor__n_estimators':[40,50,70,80,100], 'regressor__max_depth':[8,9,10,11,12], 'regressor__min_samples_split':[3, 5, 7],'regressor':[reg2]}
    settings3 = {'regressor__max_depth':[8,9,10,11,12], 'regressor__min_child_weight':[2,3,5],'regressor__n_estimators':[50,100,150],\
        'regressor__learning_rate':[0.5,0.2,0.1,0.05],'regressor':[reg3]}
    settings4 = {'regressor__activation':['relu','sigmoid'], 'regressor__solver':['lbfgs','adam'], 'regressor__alpha':[1.e-3,1,100],\
                'regressor__hidden_layer_sizes':[(30,),(40,),(50,),(60,),(70,),(80,),(90,),(100,),(110,),(120,),(50,50),(60,60),(70,70)], 'regressor__warm_start':[True],'regressor':[reg4]}

    #Final pipeline
    params = [settings1, settings2, settings3,settings4]
    pipe = Pipeline([\
        ('scl', StandardScaler()),\
        ('regressor', reg1)])

    #Model search
    if gridsearch==True:
        #With gridsearch:
        gs=GridSearchCV(pipe, params, cv=3, n_jobs=-1, scoring='neg_mean_absolute_percentage_error',verbose=-1).fit(X_train, y_train)
    else:
        #With Random search:
        gs=RandomizedSearchCV(pipe, params, cv=3, n_jobs=-1, scoring='neg_mean_absolute_percentage_error',verbose=-1).fit(X_train, y_train)
    
    
    my_params = gs.best_params_
    print('Best algorithm:\n', gs.best_params_['regressor'])
    print('Best params:\n', gs.best_params_)
    alg=gs.best_estimator_
    print('GridSearchCV accuracy:\n', gs.score(X_test, y_test))
    print('MSE: {}'.format(np.round(gs.score(X_test, y_test),2)))
    print('MAPE: {}'.format(np.round(mean_absolute_percentage_error(y_test,alg.predict(X_test)),2)))
    print('R2: {}'.format(np.round(r2_score(y_test,alg.predict(X_test)),2)))
    sigma=np.std(y_test-alg.predict(X_test))
    print('Sigma: {}'.format(sigma))
    return(alg,gs.score(X_test, y_test))

def dizionario_modelli(df,perc_train):

    split_set(df, perc_train)
    dict_modelli = {}

    for T in split_set(df,perc_train):

        X_train = split_set(df,perc_train)[T]['X_train']
        y_train = split_set(df,perc_train)[T]['y_train']
        X_validation = split_set(df,perc_train)[T]['X_validation']
        y_validation = split_set(df,perc_train)[T]['y_validation']
        

        model = bestmodel(X_train, y_train, X_validation, y_validation)[0]

        pred_validation = model.predict(X_validation)
        residui_validation = y_validation - pred_validation
        sigma_residui_validation = residui_validation.std()
        media_residui_validation = residui_validation.mean()

        LCL = media_residui_validation - 6*sigma_residui_validation
        UCL = media_residui_validation + 6*sigma_residui_validation

        dict_modelli[T] = {}
        dict_modelli[T]['model'] = model
        dict_modelli[T]['sigma'] = sigma_residui_validation
        dict_modelli[T]['LCL'] = LCL
        dict_modelli[T]['UCL'] = UCL
    return(dict_modelli)   

    
def tabella(dict_modelli,df):

    Tab = df.copy()

    for T in df.columns[:-1]:

        X = df.drop(columns = T)
        Tab[f'{T}_pred'] = dict_modelli[T]['model'].predict(X)
    
    for T in df.columns[:-1]:

        Tab[f'{T}_residual'] = Tab[T] - Tab[f'{T}_pred']

    for T in df.columns[:-1]:
        LCL = dict_modelli[T]['LCL'] 
        UCL = dict_modelli[T]['UCL'] 
        Tab[f'{T} Alert semplice'] = [ 1 if (t > UCL or t < LCL) else 0 for t in df[T] ]

    for T in df.columns[:-1]:
        sigma = dict_modelli[T]['sigma']
        Rolling_mean = df[T].rolling(6).mean()
        Tab[f'{T} Alert strutturale'] = [ 1 if roll > sigma else 0 for roll in Rolling_mean]
    
    Tab['ALLARME'] = Tab[-4:].sum(axis = 1)
    
def train_predict(df, perc_train):
    dict_modelli = dizionario_modelli(df,perc_train)
    tabella(dict_modelli,df)
    return(tabella)




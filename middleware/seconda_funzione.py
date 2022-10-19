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

#Estrae l'info delle ORE dal TimeStamp. Quest'ultimo verrà poi impostato come indice
def preprocessing(df):
    df.time = pd.to_datetime(df.time)
    df['hour'] = [t.hour for t in df.time]
    df.set_index('time', inplace = True)
    return(df)

def split_set(df, perc_train):

    dict_set = {}

    for T in df.columns[:-1]:
        
        dict_set[T] = {}

        XX = df.drop(columns = T)
        yy = df[T]
        
        from sklearn.model_selection import train_test_split
        X_train,X_validation,y_train,y_validation=train_test_split(XX, yy, test_size = perc_train, random_state=42)

        dict_set[T]['X_train'] = X_train
        dict_set[T]['y_train'] = y_train
        dict_set[T]['X_validation'] = X_validation
        dict_set[T]['y_validation'] = y_validation

    return(dict_set)

def bestmodel(X_train, y_train,gridsearch=True):
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
    # print('GridSearchCV accuracy:\n', gs.score(X_test, y_test))
    # print('MSE: {}'.format(np.round(gs.score(X_test, y_test),2)))
    # print('MAPE: {}'.format(np.round(mean_absolute_percentage_error(y_test,alg.predict(X_test)),2)))
    # print('R2: {}'.format(np.round(r2_score(y_test,alg.predict(X_test)),2)))
    # sigma=np.std(y_test-alg.predict(X_test))
    # print('Sigma: {}'.format(sigma))
    return alg #,gs.score(X_test, y_test))


def codice(df,perc_train = 0.6):

    import calendar
    import time

    current_GMT = time.gmtime()

    time_stamp = calendar.timegm(current_GMT)
    print("Current timestamp:", time_stamp)

    split_set(df, perc_train)
    dict_modelli = {}

    for T in split_set(df,perc_train):

        X_train = split_set(df,perc_train)[T]['X_train']
        y_train = split_set(df,perc_train)[T]['y_train']
        X_validation = split_set(df,perc_train)[T]['X_validation']
        y_validation = split_set(df,perc_train)[T]['y_validation']
        

        modello = bestmodel(X_train, y_train)

        pred_validation = modello.predict(X_validation)
        residui_validation = y_validation - pred_validation

        sigma_residui_validation = residui_validation.std()
        media_residui_validation = residui_validation.mean()

        LCL = media_residui_validation - 3*sigma_residui_validation
        UCL = media_residui_validation + 3*sigma_residui_validation

        dict_modelli[T] = {}
        dict_modelli[T]['model'] = modello
        dict_modelli[T]['Residui'] = residui_validation
        dict_modelli[T]['Sigma'] = sigma_residui_validation
        dict_modelli[T]['LCL'] = LCL
        dict_modelli[T]['UCL'] = UCL

        codice = f'MIPU_transformer_model_{time_stamp}'
        
        with open(codice,'wb') as tf :
                pickle.dump(dict_modelli,tf)

    return(codice)

def tabella_output(df2, codice):

    with open(f'{codice}','rb') as tf:
        dict_modello = pickle.load(tf)

    TAB = df2.copy()

    for T in dict_modello:

        X_test = df2.drop(columns = T)
        y_test = df2[T]
        pred_test = dict_modello[T]['model'].predict(X_test)
        TAB[f'{T}_pred'] = pred_test

    for T in dict_modello:
        
        residui = y_test - pred_test
        LCL = dict_modello[T]['LCL']
        UCL = dict_modello[T]['UCL']

        TAB[f'{T} Alert semplice'] = [ 1 if (res > UCL) or (res < LCL) else 0 for res in residui ]

    for T in dict_modello:
        
        residui = y_test - pred_test
        rolling_mean = residui.rolling(6).mean()
        sigma_residui_validation = dict_modello[T]['Sigma']
        TAB[f'{T} Alert strutturale'] = [ 1 if roll > 6*sigma_residui_validation else 0 for roll in rolling_mean ]
    
    return(TAB)


""" 
Funzione A :
    codice_personale = codice(df)

Funzione B :
    tabella_output(df2, codice_personale)

"""
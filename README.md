# I-Nergy | AI for Energy
# Maintenet solution for predictive maintenance on transformers

This repository contains a prototype which has the goal to provide a complete solution with a machine learning algorithm and expert system for the continuous monitoring of the health status of the assets within the distribution network, with focus on transformers. 
The analytical pipeline consists of a preprocessing of the data provided, the training and prediction using a machine learning model, and the post-processing of the prediction in order to identify anomalies in the behaviour.  The prediction system uses winding temperatures and a core temperature to define which observations are anomalous with respect to the general distribution of the temperatures in time.

The training dataset has been selected from a cast resin transformer for medium-voltage to low-voltage transformation, with 3 windings. The resulting dataset, in line with what defined in the algorithmic strategy, is a 4-columns dataset with 3 windings temperatures and a core temperature.

The model works using 4 temperature of the trasnformer. Using 4 different autoeconding models, it identifies out of control in the temperature distribution, and creates alarms based on the tolerance of the model, with a 5 min frequency.

This reporitory contains the code used to provide AI assets in the AIOD platform. 
The main deliverable is a set of tools built with the scope to provide an anomaly detection model for transformers. 

The solution, can be accessed through a docker solution that includes a web server where a specific proprietary function runs and creates the anomaly identification. The output is a CSV file containing the real vs. predicted values, the alarms identified, and an interactive plot inspired by the standard output or Rebecca proprietary platform.
_________________________________________________________________________________________

The user can provide 4 different temperatures and the hour at which the temperature was collected, and the software will give as a result the real vs. predicted graph for the four temperatures, and the predictions for each temperature.

The repo in structuerd as follows:

    Main: all folders

        Dataset Analysis: contains code used to do EDA on transformer 

        Synthetic Dataset Creation: contains the synthetic dataset as well as the code used to create the dataset. 

        AIOD solution for anomaly detection: contains an executable linked to MIPU's platform Rebecca, and based on the data provided provides the real vs. predicted timetrend and csv. 
        
        
# MIDDLEWARE tools

The middleware tool, is a Web Server based on python Tornado framework, that includes the AI algorithm  based on syntethic data, and the methods usefull to train and predict data by user that are able to provide transfomer temperature data.
The middleware expose some  API Rest methods in order to give to a user or a third party the possibility to train model based on own data and  get the predictions one.
API Rest Methods exposed are the following:

## TRAIN AND PREDICT
    This method docen't save the data passed and the model, train the data and give predistion values based on train set.
    http://<local host>:8889/inergy/api/v1/TR_mtbt/TrainAndPredict/
    - In the body, spcify the 4 Temperatires data in a json format:
        {"data": 
            [
                    {"Temperature_B": 77.9897290650309, 
                     "Temperature_D": 94.43668658735491, 
                     "Temperature_A": 57.62743004178479, 
                     "Temperature_C": 59.52237237448914, 
                     "hour": 0, 
                     "time": "2022-08-13 00:00:00"
                    }
            ]
        }
    - Use Basic Auth

Following are the instruuctions to recall such method in (POST) via for example Insomnia client or postman client:
URL:
https://<localhost or remote server pc>:8889/inergy/api/v1/TR_mtbt/predict/
in the body you have to include the json (json_I-nergy.json is an example)

INSTRUCTION TO BUILD THE CONTAINER WITH DOCKER in a Linux PC or server:
- Download the directory Script
- Go to directory where you stored the code
- To build the Docker container: sudo docker build -t mipu_inergymiddleware_img:latest .
- To run an interactive docker instance: sudo docker run -it -p 8889:8889 --name=Mipu_inergymiddleware_instance mipu_inergymiddleware_img
- sudo docker start Mipu_inergymiddleware_instance in order to start the container in backgroound mode

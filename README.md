# I-Nergy | AI for Energy
# Maintenet solution for predictive maintenance on transformers

This reporitory contains the code used to provide AI assets in the AIOD platform. 
The main deliverable is a set of tools built with the scope to provide an anomaly detection model for transformers. 
The model works using 4 temperature of the trasnformer. Using 4 different autoeconding models, it identifies out of control in the temperature distribution, and creates alarms based on the tolerance of the model, with a 5 min frequency. 
_________________________________________________________________________________________

The user can provide 4 different temperatures and the hour at which the temperature was collected, and the software will give as a result the real vs. predicted graph for the four temperatures, and the predictions for each temperature.

The repo in structuerd as follows:

    Main: all folders

        Dataset Analysis: contains code used to do EDA on transformer 

        Synthetic Dataset Creation: contains the synthetic dataset as well as the code used to create the dataset. 

        AIOD solution for anomaly detection: contains an executable linked to MIPU's platform Rebecca, and based on the data provided provides the real vs. predicted timetrend and csv. 
        
        
        
#MIDDLEWARE tools
The middleware tool, is a Web Server based on python Tornado framework, that includes the AI algorithm  based on syntethic data, and the method usefule to train and predict data by user that are able to provide transfomer temperature data.
The middleware expose an API Rest in order to give the user the possibility to train model based on owen data and to get the predictione data.
Following are the instruuctions to recall such method in (POST) via for example Insomnia client or ostman client:
URL:
https://<localhost or remote server pc>:8889/inergy/api/v1/TR_mtbt/predict/
in the body you have to include the json (json_I-nergy.json)

INSTRUCTION TO BUILD THE CONTAINER WITH DOCKER in a Linux PC or server:
- Download the directory Script
- Go to directory where you stored the code
- Docker build: sudo docker build -t mipu_inergymiddleware_img:latest .
- Docker run: sudo docker run -it -p 8889:8889 --name=Mipu_inergymiddleware_instance mipu_inergymiddleware_img
    in order to start the container in intercative mode
- sudo docker start Mipu_inergymiddleware_instance in order to start the container in backgroound mode

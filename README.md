# I-Nergy | AI for Energy
# Maintenet solution for predictive maintenance on transformers
> "This project has received funding from the European Union's Horizon 2020 research and innovation programme within the framework of the I-NERGY Project, funded under grant agreement No 101016508"
 
This repository contains a prototype which has the goal to provide a complete solution with a machine learning algorithm and expert system for the continuous monitoring of the health status of the assets within the distribution network, with focus on transformers. 
The analytical pipeline consists of a preprocessing of the data provided, the training and prediction using a machine learning model, and the post-processing of the prediction in order to identify anomalies in the behaviour.  The prediction system uses winding temperatures and a core temperature to define which observations are anomalous with respect to the general distribution of the temperatures in time.

The training dataset has been selected from a cast resin transformer for medium-voltage to low-voltage transformation, with 3 windings. The resulting dataset, in line with what defined in the algorithmic strategy, is a 4-columns dataset with 3 windings temperatures and a core temperature.

The model works using 4 temperature of the trasnformer. Using 4 different autoeconding models, it identifies out of control in the temperature distribution, and creates alarms based on the tolerance of the model, with a 5 min frequency.

This reporitory contains the code used to provide AI assets in the AIOD platform. 
The main deliverable is a set of tools built with the scope to provide an anomaly detection model for transformers. 

The solution, can be accessed through a docker solution that includes a web server where a specific proprietary function runs and creates the anomaly identification. The output is a CSV file containing the real vs. predicted values, the alarms identified, and an interactive plot inspired by the standard output or Rebecca proprietary platform.

_________________________________________________________________________________________

The user can provide 4 different temperatures and the hour at which the temperature was collected, and the software will give as a result the real vs. predicted graph for the four temperatures, and the predictions for each temperature.

### REPO STRUCTURE
The repo in structured as follows:

    Main: all folders

        - Dataset Analysis:
        - Synthetic Dataset Creation
        - Middleware
	
 # Dataset Analysis
 Contains code used to do EDA on transformer 
 
 # Syntethic DataSet
 Contains the synthetic dataset as well as the code used to create the dataset. 
        
# MIDDLEWARE tools

The middleware tool, is a Web Server based on python Tornado framework, that includes the AI algorithm  based on syntethic data, and the methods usefull to train and predict data by user that are able to provide transfomer temperature data.
The middleware expose some  API Rest methods in order to give to a user or a third party the possibility to train model based on own data and  get the predictions one.
The middleware or API Gateway is built in a docker and released in a docker container (below you can find instruction to build the middleware).

API Rest Methods exposed are the following:

## TRAIN AND PREDICT
    This method doesn't save the data passed and the model, train the data and give predistion values based on train set.
    POST METHOD:  http://<local host>:8889/inergy/api/v1/TR_mtbt/TrainAndPredict/
    - In the body, specify the 4 Temperatires data in a json format:
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
    - Uses Basic Auth (user1, pass1)
    return a json with predicted values:
        {
        "Results": [
            {
                "Temperature_A": 57.62743004178479,
                "Temperature_A Alert semplice": 0,
                "Temperature_A Alert strutturale": 0,
                "Temperature_A_pred": 75.73596654323161,
                "Temperature_B": 77.9897290650309,
                "Temperature_B Alert semplice": 0,
                "Temperature_B Alert strutturale": 0,
                "Temperature_B_pred": 79.56667994703176,
                "Temperature_C": 59.52237237448914,
                "Temperature_C Alert semplice": 0,
                "Temperature_C Alert strutturale": 0,
                "Temperature_C_pred": 69.31261444091797,
                "Temperature_D": 94.43668658735491,
                "Temperature_D Alert semplice": 0,
                "Temperature_D Alert strutturale": 0,
                "Temperature_D_pred": 74.38961180632032,
                "hour": 0
            }
         }
## TRAIN METHOD 
    POST METHOD: http://<local host>:8889/inergy/api/v1/TR_mtbt/train/
    Body of the call (example)
    {"data": [{"Temperature_B": 77.9897290650309, "Temperature_D": 94.43668658735491, "Temperature_A": 57.62743004178479, "Temperature_C": 59.52237237448914, "hour": 			0, "time": "2022-08-13 00:00:00"}
	]
    }
    OUTPUT: is the model's code to identify trained algorithm in next predict calls:
	{
		"ModelCode": "MIPU_transformer_model_1666617526"
	}
    
## PREDICT METHOD
    POST METHOD:  http://localhost:8889/inergy/api/v1/TR_mtbt/predict/
     - In the body, specify the 4 Temperatures data in a json format, and the code to identify the model to use in the prediction (the id returned by a previuos train  call:
      {"data": [{"Temperature_B": 77.9897290650309, "Temperature_D": 94.43668658735491, "Temperature_A": 57.62743004178479, "Temperature_C": 59.52237237448914, "hour":             0, "time": "2022-08-13 00:00:00"}, 
        "codice": "MIPU_transformer_model_1666602245"}
    
    Json output:
    {
	"Results": [
		{
			"Temperature_A": 57.62743004178479,
			"Temperature_A Alert semplice": 0,
			"Temperature_A Alert strutturale": 0,
			"Temperature_A_pred": 75.73596654323161,
			"Temperature_B": 77.9897290650309,
			"Temperature_B Alert semplice": 0,
			"Temperature_B Alert strutturale": 0,
			"Temperature_B_pred": 79.56667994703176,
			"Temperature_C": 59.52237237448914,
			"Temperature_C Alert semplice": 0,
			"Temperature_C Alert strutturale": 0,
			"Temperature_C_pred": 69.31261444091797,
			"Temperature_D": 94.43668658735491,
			"Temperature_D Alert semplice": 0,
			"Temperature_D Alert strutturale": 0,
			"Temperature_D_pred": 74.38961180632032,
			"hour": 0
		}
	]
	}
    
## INSTRUCTION TO BUILD THE CONTAINER WITH DOCKER in a Linux PC or server:
- Download the directory Script
- Go to directory where you stored the code
- To build the Docker container: sudo docker build -t mipu_inergymiddleware_img:latest .
- To run an interactive docker instance: sudo docker run -it -p 8889:8889 --name=Mipu_inergymiddleware_instance mipu_inergymiddleware_img
- sudo docker start Mipu_inergymiddleware_instance in order to start the container in backgroound mode


## LIGHT GUI
the folder Light GUI contains an exampled code the calls the API exposed by the middleware, passing data read from a csv file and displayng predicted data on a chart.
It's a python script, to call with the following command: python TR_predictions_GUI.py

## LICENSE

This project is licensed under the terms of the GNU GPLv3 license.

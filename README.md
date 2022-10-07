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
import os
import sys 
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from urllib.parse import urlparse
import mlflow
from mlflow.models.signature import infer_signature
import mlflow.sklearn
import logging

logging.basicConfig(level = logging.WARN)
logger = logging.getLogger(__name__)

def eval_metrics(actual, pred) :
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

if __name__ == "__main__" :

    ## Data Ingestion-Reading the dataset -- wine quality dataset
    csv_url=(
        "https://raw.githubusercontent.com/mlflow/mlflow/master/tests/datasets/winequality-red.csv"
    )

    try : 
        data = pd.read_csv(csv_url, sep = ";")

    except Exception as e :
        logger.exception("Unable to download the data")
    

    # Split the data in train and test

    train, test = train_test_split(data)

    train_x = train.drop(["quality"], axis = 1)
    test_x = test.drop(["quality"], axis = 1)
    train_y = train["quality"]
    test_y = test["quality"]

    alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    l1_ratio = float(sys.agrv[2]) if len(sys.argv) > 2 else 0.5

    with mlflow.start_run() :
        lr = ElasticNet(alpha = alpha, l1_ratio = l1_ratio, random_state = 42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print(f"Elasticnet Model (alpha = {alpha}, l1_ratio = {l1_ratio})")
        print(f"RMSE : {rmse}")
        print(f"MAE {mae}")
        print(f"R2 {r2}")

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        # For the remote server AWS we need to do the setup
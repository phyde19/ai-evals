<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/connect-environment -->

On this page

Last updated on **Sep 25, 2025**

# Tutorial: Connect your development environment to MLflow

This page shows you how to create an MLflow Experiment and connect your development environment to it.

An MLflow Experiment is the container for your GenAI application. Learn more about MLflow Experiments in the [Experiment data model](</aws/en/mlflow3/genai/concepts/>) concept guide.

Go the section relevant to your development environment:

  * **Locally** in an IDE or notebook
  * **Databricks-hosted Notebook**



## Local development environmentâ

### Step 1: Install MLflowâ

Install MLflow with Databricks connectivity:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1"  
    

###  Step 2: Create an MLflow Experimentâ

  1. Open your Databricks workspace.
  2. In the left sidebar, under **AI/ML** , click **Experiments**.
  3. At the top of the Experiments page, click **GenAI apps & agents**.



### Step 3: Configure authenticationâ

note

These steps describe using a Databricks Personal Access Token. MLflow also works with the other [Databricks-supported authentication methods](</aws/en/dev-tools/auth/>).

Choose one of the following authentication methods:

  * Environment Variables
  * .env File



  1. In your MLflow Experiment, click the Kebab menu icon  > **Log traces locally** > click **Generate API Key**.
  2. Copy and run the generated code in your terminal:



Bash
    
    
    export DATABRICKS_TOKEN=<databricks-personal-access-token>  
    export DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com  
    export MLFLOW_TRACKING_URI=databricks  
    export MLFLOW_REGISTRY_URI=databricks-uc  
    export MLFLOW_EXPERIMENT_ID=<experiment-id>  
    

  1. In your MLflow Experiment, click the Kebab menu icon  > **Log traces locally** > click **Generate API Key**.
  2. Copy the generated code to a `.env` file in your project root:



Bash
    
    
    DATABRICKS_TOKEN=<databricks-personal-access-token>  
    DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com  
    MLFLOW_TRACKING_URI=databricks  
    MLFLOW_REGISTRY_URI=databricks-uc  
    MLFLOW_EXPERIMENT_ID=<experiment-id>  
    

  1. Install the `python-dotenv` package:



Bash
    
    
    pip install python-dotenv  
    

  1. Load environment variables in your code:



Python
    
    
    # At the beginning of your Python script  
    from dotenv import load_dotenv  
      
    # Load environment variables from .env file  
    load_dotenv()  
    

### Step 4: Verify your connectionâ

Create a test file and run this code to verify your connection and log a test [trace](</aws/en/mlflow3/genai/tracing/>) to your MLflow Experiment:

Python
    
    
    import mlflow  
    import os  
      
    experiment_id = os.environ.get("MLFLOW_EXPERIMENT_ID")  
    databricks_host = os.environ.get("DATABRICKS_HOST")  
    mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")  
      
    if experiment_id is None or databricks_host is None or mlflow_tracking_uri is None:  
        raise Exception("Environment variables are not configured correctly.")  
      
    @mlflow.trace  
    def hello_mlflow(message: str):  
      
        hello_data = {  
            "experiment_url": f"{databricks_host}/mlflow/experiments/{experiment_id}",  
            "experiment_name": mlflow.get_experiment(experiment_id=experiment_id).name,  
            "message": message,  
        }  
        return hello_data  
      
    result = hello_mlflow("hello, world!")  
    print(result)  
    

## Develop in a Databricks-hosted Notebookâ

### Step 1: Create a notebookâ

Creating a Databricks Notebook creates an MLflow Experiment that is the container for your GenAI application. To learn more about experiments, see [data model](</aws/en/mlflow3/genai/concepts/>).

  1. Open your Databricks workspace.
  2. Go to **New** at the top of the left sidebar.
  3. Click **Notebook**.



### Step 2: Install MLflowâ

Databricks runtimes include MLflow, but for the best experience with GenAI capabilities, update to the latest version:

Python
    
    
    %pip install --upgrade "mlflow[databricks]>=3.1"  
    dbutils.library.restartPython()  
    

### Step 3: Configure authenticationâ

No additional authentication configuration is needed when working within a Databricks Notebook. The notebook automatically has access to your workspace and the associated MLflow Experiment.

### Step 4: Verify your connectionâ

Run this code in a notebook cell to verify your connection. You will see an MLflow trace appear below your notebook cell.

Python
    
    
    import mlflow  
    import os  
      
    @mlflow.trace  
    def hello_mlflow(message: str):  
        hello_data = {  
            "message": message,  
        }  
        return hello_data  
      
    result = hello_mlflow("hello, world!")  
    print(result)  
    

## Next stepsâ

  * [Instrument your app with tracing (IDE)](</aws/en/mlflow3/genai/getting-started/tracing/tracing-ide>) \- Add MLflow Tracing to your GenAI app in a local IDE
  * [Instrument your app with tracing (Notebook)](</aws/en/mlflow3/genai/getting-started/tracing/tracing-notebook>) \- Add MLflow Tracing in a Databricks Notebook



## Reference guidesâ

For details on concepts and features in this guide, see:

  * [MLflow Experiments](</aws/en/mlflow3/genai/concepts/>) \- Understand the experiment container for your GenAI application
  * [Databricks authentication](</aws/en/dev-tools/auth/>) \- Explore all available authentication methods
  * [Tracing concepts](</aws/en/mlflow3/genai/tracing/tracing-101>) \- Learn the fundamentals of MLflow Tracing
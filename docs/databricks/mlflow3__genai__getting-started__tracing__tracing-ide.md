<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/tracing/tracing-ide -->

On this page

Last updated on **Nov 26, 2025**

# Get started: MLflow Tracing for GenAI (Local IDE)

This quickstart helps you integrate your GenAI app with [MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) if you use a local development environment such as an IDE (VS Code, PyCharm, Cursor or others) or a locally-hosted notebook environment (Jupyter or others). If you use a Databricks Notebook, please use the [Databricks Notebook quickstart](</aws/en/mlflow3/genai/getting-started/tracing/tracing-notebook>) instead.

By the end of this tutorial, you will have:

  * An MLflow experiment for your GenAI app
  * Your local development environment connected to MLflow
  * A simple GenAI application instrumented with MLflow Tracing
  * A trace from that app in your MLflow experiment



## Prerequisitesâ

  * **Databricks Workspace** : Access to a Databricks workspace.



## Step 1: Install MLflowâ

When working in your local IDE, you need to install MLflow with Databricks connectivity.

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" openai  
    

## Step 2: Create a new MLflow experimentâ

An MLflow experiment is the container for your GenAI application. Learn more about experiments in the [concepts section](</aws/en/mlflow3/genai/concepts/#experiments>).

  1. Open your Databricks workspace
  2. In the left sidebar, under **AI/ML** , click **Experiments**.
  3. At the top of the Experiments page, click on **GenAI apps & agents**
  4. Get the experiment ID and path by clicking on the information icon  in the upper-left. You will use these later.



## Step 3: Connect your environment to MLflowâ

The code snippets below show how to set up authentication using a Databricks Personal Access Token. MLflow also works with the other [Databricks-supported authentication methods](</aws/en/dev-tools/auth/>).

  * Use environment variables
  * Use a .env file



  1. In your MLflow Experiment, click the Kebab menu icon  > **Log traces locally** > click **Generate API Key**.

  2. Copy and run the generated code in your terminal.

Bash
         
         export DATABRICKS_TOKEN=<databricks-personal-access-token>  
         export DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com  
         export MLFLOW_TRACKING_URI=databricks  
         export MLFLOW_REGISTRY_URI=databricks-uc  
         export MLFLOW_EXPERIMENT_ID=<experiment-id>  
         




  1. In your MLflow Experiment, click the Kebab menu icon  > **Log traces locally** > click **Generate API Key**.

  2. Copy the generated code to a `.env` file in your project root

Bash
         
         DATABRICKS_TOKEN=<databricks-personal-access-token>  
         DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com  
         MLFLOW_TRACKING_URI=databricks  
         MLFLOW_REGISTRY_URI=databricks-uc  
         MLFLOW_EXPERIMENT_ID=<experiment-id>  
         

  3. Install the `python-dotenv` package

Bash
         
         pip install python-dotenv  
         

  4. Load environment variables in your code

Python
         
         # At the beginning of your Python script  
         from dotenv import load_dotenv  
           
         # Load environment variables from .env file  
         load_dotenv()  
         




## Step 4: Create and instrument your applicationâ

Create your GenAI app with tracing enabled.

  1. Create a Python file named `app.py` in your project directory.

  2. Initialize an OpenAI client to connect to either Databricks-hosted LLMs or LLMs hosted by OpenAI.

     * Databricks-hosted LLMs
     * OpenAI-hosted LLMs

Use `databricks-openai` to get an OpenAI client that connects to Databricks-hosted LLMs. Select a model from the [available foundation models](</aws/en/machine-learning/foundation-model-apis/supported-models>).

Python
    
    import mlflow  
    from databricks_openai import DatabricksOpenAI  
      
    # Enable MLflow's autologging to instrument your application with Tracing  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/docs-demo")  
      
    # Create an OpenAI client that is connected to Databricks-hosted LLMs  
    client = DatabricksOpenAI()  
      
    # Select an LLM  
    model_name = "databricks-claude-sonnet-4"  
    

Use the native OpenAI SDK to connect to OpenAI-hosted models. Select a model from the [available OpenAI models](<https://platform.openai.com/docs/models>).

Python
    
    import mlflow  
    import os  
    import openai  
      
    # Ensure your OPENAI_API_KEY is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "<YOUR_API_KEY>" # Uncomment and set if not globally configured  
      
    # Enable auto-tracing for OpenAI  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/docs-demo")  
      
    # Create an OpenAI client connected to OpenAI SDKs  
    client = openai.OpenAI()  
      
    # Select an LLM  
    model_name = "gpt-4o-mini"  
    

  3. Define and run your application:

Use the [`@mlflow.trace` decorator](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/>), which makes it easy to trace any Python function, combined with [OpenAI automatic instrumentation](</aws/en/mlflow3/genai/tracing/integrations/openai>) to capture the details of the call to the OpenAI SDK.

Python
         
         # Use the trace decorator to capture the application's entry point  
         @mlflow.trace  
         def my_app(input: str):  
             # This call is automatically instrumented by `mlflow.openai.autolog()`  
             response = client.chat.completions.create(  
                 model=model_name,  # This example uses a Databricks hosted LLM - you can replace this with any AI Gateway or Model Serving endpoint. If you provide your own OpenAI credentials, replace with a valid OpenAI model e.g., gpt-4o, etc.  
                 messages=[  
                     {  
                         "role": "system",  
                         "content": "You are a helpful assistant.",  
                     },  
                     {  
                         "role": "user",  
                         "content": input,  
                     },  
                 ],  
             )  
             return response.choices[0].message.content  
           
         result = my_app(input="What is MLflow?")  
         print(result)  
         

  4. Run the application

Bash
         
         python app.py  
         




For details on adding tracing to apps, see the [tracing instrumentation guide](</aws/en/mlflow3/genai/tracing/app-instrumentation/>) and the [20+ library integrations](</aws/en/mlflow3/genai/tracing/integrations/>).

## Step 5: View the trace in MLflowâ

  1. Navigate back to the MLflow experiment UI.
  2. You will now see the generated trace in the **Traces** tab.
  3. Click on the trace to view its details.



### Understanding the traceâ

The trace you've just created shows:

  * **Root span** : Represents the inputs to the `my_app(...)` function
    * **Child span** : Represents the OpenAI completion request
  * **Attributes** : Contains metadata like model name, token counts, and timing information
  * **Inputs** : The messages sent to the model
  * **Outputs** : The response received from the model



This simple trace already provides valuable insights into your application's behavior, such as:

  * What was asked
  * What response was generated
  * How long the request took
  * How many tokens were used (affecting cost)



For more complex applications like RAG systems or multi-step agents, MLflow Tracing provides even more value by revealing the inner workings of each component and step.

## Guides and referencesâ

For details on concepts and features in this guide, see:

  * [MLflow Tracing guide](</aws/en/mlflow3/genai/tracing/>) \- Start here for more in-depth learning about MLflow Tracing
  * [MLflow Tracing integrations](</aws/en/mlflow3/genai/tracing/integrations/>) \- 20+ libraries with automatic tracing integrations
  * [Tracing concepts](</aws/en/mlflow3/genai/tracing/tracing-101>) \- Understand the fundamentals of MLflow Tracing
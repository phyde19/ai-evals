<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/search-traces-examples -->

On this page

Last updated on **Jan 7, 2026**

# Tutorial: Search traces programmatically

Copy notebook link for import

Copy a link to the clipboard for importing this page as a notebook

Open notebook in new tab

Open a notebook containing all code in this page in a new tab

This tutorial provides simple examples to get started with [mlflow.search_traces()](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>). For details on searching traces, see [Search traces programmatically](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-via-sdk>).

## Environment setupâ

Install required packages:

  * `mlflow[databricks]`: Use the latest version of MLflow to get more features and improvements.
  * `openai`: This app will use the OpenAI API client to call Databricks-hosted models.



Python
    
    
    %pip install -qq --upgrade "mlflow[databricks]>=3.1.0" openai  
    dbutils.library.restartPython()  
    

Create an MLflow experiment. If you are using a Databricks notebook, you can skip this step and use the default notebook experiment. Otherwise, follow the [environment setup quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>) to create the experiment and connect to the MLflow Tracking server.

## Generate traces for analysisâ

This simple app generates traces to use with `search_traces()`.

Python
    
    
      
    import mlflow  
    from databricks_openai import DatabricksOpenAI  
      
    mlflow.openai.autolog()  
      
    @mlflow.trace  
    def my_app(message: str) -> str:  
        # Create an OpenAI client that is connected to Databricks-hosted LLMs  
        client = DatabricksOpenAI()  
      
        response = client.chat.completions.create(  
            model="databricks-claude-sonnet-4",  
            messages=[  
                {  
                    "role": "system",  
                    "content": "You are a helpful assistant. Give brief, 1-2 sentence responses.",  
                },  
                {  
                    "role": "user",  
                    "content": message,  
                },  
            ]  
        )  
      
        # Add examples of custom metadata and tags  
        mlflow.update_current_trace(  
            metadata={  
                "mlflow.trace.user": 'name@my_company.com',  
            },  
            tags={  
                "environment": "production",  
            },  
        )  
      
        return response.choices[0].message.content  
    

Python
    
    
    my_app("What is MLflow and how does it help with GenAI?")  
    my_app("What is ML vs. AI?")  
    my_app("What is MLflow and how does it help with machine learning?")  
    

## Quick referenceâ

Python
    
    
    # Search by status  
    mlflow.search_traces(filter_string="attributes.status = 'OK'")  
    mlflow.search_traces(filter_string="attributes.status = 'ERROR'")  
      
    # Search by time  
    mlflow.search_traces(filter_string="attributes.timestamp_ms > 1749006880539")  
    mlflow.search_traces(filter_string="attributes.execution_time_ms > 2500")  
      
    # Search by metadata  
    mlflow.search_traces(filter_string="metadata.`mlflow.trace.user` = 'name@my_company.com'")  
      
    # Search by tags  
    mlflow.search_traces(filter_string="tags.environment = 'production'")  
    mlflow.search_traces(filter_string="tags.`mlflow.traceName` = 'my_app'")  
      
    # Combined filters (AND only)  
    mlflow.search_traces(  
        filter_string="attributes.status = 'OK' AND tags.environment = 'production'"  
    )  
      
    traces = mlflow.search_traces()  
    traces  
    

`mlflow.search_traces()` returns a pandas DataFrame or list of [`Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) objects with these fields:

Python
    
    
    list(traces.columns)  
    

Output
    
    
    ['trace_id',  
     'trace',  
     'client_request_id',  
     'state',  
     'request_time',  
     'execution_duration',  
     'request',  
     'response',  
     'trace_metadata',  
     'tags',  
     'spans',  
     'assessments']  
    

## Search examplesâ

When you run this tutorial, the code cells below will show search results.

### Search by statusâ

Searching by status lets you find successful, failed, or in-progress traces.

Python
    
    
    mlflow.search_traces(filter_string="attributes.status = 'OK'")  
    

Python
    
    
    mlflow.search_traces(filter_string="attributes.status != 'ERROR'")  
    

### Search by timestampâ

Time must be specified in milliseconds, using Unix timestamps.

Find recent traces from the last 5 minutes:

Python
    
    
    import time  
    from datetime import datetime  
      
    current_time_ms = int(time.time() * 1000)  
    five_minutes_ago = current_time_ms - (5 * 60 * 1000)  
    mlflow.search_traces(  
        filter_string=f"attributes.timestamp_ms > {five_minutes_ago}"  
    )  
    

Search over a date range:

Python
    
    
    start_date = int(datetime(2026, 1, 1).timestamp() * 1000)  
    end_date = int(datetime(2026, 1, 31).timestamp() * 1000)  
    mlflow.search_traces(  
        filter_string=f"attributes.timestamp_ms > {start_date} AND attributes.timestamp_ms < {end_date}"  
    )  
    

You can also use the 'timestamp' alias instead of 'timestamp_ms':

Python
    
    
    mlflow.search_traces(filter_string=f"attributes.timestamp > {five_minutes_ago}")  
    

### Search by execution timeâ

Find slow traces:

Python
    
    
    mlflow.search_traces(filter_string="attributes.execution_time_ms > 2500")  
    

You can also use the 'latency' alias instead of 'execution_time_ms':

Python
    
    
    mlflow.search_traces(filter_string="attributes.latency > 1000")  
    

### Search by metadataâ

Remember to use backticks for metadata names with dots.

Search custom metadata for a specific user:

Python
    
    
    mlflow.search_traces(filter_string="metadata.`mlflow.trace.user` = 'name@my_company.com'")  
    

### Search by tagsâ

Remember to use backticks for tag names with dots.

Search system tags:

Python
    
    
    mlflow.search_traces(  
        filter_string="tags.`mlflow.traceName` = 'my_app'"  
    )  
    

Search custom tags set using [`mlflow.update_current_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>):

Python
    
    
    mlflow.search_traces(filter_string="tags.environment = 'production'")  
    

### Complex filtersâ

Only AND is supported, not OR.

Find recent successful production traces:

Python
    
    
    current_time_ms = int(time.time() * 1000)  
    one_hour_ago = current_time_ms - (60 * 60 * 1000)  
      
    mlflow.search_traces(  
        filter_string=f"attributes.status = 'OK' AND "  
                      f"attributes.timestamp_ms > {one_hour_ago} AND "  
                      f"tags.environment = 'production'"  
    )  
    

Find fast traces from a specific user:

Python
    
    
    mlflow.search_traces(  
        filter_string="attributes.execution_time_ms < 2500 AND "  
                      "metadata.`mlflow.trace.user` = 'name@my_company.com'"  
    )  
    

Find traces from a specific function that exceed a performance threshold:

Python
    
    
    mlflow.search_traces(  
        filter_string="tags.`mlflow.traceName` = 'my_app' AND "  
                      "attributes.execution_time_ms > 1000"  
    )  
    

## Next stepsâ

In general, you will call [`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>) to extract a set of traces and then do further analysis or processing of the returned DataFrame or list of `Trace` objects.

For more advanced examples, see:

  * [Tutorial: Trace and analyze users and environments](</aws/en/mlflow3/genai/tracing/add-context-to-traces-tutorial>) \- Run an example of adding context metadata to traces and analyzing the results
  * [Examples: Trace analysis](</aws/en/mlflow3/genai/tracing/observe-with-traces/analyze-traces>) \- See a variety of examples of trace analysis



## Example notebookâ

#### Tutorial: Search traces programmatically

[Open notebook in new tab](<https://docs.databricks.com/aws/en/notebooks/source/mlflow3/genai/tracing/search-traces-examples.html>)

Copy link for import

Copy to clipboard
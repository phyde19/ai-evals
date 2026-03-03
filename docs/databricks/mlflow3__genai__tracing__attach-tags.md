<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/attach-tags/ -->

On this page

Last updated on **Nov 26, 2025**

# Attach custom tags and metadata

Attach key-value pairs to traces for organization, search, and filtering.

**Tags** are mutable and can be updated after a trace is logged. Use tags for dynamic information that may change, such as user feedback, review status, or data quality assessments.

**Metadata** is write-once and immutable after logging. Use metadata for fixed information captured during execution, such as model version, environment, or system configuration.

This guide shows you how to set and managed metadata and tags.

API / Method| Use Case| [`mlflow.update_current_trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>) API.| Setting tags or metadata on an **active** trace during the code execution.| [`MlflowClient.set_trace_tag`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.set_trace_tag>) API.| Set or update tags on a finished trace.| MLflow UI| Set or update tags on a finished trace.  
---|---  
  
## Prerequisitesâ

  1. Install MLflow and required packages

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.1.0" openai "databricks-connect>=16.1"  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




## Setting metadata on an active traceâ

If you are using automatic tracing or fluent APIs to create traces and want to add metadata to the trace during its execution, you can use the [`mlflow.update_current_trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>) function.

For example, the following code example adds the `"model_version": "v1.2.3"` metadata to the trace created for the `my_func` function:

Python
    
    
    import mlflow  
      
    @mlflow.trace  
    def my_func(x):  
        mlflow.update_current_trace(metadata={"model_version": "v1.2.3", "environment": "production"})  
        return x + 1  
      
    my_func(10)  
    

note

Metadata is immutable once set. If you try to update metadata with a key that already exists, the operation will be ignored and the original value will remain unchanged.

## Setting tags on an active traceâ

If you are using automatic tracing or fluent APIs to create traces and want to add tags to the trace during its execution, you can use the [`mlflow.update_current_trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>) function.

For example, the following code example adds the `"fruit": "apple"` tag to the trace created for the `my_func` function:

Python
    
    
    @mlflow.trace  
    def my_func(x):  
        mlflow.update_current_trace(tags={"fruit": "apple"})  
        return x + 1  
      
    my_func(10)  
    

note

The [`mlflow.update_current_trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>) function adds the specified tag(s) to the current trace when the key is not already present. If the key is already present, it updates the key with the new value.

## Setting tags on a finished traceâ

To set tags on a trace that has already been completed and logged in the backend store, use the [`mlflow.set_trace_tag`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_trace_tag>) method to set a tag on a trace, and the [`mlflow.delete_trace_tag`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.delete_trace_tag>) method to remove a tag from a trace.

Python
    
    
    import mlflow  
      
    # Create and execute a traced function  
    @mlflow.trace  
    def process_data(data):  
        return data.upper()  
      
    # Execute the function to create a trace  
    result = process_data("hello world")  
      
    # Get the trace_id from the most recent trace  
    trace_id = mlflow.get_last_active_trace_id()  
      
    # Set a tag on the trace  
    mlflow.set_trace_tag(trace_id=trace_id, key="review_status", value="approved")  
      
    # Set another tag  
    mlflow.set_trace_tag(trace_id=trace_id, key="data_quality", value="high")  
      
    # Delete a tag from the trace  
    mlflow.delete_trace_tag(trace_id=trace_id, key="data_quality")  
    

## Setting tags using the MLflow UIâ

Alternatively, you can update or delete tags on a trace from the MLflow UI. To do this, navigate to the trace tab, then click on the pencil icon next to the tag you want to update.

## Next stepsâ

  * [Add context to traces](</aws/en/mlflow3/genai/tracing/add-context-to-traces>) \- Track users, sessions, versions, and environments in your traces
  * [Search traces programmatically](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-via-sdk>) \- Filter and search traces using tags and metadata
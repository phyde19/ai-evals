<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/faq -->

On this page

Last updated on **Nov 26, 2025**

# Tracing FAQ

### Q: What is the latency overhead introduced by Tracing?â

Traces are written asynchronously to minimize performance impact. However, tracing still adds minimal latency, particularly when the trace size is large. MLflow recommends testing your application to understand tracing latency impacts before deploying to production.

The following table provides rough estimates for latency impact by trace size:

Trace size per request| Impact to response speed latency (ms)| ~10 KB| ~ 1 ms| ~ 1 MB| 50 ~ 100 ms| 10 MB| 150 ms ~  
---|---  
  
### Q: What are the rate limits and quotas for MLflow Tracing in Databricks?â

When using MLflow Tracing within a Databricks workspace quotas and rate limits apply to ensure service stability and fair usage. See [Resource limits](</aws/en/resources/limits>).

### Q: I cannot open my trace in the MLflow UI. What should I do?â

There are multiple possible reasons why a trace may not be viewable in the MLflow UI.

  1. **The trace is not completed yet** : If the trace is still being collected, MLflow cannot display spans in the UI. Ensure that all spans are properly ended with either "OK" or "ERROR" status.

  2. **The browser cache is outdated** : When you upgrade MLflow to a new version, the browser cache may contain outdated data and prevent the UI from displaying traces correctly. Clear your browser cache (Shift+F5) and refresh the page.




### Q: The model execution gets stuck and my trace is "in progress" forever.â

Sometimes a model or an agent gets stuck in a long-running operation or an infinite loop, causing the trace to be stuck in the "in progress" state.

To prevent this, you can set a timeout for the trace using the `MLFLOW_TRACE_TIMEOUT_SECONDS` environment variable. If the trace exceeds the timeout, MLflow will automatically halt the trace with `ERROR` status and export it to the backend, so that you can analyze the spans to identify the issue. By default, the timeout is not set.

note

The timeout only applies to MLflow trace. The main program, model, or agent, will continue to run even if the trace is halted.

For example, the following code sets the timeout to 5 seconds and simulates how MLflow handles a long-running operation:

Python
    
    
    import mlflow  
    import os  
    import time  
      
    # Set the timeout to 5 seconds for demonstration purposes  
    os.environ["MLFLOW_TRACE_TIMEOUT_SECONDS"] = "5"  
      
      
    # Simulate a long-running operation  
    @mlflow.trace  
    def long_running():  
        for _ in range(10):  
            child()  
      
      
    @mlflow.trace  
    def child():  
        time.sleep(1)  
      
      
    long_running()  
    

note

MLflow monitors the trace execution time and expiration in a background thread. By default, this check is performed every second and resource consumption is negligible. If you want to adjust the interval, you can set the `MLFLOW_TRACE_TIMEOUT_CHECK_INTERVAL_SECONDS` environment variable.

### Q: My trace is split into multiple traces when doing multi-threading. How can I combine them into a single trace?â

As MLflow Tracing depends on Python ContextVar, each thread has its own trace context by default, but it is possible to generate a single trace for multi-threaded applications with a few additional steps. See [Multi-threading](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator#multi-threading>) section for more information.

### Q: How do I temporarily disable tracing?â

To **disable** tracing, [`mlflow.tracing.disable`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.disable>) API will cease the collection of trace data from within MLflow and will not log any data to the MLflow Tracking service regarding traces.

To **enable** tracing (if it had been temporarily disabled), [`mlflow.tracing.enable`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.enable>) API will re-enable tracing functionality for instrumented models that are invoked.

### Q: My trace search results are too big for `mlflow.search_traces()`. How do I search traces at scale?â

The MLflow API provides pagination through the [`MlflowClient.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_traces>) method. However, for use cases not requiring pagination, [`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>) is recommended since it provides more functionality and convenient defaults.

For large-scale trace analysis in production, it is generally best to use [production monitoring](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) to log traces to Delta tables in Unity Catalog. See [Trace agents deployed on Databricks](</aws/en/mlflow3/genai/tracing/prod-tracing>) for production tracing guidance.
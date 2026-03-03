<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/third-party/langfuse -->

On this page

Last updated on **Feb 26, 2026**

# Export Langfuse traces to Databricks MLflow

Configure [Langfuse](<https://langfuse.com/>) to send OpenTelemetry-based trace spans to the Databricks MLflow OTLP endpoint, so that traces are stored in Unity Catalog tables alongside your other MLflow traces.

Consolidating traces on Databricks provides the following benefits:

  * Query and compare Langfuse-instrumented calls together with traces from other frameworks in a single place.
  * Use Databricks SQL to analyze trace data at scale.
  * Apply Unity Catalog governance such as access controls and lineage to all your traces.



## Requirementsâ

  * A Databricks workspace with the "OpenTelemetry on Databricks" preview enabled. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).
  * A new MLflow experiment.



## Step 1: Install packagesâ

Install the required packages in your Databricks notebook:

Python
    
    
    %pip install "langfuse>=3.14.5" "mlflow[databricks]>=3.10.0" opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-http  
    %restart_python  
    

## Step 2: Disable Langfuse trace collectionâ

Langfuse requires the `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY` environment variables to initialize its SDK. Set these variables to dummy values to prevent traces from being sent to a Langfuse server. Only the OTEL exporter, configured in Add the OTLP exporter, will receive the spans.

Python
    
    
    import os  
      
    os.environ["LANGFUSE_HOST"] = "localhost"  
    os.environ["LANGFUSE_PUBLIC_KEY"] = ""  
    os.environ["LANGFUSE_SECRET_KEY"] = ""  
    

note

This is the simplest approach to prevent Langfuse from collecting traces on its own servers. Alternatively, you can set `LANGFUSE_TRACING_ENABLED=False` to disable Langfuse's built-in trace collection.

## Step 3: Configure Databricks connectionâ

Retrieve the workspace host URL and an API token. In a Databricks notebook, you can get these from the notebook context:

Python
    
    
    # If running outside a Databricks notebook, set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables manually.  
    context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()  
    DATABRICKS_HOST = context.apiUrl().get().rstrip("/")  
    DATABRICKS_TOKEN = context.apiToken().get()  
    

## Step 4: Link an experiment to Unity Catalogâ

Define your Unity Catalog catalog and schema, then link them to an MLflow experiment using `set_experiment_trace_location`. This tells Databricks where to store the incoming traces.

Python
    
    
    import mlflow  
    from mlflow.entities import UCSchemaLocation  
    from mlflow.tracing.enablement import set_experiment_trace_location  
      
    CATALOG_NAME = "<UC_CATALOG_NAME>"  
    SCHEMA_NAME = "<UC_SCHEMA_NAME>"  
    EXPERIMENT_ID = "<EXPERIMENT_ID>"  
      
    trace_location = set_experiment_trace_location(  
        location=UCSchemaLocation(catalog_name=CATALOG_NAME, schema_name=SCHEMA_NAME),  
        experiment_id=EXPERIMENT_ID,  
    )  
    

## Step 5: Add the Databricks OTLP exporterâ

Get the `TracerProvider` that Langfuse uses, then attach a `BatchSpanProcessor` with an `OTLPSpanExporter` that points to the Databricks OTLP endpoint.

Python
    
    
    from langfuse import get_client  
    from opentelemetry import trace as otel_trace  
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  
      
    # Initialize the Langfuse client. Langfuse registers its own TracerProvider as the global OpenTelemetry TracerProvider.  
    langfuse = get_client()  
      
    # Retrieve the global TracerProvider.  
    # Use this to attach an additional span processor that forwards Langfuse spans to Databricks.  
    provider = otel_trace.get_tracer_provider()  
      
    # Configure the OTLP exporter to send spans to the Databricks MLflow endpoint.  
    # The X-Databricks-UC-Table-Name header routes incoming spans to the Unity Catalog table defined by the trace location.  
    databricks_exporter = OTLPSpanExporter(  
        endpoint=f"{DATABRICKS_HOST}/api/2.0/otel/v1/traces",  
        headers={  
            "content-type": "application/x-protobuf",  
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",  
            "X-Databricks-UC-Table-Name": trace_location.full_otel_spans_table_name,  
        },  
    )  
      
    # Attach the Databricks exporter to Langfuse's provider. Because the Langfuse  
    # env vars are set to dummy values, this processor is the only active exporter,  
    # so all spans are sent exclusively to Databricks.  
    provider.add_span_processor(BatchSpanProcessor(databricks_exporter))  
    

## Step 6: Run a traced functionâ

Use Langfuse's `@observe()` decorator to instrument your functions. The decorator creates OTEL spans that the exporter sends to Databricks.

Python
    
    
    from langfuse import observe  
      
    @observe()  
    def my_llm_call(prompt: str) -> str:  
        # Replace with your LLM logic (OpenAI, Anthropic, etc.)  
        return f"Response to: {prompt}"  
      
    @observe()  
    def my_pipeline(user_input: str) -> str:  
        result = my_llm_call(user_input)  
        return result  
      
    my_pipeline("Hello, world!")  
    

## Step 7: View tracesâ

Open the MLflow experiment in your Databricks workspace and click the **Traces** tab. The trace from the `my_pipeline` call should appear.

## Next stepsâ

  * [Store MLflow traces in Unity Catalog](</aws/en/mlflow3/genai/tracing/trace-unity-catalog>): Learn more about storing and managing traces in Unity Catalog tables.
  * [View traces in the Databricks MLflow UI](</aws/en/mlflow3/genai/tracing/observe-with-traces/ui-traces>): Search and filter traces in the MLflow UI.
  * [Query MLflow traces using MLflow Databricks SQL](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-dbsql>): Query trace data directly using SQL through a Databricks SQL warehouse.
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/trace-unity-catalog -->

On this page

Last updated on **Feb 26, 2026**

# Store MLflow traces in Unity Catalog

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

Databricks supports storing MLflow traces in Unity Catalog tables using an OpenTelemetry-compatible format (OTEL). By default, MLflow stores traces organized by experiments in the MLflow control plane service. However, storing traces in Unity Catalog using OTEL format provides the following benefits:

  * Access control is managed through Unity Catalog schema and table permissions rather than experiment-level ACLs. Users with access to the Unity Catalog tables can view all traces stored in those tables, regardless of which experiment the traces belong to.

  * Trace IDs use URI format instead of the `tr-<UUID>` format, improving compatibility with external systems.

  * Store unlimited traces in Delta tables, enabling long-term retention and analysis of trace data. See [Performance considerations](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-dbsql#performance-considerations>).

  * Query trace data directly using SQL through a Databricks SQL warehouse, enabling advanced analytics and custom reporting.

  * OTEL format ensures compatibility with other OpenTelemetry clients and tools




## Prerequisitesâ

  * A Unity Catalog-enabled workspace.
  * Ensure the "OpenTelemetry on Databricks" preview is enabled. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).
  * Permissions to create catalogs and schemas in Unity Catalog.
  * A [Databricks SQL warehouse](</aws/en/compute/sql-warehouse/>) with `CAN USE` permissions. Save the warehouse ID for later reference.


  * While this feature is in [Beta](</aws/en/release-notes/release-types>), your workspace must be in one of the following regions:
    * `us-east-1`
    * `us-west-2`


  * MLflow Python library version 3.9.0 or later installed in your environment:

Bash
        
        pip install mlflow[databricks]>=3.9.0 --upgrade --force-reinstall  
        




##  Setup: Create UC tables and link an experimentâ

Create the Unity Catalog tables to store the traces. Then, link the Unity Catalog schema containing the tables to an MLflow experiment to write its traces to the tables by default:

important

The experiment you link must only have Unity Catalog traces. Linking fails if the experiment already has traces in MLflow experiment storage. This can happen if you previously ran a traced function against the experiment without setting up Unity Catalog storage. Use a brand new experiment with no trace history or select an experiment with only Unity Catalog traces.

Python
    
    
    # Example values for the placeholders below:  
    # MLFLOW_TRACING_SQL_WAREHOUSE_ID: "abc123def456" (found in SQL warehouse URL)  
    # experiment_name: "/Users/user@company.com/traces"  
    # catalog_name: "main" or "my_catalog"  
    # schema_name: "mlflow_traces" or "production_traces"  
      
    import os  
    import mlflow  
    from mlflow.exceptions import MlflowException  
    from mlflow.entities import UCSchemaLocation  
    from mlflow.tracing.enablement import set_experiment_trace_location  
      
    mlflow.set_tracking_uri("databricks")  
      
    # Specify the ID of a SQL warehouse you have access to.  
    os.environ["MLFLOW_TRACING_SQL_WAREHOUSE_ID"] = "<SQL_WAREHOUSE_ID>"  
    # Specify the name of the MLflow Experiment to use for viewing traces in the UI.  
    experiment_name = "<MLFLOW_EXPERIMENT_NAME>"  
    # Specify the name of the Catalog to use for storing traces.  
    catalog_name = "<UC_CATALOG_NAME>"  
    # Specify the name of the Schema to use for storing traces.  
    schema_name = "<UC_SCHEMA_NAME>"  
      
    if experiment := mlflow.get_experiment_by_name(experiment_name):  
        experiment_id = experiment.experiment_id  
    else:  
        experiment_id = mlflow.create_experiment(name=experiment_name)  
    print(f"Experiment ID: {experiment_id}")  
      
    # To link an experiment to a trace location  
    result = set_experiment_trace_location(  
        location=UCSchemaLocation(catalog_name=catalog_name, schema_name=schema_name),  
        experiment_id=experiment_id,  
    )  
    print(result.full_otel_spans_table_name)  
    

### Verify tablesâ

After running the setup code, three new Unity Catalog tables will be visible in the schema in the Catalog Explorer UI:

  * `mlflow_experiment_trace_otel_logs`
  * `mlflow_experiment_trace_otel_metrics`
  * `mlflow_experiment_trace_otel_spans`



## Grant permissionsâ

The following permissions are required for a Databricks user or service principal to write or read MLflow Traces from the Unity Catalog tables:

  1. **USE_CATALOG** permissions on the catalog.
  2. **USE_SCHEMA** permissions on the schema.
  3. **MODIFY** and **SELECT** permissions on each of the `mlflow_experiment_trace_<type>` tables.



note

`ALL_PRIVILEGES` is not sufficient for accessing Unity Catalog trace tables. You must explicitly grant **MODIFY** and **SELECT** permissions.

## Log traces to the Unity Catalog tablesâ

After creating the tables, you can write traces to them from various sources by specifying the trace destination. How you do this depends on the source of the traces.

  * MLflow SDK
  * Databricks App
  * Model Serving endpoint
  * 3rd party OTEL client



The catalog and schema can be specified using the [`mlflow.tracing.set_destination`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.set_destination>) Python API, or by setting the `MLFLOW_TRACING_DESTINATION` environment variable.

Python
    
    
    import mlflow  
      
    mlflow.set_tracking_uri("databricks")  
      
    # Specify the name of the catalog and schema to use for storing Traces  
    catalog_name = "<UC_CATALOG_NAME>"  
    schema_name = "<UC_SCHEMA_NAME>"  
      
    # Option 1: Use the `set_destination` API to configure the catalog and schema for  
    # storing MLflow Traces  
    from mlflow.entities import UCSchemaLocation  
    mlflow.tracing.set_destination(  
        destination=UCSchemaLocation(  
            catalog_name=catalog_name,  
            schema_name=schema_name,  
        )  
    )  
      
    # Option 2: Use the `MLFLOW_TRACING_DESTINATION` environment variable to configure the  
    # catalog and schema for storing MLflow Traces  
    import os  
    os.environ["MLFLOW_TRACING_DESTINATION"] = f"{catalog_name}.{schema_name}"  
      
    # Create and ingest an example trace using the `@mlflow.trace` decorator  
    @mlflow.trace  
    def test(x):  
        return x + 1  
      
    test(100)  
    

A Databricks App running `mlflow >= 3.5.0` can write traces to Unity Catalog, as long as the Databricks App's [service principal](</aws/en/dev-tools/databricks-apps/auth#app-authorization>) has access to the Unity Catalog tables.

To give your Databricks App's service principal access to Unity Catalog tables for trace ingestion:

  1. Find your app's service principal name under the **Authorization** tab of the app.

  2. Grant the service principal `MODIFY` and `SELECT` access to the `logs` and `spans` tables.

  3. Update your Databricks App code to set the catalog and schema for trace ingestion:

Python
         
         import mlflow  
           
         mlflow.set_tracking_uri("databricks")  
         # Specify the name of the catalog and schema to use for storing Traces  
         catalog_name = "<UC_CATALOG_NAME>"  
         schema_name = "<UC_SCHEMA_NAME>"  
           
         # Option 1: Use the `set_destination` API to configure the catalog and schema for  
         # storing MLflow Traces  
         from mlflow.entities import UCSchemaLocation  
         mlflow.tracing.set_destination(  
             destination=UCSchemaLocation(  
                 catalog_name=catalog_name,  
                 schema_name=schema_name,  
             )  
         )  
           
         # Option 2: Use the `MLFLOW_TRACING_DESTINATION` environment variable to configure the  
         # catalog and schema for storing MLflow Traces  
         import os  
         os.environ["MLFLOW_TRACING_DESTINATION"] = f"{catalog_name}.{schema_name}"  
           
         # Create and ingest an example trace using the `@mlflow.trace` decorator  
         @mlflow.trace  
         def test(x):  
             return x + 1  
           
         test(100)  
         

  4. Deploy the Databricks App.




To write traces from a Databricks model serving endpoint to Unity Catalog tables, you must configure a Personal Access Token (PAT).

  1. Grant a user or service principal `MODIFY` and `SELECT` access to the `logs` and `spans` tables.
  2. [Generate a PAT](</aws/en/dev-tools/auth/pat#pat-user>) for the user or service principal.
  3. Add the PAT to the [Databricks model serving endpoint's environment variables configuration](</aws/en/machine-learning/model-serving/store-env-variable-model-serving#plain-text>), specifying `DATABRICKS_TOKEN` as the environment variable name.
  4. Add the trace location to write to as a `"{catalog}.{schema}"` string to the [Databricks model serving endpoint's environment variables configuration](</aws/en/machine-learning/model-serving/store-env-variable-model-serving#plain-text>) with `MLFLOW_TRACING_DESTINATION` as the environment variable name:



Python
    
    
    import mlflow  
    import os  
      
    mlflow.set_tracking_uri("databricks")  
      
    # Specify the name of the catalog and schema to use for storing Traces  
    catalog_name = "<UC_CATALOG_NAME>"  
    schema_name = "<UC_SCHEMA_NAME>"  
      
    # Option 1: Use the `set_destination` API to configure the catalog and schema for  
    # storing MLflow Traces  
    from mlflow.entities import UCSchemaLocation  
    mlflow.tracing.set_destination(  
        destination=UCSchemaLocation(  
            catalog_name=catalog_name,  
            schema_name=schema_name,  
        )  
    )  
      
    # Option 2: Use the `MLFLOW_TRACING_DESTINATION` environment variable to configure the  
    # catalog and schema for storing MLflow Traces  
    os.environ["MLFLOW_TRACING_DESTINATION"] = f"{catalog_name}.{schema_name}"  
      
    # Create and ingest an example trace using the `@mlflow.trace` decorator  
    @mlflow.trace  
    def test(x):  
        return x + 1  
      
    test(100)  
    

One benefit of storing traces in the OTEL format is that you can write to the Unity Catalog tables using third party clients that support OTEL. Traces written this way will appear in an MLflow experiment linked to the table as long as they have a root span. The following example shows [OpenTelemetry OTLP exporters](<https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html>).

Python
    
    
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  
      
    # Span exporter configuration  
    otlp_trace_exporter = OTLPSpanExporter(  
        # Databricks hosted OTLP traces collector endpoint  
        endpoint="https://myworkspace.databricks.com/api/2.0/otel/v1/traces",  
        headers={  
            "content-type": "application/x-protobuf",  
            "X-Databricks-UC-Table-Name": "cat.sch.mlflow_experiment_trace_otel_spans",  
            "Authorization": "Bearer MY_API_TOKEN"  
        },  
    )  
    

See [Export Langfuse traces to Databricks MLflow](</aws/en/mlflow3/genai/tracing/third-party/langfuse>).

## View traces in the UIâ

View traces stored in OTEL format the same way you view other traces:

  1. In your Workspace, go to **Experiments**.

  2. Find the experiment where your traces are logged. For example, the experiment set by `mlflow.set_experiment("/Shared/my-genai-app-traces")`.

  3. Click **Traces** tab to see a list of all traces logged to that experiment.

  4. If you [stored your traces in a Unity Catalog table](</aws/en/mlflow3/genai/tracing/trace-unity-catalog>), Databricks retrieves traces using an [SQL warehouse](</aws/en/compute/sql-warehouse/>). Select a SQL warehouse from the drop-down menu.

  5. You can also select a different schema. When selecting an alternative schema, ensure that it already contains OpenTelemetry tables. The drop-down menu doesn't create the tables. 




For more information on using the UI to search for traces, see [View traces in the Databricks MLflow UI](</aws/en/mlflow3/genai/tracing/observe-with-traces/ui-traces>).

## Enable production monitoringâ

To use [production monitoring](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) with traces stored in Unity Catalog, you must configure a SQL warehouse ID for the experiment. The monitoring job requires this configuration to execute scorer queries against Unity Catalog tables.

Set the SQL warehouse ID using [`set_databricks_monitoring_sql_warehouse_id()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.set_databricks_monitoring_sql_warehouse_id>):

Python
    
    
    from mlflow.tracing import set_databricks_monitoring_sql_warehouse_id  
      
    # Set the SQL warehouse ID for monitoring  
    set_databricks_monitoring_sql_warehouse_id(  
        warehouse_id="<SQL_WAREHOUSE_ID>",  
        experiment_id="<EXPERIMENT_ID>"  # Optional, uses active experiment if not specified  
    )  
    

Alternatively, you can set the `MLFLOW_TRACING_SQL_WAREHOUSE_ID` environment variable before starting monitoring.

If you skip this step, monitoring jobs will fail with an error indicating the `mlflow.monitoring.sqlWarehouseId` experiment tag is missing.

To configure monitoring for Unity Catalog traces, you need the following workspace-level permissions:

  * `CAN USE` permission on the SQL warehouse
  * `CAN EDIT` permission on the MLflow experiment
  * Permission on the monitoring job (automatically granted when you register the first scorer)



The monitoring job runs under the identity of the user who first registered a scorer on the experiment. This user's permissions determine what the monitoring job can access.

## Unlink a Unity Catalog schemaâ

To unlink a Unity Catalog schema from an MLflow experiment, click the **Storage UC Schema** dropdown from the MLflow experiment UI and select **Unlink schema**.

Traces will still be present in the Unity Catalog schema, and the schema can be re-linked to the MLflow experiment at any time.

##  Limitationsâ

  * Trace ingestion is limited to 100 traces per second per workspace and 100MB per second per table.

  * UI performance may degrade when over 2TB of trace data are stored in the table. See [Performance considerations](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-dbsql#performance-considerations>).

  * Deleting individual traces is not supported for traces stored in Unity Catalog. To remove traces, you must delete rows directly from the underlying Unity Catalog tables using SQL. This differs from experiment traces, which can be deleted using the MLflow UI or API.

  * When connecting an MLflow experiment to a Unity Catalog schema, only traces stored in the Unity Catalog schema linked to the experiment are accessible. Pre-existing traces in the experiment will become **inaccessible** by search from MLflow clients Python >= 3.5.0 and from the MLflow UI. These traces remain stored in the experiment but cannot be viewed or searched while the experiment is linked to Unity Catalog.

Unlinking the schema from the MLflow experiment restores access to pre-existing traces.

  * [MLflow MCP server](</aws/en/mlflow3/genai/tracing/mlflow-mcp>) does not support interacting with traces stored in Unity Catalog.

  * Ingestion throughput limit of 200 queries per second (QPS)




## Next stepsâ

  * [Query MLflow traces using MLflow Databricks SQL](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-dbsql>)
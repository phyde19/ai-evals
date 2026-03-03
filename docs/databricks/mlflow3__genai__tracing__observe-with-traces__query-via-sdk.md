<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/query-via-sdk -->

On this page

Last updated on **Nov 26, 2025**

# Search traces programmatically

Search and analyze traces programmatically using [`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>). This function can query traces stored in the MLflow tracking server, inference tables, or Unity Catalog tables. You can select subsets of traces to analyze or to create evaluation datasets.

## `mlflow.search_traces()` APIâ

Python
    
    
    def mlflow.search_traces(  
        experiment_ids: list[str] | None = None,  
        filter_string: str | None = None,  
        max_results: int | None = None,  
        order_by: list[str] | None = None,  
        extract_fields: list[str] | None = None,  
        run_id: str | None = None,  
        return_type: Literal['pandas', 'list'] | None = None,  
        model_id: str | None = None,  
        sql_warehouse_id: str | None = None,  
        include_spans: bool = True,  
        locations: list[str] | None = None,  
    ) -> pandas.DataFrame | list[Trace]  
    

[`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>) lets you filter and select data along a few dimensions:

  * Filter by a query string
  * Filter by locations: experiment, run, model, or Unity Catalog schema
  * Limit data: max results, include or exclude spans
  * Adjust return value format: data format, data order



`search_traces()` returns either a pandas DataFrame or a list of [`Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) objects, which can then be analyzed further or reshaped into evaluation datasets. See the [schema details](<https://mlflow.org/docs/latest/genai/tracing/search-traces/#return-format>) of these return types.

See the [`mlflow.search_traces()` API docs](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>) for full details.

### `mlflow.search_traces()` parametersâ

Category| `parameter: type`| Description| Example| **Filter by query string**| `filter_string: str`| See the [search query syntax](<https://mlflow.org/docs/latest/genai/tracing/search-traces/#search-query-syntax>) including supported filters and comparators.| `attributes.status = 'OK' AND tags.environment = 'production'`| **Filter by locations**| `locations: list[str]`| This argument can be list of experiment IDs or Unity Catalog `catalog.schema` locations for filtering. Use this to search traces stored in inference or Unity Catalog tables.| `['591498498138889', '782498488231546']` or `['my_catalog.my_schema']`| | `run_id: str`| MLflow run ID| `35464a26b0144533b09d8acbb4681985`| | `model_id: str`| MLflow model ID| `acc4c426-5dd7-4a3a-85de-da1b22ce05f1`| **Limit data**| `max_results: int`| Max number of traces (rows) to return| `100`| | `include_spans: bool`| Include or exclude spans from the results. Spans include trace details and can make result sizes much larger.| `True`| **Return value format**| `order_by: list[str]`| See the [syntax and supported keys](<https://mlflow.org/docs/latest/genai/tracing/search-traces/#ordering-results>).| `["timestamp_ms DESC", "status ASC"]`| | `return_type: Literal['pandas', 'list']`| This function can return either a pandas DataFrame or a list of [`Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) objects. See [schema details](<https://mlflow.org/docs/latest/genai/tracing/search-traces/#return-format>).| `'pandas'`| **Deprecated**| `experiment_ids: list[str]`| Use `locations` instead.| | | `extract_fields: list[str]`| Select fields in the returned DataFrame or trace objects instead.| | | `sql_warehouse_id: str`| Use the `MLFLOW_TRACING_SQL_WAREHOUSE_ID` environment variable instead.|   
---|---|---|---  
  
## Best practicesâ

### Keyword argumentsâ

Always use keyword (named) arguments with `mlflow.search_traces()`. It allows positional arguments, but the function arguments are evolving.

Good practice: `mlflow.search_traces(filter_string="attributes.status = 'OK'")`

Bad practice: `mlflow.search_traces([], "attributes.status = 'OK'")`

### `filter_string` gotchasâ

When searching using the `filter_string` argument to `mlflow.search_traces()`, remember to:

  * Use prefixes: `attributes.`, `tags.`, or `metadata.`
  * Use backticks if tag or attribute names have dots: `tags.`mlflow.traceName``
  * Use single quotes only: `'value'` not `"value"`
  * Use Unix timestamp (milliseconds) for time: `1749006880539` not dates
  * Use AND only: No OR support



See the [search query syntax](<https://mlflow.org/docs/latest/genai/tracing/search-traces/#search-query-syntax>) for further details.

###  SQL warehouse integrationâ

`mlflow.search_traces()` can optionally use a Databricks [SQL warehouse](</aws/en/compute/sql-warehouse/>) to improve performance on large trace datasets in inference tables or Unity Catalog tables. Specify your SQL warehouse ID using the `MLFLOW_TRACING_SQL_WAREHOUSE_ID` environment variable.

Execute trace queries using a Databricks SQL warehouse for improved performance on large trace datasets:

Python
    
    
    import os  
      
    os.environ['MLFLOW_TRACING_SQL_WAREHOUSE_ID'] = 'fa92bea7022e81fb'  
      
    # Use SQL warehouse for better performance  
    traces = mlflow.search_traces(  
        filter_string="attributes.status = 'OK'",  
        locations=['my_catalog.my_schema'],  
    )  
    

### Paginationâ

`mlflow.search_traces()` returns results in memory, which works well for smaller result sets. To handle large result sets, use [`MlflowClient.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_traces>) since it supports pagination.

## Next stepsâ

  * [Tutorial: Search traces programmatically](</aws/en/mlflow3/genai/tracing/observe-with-traces/search-traces-examples>) \- Run a set of simple examples of `mlflow.search_traces()`
  * [Tutorial: Trace and analyze users and environments](</aws/en/mlflow3/genai/tracing/add-context-to-traces-tutorial>) \- Run an example of adding context metadata to traces and analyzing the results
  * [Examples: Analyzing traces](</aws/en/mlflow3/genai/tracing/observe-with-traces/analyze-traces>) \- See a variety of examples of trace analysis
  * [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) \- Convert queried traces into test datasets
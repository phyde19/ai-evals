<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/span-concepts -->

On this page

Last updated on **Nov 26, 2025**

# Span concepts

The [Span](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span>) object is a fundamental building block in the Trace data model. It serves as a container for information about individual steps of a trace, such as LLM calls, tool execution, retrieval operations, and more.

Spans are organized hierarchically in a trace to represent your application's execution flow. Each span captures:

  * Input and output data
  * Timing information (start and end times)
  * Status (success or error)
  * Metadata and attributes about the operation
  * Relationship to other spans (parent-child connections)



## Span object schemaâ

MLflow's Span design maintains compatibility with [OpenTelemetry specifications](<https://opentelemetry.io/docs/concepts/signals/traces#spans>). The schema includes eleven core properties:

Property| Type| Description| `span_id`| `str`| Unique identifier for this span in the trace| `trace_id`| `str`| Links span to its parent trace| `parent_id`| `Optional[str]`| Establishes hierarchical relationship; `None` for root spans| `name`| `str`| User-defined or auto-generated span name| `start_time_ns`| `int`| Unix timestamp (nanoseconds) when span started| `end_time_ns`| `int`| Unix timestamp (nanoseconds) when span ended| `status`| `SpanStatus`| Span status: `OK`, `UNSET`, or `ERROR` with optional description| `inputs`| `Optional[Any]`| Input data entering this operation| `outputs`| `Optional[Any]`| Output data exiting this operation| `attributes`| `Dict[str, Any]`| Metadata key-value pairs providing behavioral insights| `events`| `List[SpanEvent]`| System-level exceptions and stack trace information  
---|---|---  
  
For complete details, see the [MLflow API reference](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span>).

## Span attributesâ

Attributes are key-value pairs that provide insight into behavioral modifications for function and method calls. They capture metadata about the operation's configuration and execution context.

You can add platform-specific attributes like [Unity Catalog information](</aws/en/data-governance/unity-catalog/>), [model serving endpoint](</aws/en/machine-learning/model-serving/>) details, and [infrastructure metadata](</aws/en/compute/>) for enhanced observability.

Example of [`set_attributes()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span.attributes>) for an LLM call:

Python
    
    
    span.set_attributes({  
        "ai.model.name": "claude-3-5-sonnet-20250122",  
        "ai.model.version": "2025-01-22",  
        "ai.model.provider": "anthropic",  
        "ai.model.temperature": 0.7,  
        "ai.model.max_tokens": 1000,  
    })  
    

## Span typesâ

MLflow provides predefined [`SpanType`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanType>) values for categorization. You can also use custom string values for specialized operations.

Type| Description| `CHAT_MODEL`| Query to a chat model (specialized LLM interaction)| `CHAIN`| Chain of operations| `AGENT`| Autonomous agent operation| `TOOL`| Tool execution (typically by agents) like search queries| `EMBEDDING`| Text embedding operation| `RETRIEVER`| Context retrieval operation such as vector database queries| `PARSER`| Parsing operation transforming text to structured format| `RERANKER`| Re-ranking operation ordering contexts by relevance| `MEMORY`| Memory operation persisting context in long-term storage| `UNKNOWN`| Default type when no other type specified  
---|---  
  
### Setting span typesâ

Use the `span_type` parameter with decorators or context managers to set [`SpanType`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanType>):

Python
    
    
    import mlflow  
    from mlflow.entities import SpanType  
      
    # Using a built-in span type  
    @mlflow.trace(span_type=SpanType.RETRIEVER)  
    def retrieve_documents(query: str):  
        ...  
      
    # Using a custom span type  
    @mlflow.trace(span_type="ROUTER")  
    def route_request(request):  
        ...  
      
    # With context manager  
    with mlflow.start_span(name="process", span_type=SpanType.TOOL) as span:  
        span.set_inputs({"data": data})  
        result = process_data(data)  
        span.set_outputs({"result": result})  
    

### Searching spans by typeâ

Query spans programmatically using [MLflow `search_spans()`](</aws/en/mlflow3/genai/tracing/observe-with-traces/access-trace-data#search-span>):

Python
    
    
    import mlflow  
    from mlflow.entities import SpanType  
      
    trace = mlflow.get_trace("<trace_id>")  
    retriever_spans = trace.search_spans(span_type=SpanType.RETRIEVER)  
    

You can also filter by span type in the MLflow UI when viewing traces.

## Active vs. finished spansâ

An active span or [`LiveSpan`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.LiveSpan>) is one being actively logged, such as in a [function decorated with `@mlflow.trace`](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>) or a [span context manager](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/span-tracing>). Once the decorated function or context manager have exited, the span is finished and becomes an immutable [`Span`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span>).

To modify the active span, get a handle to the span using [`mlflow.get_current_active_span()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_current_active_span>).

##  `RETRIEVER` span schemaâ

The `RETRIEVER` span type handles operations involving retrieving data from a data store, such as querying documents from a vector store. This span type has a specific output schema that enables enhanced UI features and evaluation capabilities. The output should be a list of documents, where each document is a dictionary with:

  * **`page_content`** (`str`): Text content of the retrieved document chunk
  * **`metadata`** (`Optional[Dict[str, Any]]`): Additional metadata, including:
    * `doc_uri` (`str`): Document source URI. When using [Vector Search](</aws/en/vector-search/vector-search>) on Databricks, RETRIEVER spans can include Unity Catalog volume paths in the `doc_uri` metadata for full lineage tracking.
    * `chunk_id` (`str`): Identifier if document is part of a larger chunked document
  * **`id`** (`Optional[str]`): Unique identifier for the document chunk



The MLflow [`Document` entity](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Document>) helps to construct this output structure.

**Example implementation** :

Python
    
    
    import mlflow  
    from mlflow.entities import SpanType, Document  
      
    def search_store(query: str) -> list[tuple[str, str]]:  
        # Simulate retrieving documents from a vector database  
        return [  
            ("MLflow Tracing helps debug GenAI applications...", "docs/mlflow/tracing_intro.md"),  
            ("Key components of a trace include spans...", "docs/mlflow/tracing_datamodel.md"),  
            ("MLflow provides automatic instrumentation...", "docs/mlflow/auto_trace.md"),  
        ]  
      
    @mlflow.trace(span_type=SpanType.RETRIEVER)  
    def retrieve_relevant_documents(query: str):  
        docs = search_store(query)  
        span = mlflow.get_current_active_span()  
      
        # Set outputs in the expected format  
        outputs = [  
            Document(page_content=doc, metadata={"doc_uri": uri})  
            for doc, uri in docs  
        ]  
        span.set_outputs(outputs)  
      
        return docs  
      
    # Usage  
    user_query = "MLflow Tracing benefits"  
    retrieved_docs = retrieve_relevant_documents(user_query)  
    

## Next stepsâ

  * [Trace concepts](</aws/en/mlflow3/genai/tracing/tracing-101>) \- Understand trace-level concepts and structure
  * [Tracing in a notebook](</aws/en/mlflow3/genai/getting-started/tracing/tracing-notebook>) \- Get hands-on experience with tracing
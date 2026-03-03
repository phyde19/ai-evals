<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/access-trace-data -->

On this page

Last updated on **Nov 26, 2025**

# Access trace data

This page demonstrates how to access every aspect of trace data including metadata, spans, assessments, and more. Once you learn how to access trace data, see [Examples: Analyzing traces](</aws/en/mlflow3/genai/tracing/observe-with-traces/analyze-traces>)

The MLflow [`Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) object consists of two main components:

  * [`TraceInfo`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>), metadata about the trace:

    * ID and status
    * Preview data
    * Timing
    * Tags
    * Token usage
    * Assessments
  * [`TraceData`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceData>), the actual execution data:

    * Spans
    * Full request and response data



##  Basic metadata propertiesâ

**API Reference:** [`TraceInfo`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>)

Python
    
    
    # Primary identifiers  
    print(f"Trace ID: {trace.info.trace_id}")  
    print(f"Client Request ID: {trace.info.client_request_id}")  
      
    # Status information  
    print(f"State: {trace.info.state}")  # OK, ERROR, IN_PROGRESS  
    print(f"Status (deprecated): {trace.info.status}")  # Use state instead  
      
    # Request/response previews (truncated)  
    print(f"Request preview: {trace.info.request_preview}")  
    print(f"Response preview: {trace.info.response_preview}")  
    

### Storage location and experimentâ

Python
    
    
    # Trace storage location  
    location = trace.info.trace_location  
    print(f"Location type: {location.type}")  
      
    # If stored in MLflow experiment  
    if location.mlflow_experiment:  
        print(f"Experiment ID: {location.mlflow_experiment.experiment_id}")  
        # Shortcut property  
        print(f"Experiment ID: {trace.info.experiment_id}")  
      
    # If stored in Databricks inference table  
    if location.inference_table:  
        print(f"Table: {location.inference_table.full_table_name}")  
    

##  Request and response previewsâ

The [`request_preview`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>) and [`response_preview`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>) properties provide truncated summaries of the full request and response data, making it easy to quickly understand what happened without loading the complete payloads.

Python
    
    
    request_preview = trace.info.request_preview  
    response_preview = trace.info.response_preview  
      
    print(f"Request preview: {request_preview}")  
    print(f"Response preview: {response_preview}")  
      
    # Compare with full request/response data  
    full_request = trace.data.request  # Complete request text  
    full_response = trace.data.response  # Complete response text  
      
    if full_request and request_preview:  
        print(f"Full request length: {len(full_request)} characters")  
        print(f"Preview is {len(request_preview)/len(full_request)*100:.1f}% of full request")  
    

##  Time-related propertiesâ

**API Reference:** [`TraceInfo`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>) timing properties

Python
    
    
    # Timestamps (milliseconds since epoch)  
    print(f"Start time (ms): {trace.info.request_time}")  
    print(f"Timestamp (ms): {trace.info.timestamp_ms}")  # Alias for request_time  
      
    # Duration  
    print(f"Execution duration (ms): {trace.info.execution_duration}")  
    print(f"Execution time (ms): {trace.info.execution_time_ms}")  # Alias  
      
    # Convert to human-readable format  
    import datetime  
    start_time = datetime.datetime.fromtimestamp(trace.info.request_time / 1000)  
    print(f"Started at: {start_time}")  
    

##  Tags and metadataâ

**API Reference:** [`TraceInfo.tags`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>) and [`TraceInfo.trace_metadata`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>)

Python
    
    
    # Tags (mutable, can be updated after creation)  
    print("Tags:")  
    for key, value in trace.info.tags.items():  
        print(f"  {key}: {value}")  
      
    # Access specific tags  
    print(f"Environment: {trace.info.tags.get('environment')}")  
    print(f"User ID: {trace.info.tags.get('user_id')}")  
      
    # Trace metadata (immutable, set at creation)  
    print("\nTrace metadata:")  
    for key, value in trace.info.trace_metadata.items():  
        print(f"  {key}: {value}")  
      
    # Deprecated alias  
    print(f"Request metadata: {trace.info.request_metadata}")  # Same as trace_metadata  
    

##  Token usage informationâ

MLflow Tracing can track token usage of LLM calls, using token counts returned by LLM provider APIs.

Python
    
    
    # Get aggregated token usage (if available)  
    token_usage = trace.info.token_usage  
    if token_usage:  
        print(f"Input tokens: {token_usage.get('input_tokens')}")  
        print(f"Output tokens: {token_usage.get('output_tokens')}")  
        print(f"Total tokens: {token_usage.get('total_tokens')}")  
    

How you track token usage depends on the LLM provider. The following table describes different methods for tracking token usage across various providers and platforms.

**Scenario**| **How to track token usage**| [Databricks Foundation Model APIs](</aws/en/machine-learning/foundation-model-apis/>)| Use the OpenAI client to verify that MLflow Tracing automatically tracks token usage.| LLM providers with native MLflow Tracing support| See the provider's integration page under [MLflow Tracing Integrations](<https://mlflow.org/docs/latest/genai/tracing/integrations/>) to determine if native token tracking is supported.| Providers without native MLflow Tracing support| Manually log token usage using [`Span.set_attribute`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.LiveSpan.set_attribute>), as shown in [this example](</aws/en/mlflow3/genai/tracing/observe-with-traces/analyze-traces#creating-complex-example-trace>).| Monitor multiple endpoints across your AI platform.| Use [AI Gateway usage tracking](</aws/en/ai-gateway/configure-ai-gateway-endpoints#usage-tracking-table-schemas>) for logging token usage to system tables across serving endpoints.  
---|---  
  
##  Assessmentsâ

Find assessments with `search_assessments()`.

**API Reference:** [`Trace.search_assessments`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace.search_assessments>)

Python
    
    
    # 1. Get all assessments  
    all_assessments = trace.search_assessments()  
    print(f"Total assessments: {len(all_assessments)}")  
      
    # 2. Search by name  
    helpfulness = trace.search_assessments(name="helpfulness")  
    if helpfulness:  
        assessment = helpfulness[0]  
        print(f"Helpfulness: {assessment.value}")  
        print(f"Source: {assessment.source.source_type} - {assessment.source.source_id}")  
        print(f"Rationale: {assessment.rationale}")  
      
    # 3. Search by type  
    feedback_only = trace.search_assessments(type="feedback")  
    expectations_only = trace.search_assessments(type="expectation")  
    print(f"Feedback assessments: {len(feedback_only)}")  
    print(f"Expectation assessments: {len(expectations_only)}")  
      
    # 4. Search by span ID  
    span_assessments = trace.search_assessments(span_id=retriever_span.span_id)  
    print(f"Assessments for retriever span: {len(span_assessments)}")  
      
    # 5. Get all assessments including overridden ones  
    all_including_invalid = trace.search_assessments(all=True)  
    print(f"All assessments (including overridden): {len(all_including_invalid)}")  
      
    # 6. Combine criteria  
    human_feedback = trace.search_assessments(  
        type="feedback",  
        name="helpfulness"  
    )  
    for fb in human_feedback:  
        print(f"Human feedback: {fb.name} = {fb.value}")  
    

Access assessment details

Python
    
    
    # Get detailed assessment information  
    for assessment in trace.info.assessments:  
        print(f"\nAssessment: {assessment.name}")  
        print(f"  Type: {type(assessment).__name__}")  
        print(f"  Value: {assessment.value}")  
        print(f"  Source: {assessment.source.source_type.value}")  
        print(f"  Source ID: {assessment.source.source_id}")  
      
        # Optional fields  
        if assessment.rationale:  
            print(f"  Rationale: {assessment.rationale}")  
        if assessment.metadata:  
            print(f"  Metadata: {assessment.metadata}")  
        if assessment.error:  
            print(f"  Error: {assessment.error}")  
        if hasattr(assessment, 'span_id') and assessment.span_id:  
            print(f"  Span ID: {assessment.span_id}")  
    

##  Work with Spansâ

Spans are the building blocks of traces, representing individual operations or units of work. The [`Span`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span>) class represents immutable, completed spans retrieved from traces.

### Access span propertiesâ

**API Reference:** [`TraceData.spans`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceData>), [`Span`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span>), and [`SpanType`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanType>)

Python
    
    
    # Access all spans from a trace  
    spans = trace.data.spans  
    print(f"Total spans: {len(spans)}")  
      
    # Get a specific span  
    span = spans[0]  
      
    # Basic properties  
    print(f"Span ID: {span.span_id}")  
    print(f"Name: {span.name}")  
    print(f"Type: {span.span_type}")  
    print(f"Trace ID: {span.trace_id}")  # Which trace this span belongs to  
    print(f"Parent ID: {span.parent_id}")  # None for root spans  
      
    # Timing information (nanoseconds)  
    print(f"Start time: {span.start_time_ns}")  
    print(f"End time: {span.end_time_ns}")  
    duration_ms = (span.end_time_ns - span.start_time_ns) / 1_000_000  
    print(f"Duration: {duration_ms:.2f}ms")  
      
    # Status information  
    print(f"Status: {span.status}")  
    print(f"Status code: {span.status.status_code}")  
    print(f"Status description: {span.status.description}")  
      
    # Inputs and outputs  
    print(f"Inputs: {span.inputs}")  
    print(f"Outputs: {span.outputs}")  
      
    # Iterate through all spans  
    for span in spans:  
        print(f"\nSpan: {span.name}")  
        print(f"  ID: {span.span_id}")  
        print(f"  Type: {span.span_type}")  
        print(f"  Duration (ms): {(span.end_time_ns - span.start_time_ns) / 1_000_000:.2f}")  
      
        # Parent-child relationships  
        if span.parent_id:  
            print(f"  Parent ID: {span.parent_id}")  
    

### Find specific spansâ

Use [`search_spans()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace.search_spans>) to find spans matching specific criteria:

Python
    
    
    import re  
    from mlflow.entities import SpanType  
      
    # 1. Search by exact name  
    retriever_spans = trace.search_spans(name="retrieve_documents")  
    print(f"Found {len(retriever_spans)} retriever spans")  
      
    # 2. Search by regex pattern  
    pattern = re.compile(r".*_tool$")  
    tool_spans = trace.search_spans(name=pattern)  
    print(f"Found {len(tool_spans)} tool spans")  
      
    # 3. Search by span type  
    chat_spans = trace.search_spans(span_type=SpanType.CHAT_MODEL)  
    llm_spans = trace.search_spans(span_type="CHAT_MODEL")  # String also works  
    print(f"Found {len(chat_spans)} chat model spans")  
      
    # 4. Search by span ID  
    specific_span = trace.search_spans(span_id=retriever_spans[0].span_id)  
    print(f"Found span: {specific_span[0].name if specific_span else 'Not found'}")  
      
    # 5. Combine criteria  
    tool_fact_check = trace.search_spans(  
        name="fact_check_tool",  
        span_type=SpanType.TOOL  
    )  
    print(f"Found {len(tool_fact_check)} fact check tool spans")  
      
    # 6. Get all spans of a type  
    all_tools = trace.search_spans(span_type=SpanType.TOOL)  
    for tool in all_tools:  
        print(f"Tool: {tool.name}")  
    

#### Intermediate outputsâ

Python
    
    
    # Get intermediate outputs from non-root spans  
    intermediate = trace.data.intermediate_outputs  
    if intermediate:  
        print("\nIntermediate outputs:")  
        for span_name, output in intermediate.items():  
            print(f"  {span_name}: {output}")  
    

### Span attributesâ

**API Reference:** [`Span.get_attribute`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span.get_attribute>) and [`SpanAttributeKey`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.constant.SpanAttributeKey>)

Python
    
    
    from mlflow.tracing.constant import SpanAttributeKey  
      
    # Get a chat model span  
    chat_span = trace.search_spans(span_type=SpanType.CHAT_MODEL)[0]  
      
    # Get all attributes  
    print("All span attributes:")  
    for key, value in chat_span.attributes.items():  
        print(f"  {key}: {value}")  
      
    # Get specific attribute  
    specific_attr = chat_span.get_attribute("custom_attribute")  
    print(f"Custom attribute: {specific_attr}")  
      
    # Access chat-specific attributes using SpanAttributeKey  
    messages = chat_span.get_attribute(SpanAttributeKey.CHAT_MESSAGES)  
    tools = chat_span.get_attribute(SpanAttributeKey.CHAT_TOOLS)  
      
    print(f"Chat messages: {messages}")  
    print(f"Available tools: {tools}")  
      
    # Access token usage from span  
    input_tokens = chat_span.get_attribute("llm.token_usage.input_tokens")  
    output_tokens = chat_span.get_attribute("llm.token_usage.output_tokens")  
    print(f"Span token usage - Input: {input_tokens}, Output: {output_tokens}")  
    

### Advanced span operationsâ

#### Convert spans to/from dictionariesâ

Python
    
    
    # Convert span to dictionary  
    span_dict = span.to_dict()  
    print(f"Span dict keys: {span_dict.keys()}")  
      
    # Recreate span from dictionary  
    from mlflow.entities import Span  
    reconstructed_span = Span.from_dict(span_dict)  
    print(f"Reconstructed span: {reconstructed_span.name}")  
    

#### Advanced span analysisâ

Python
    
    
    def analyze_span_tree(trace):  
        """Analyze the span hierarchy and relationships."""  
        spans = trace.data.spans  
      
        # Build parent-child relationships  
        span_dict = {span.span_id: span for span in spans}  
        children = {}  
      
        for span in spans:  
            if span.parent_id:  
                if span.parent_id not in children:  
                    children[span.parent_id] = []  
                children[span.parent_id].append(span)  
      
        # Find root spans  
        roots = [s for s in spans if s.parent_id is None]  
      
        def print_tree(span, indent=0):  
            duration_ms = (span.end_time_ns - span.start_time_ns) / 1_000_000  
            status_icon = "â" if span.status.status_code == SpanStatusCode.OK else "â"  
            print(f"{'  ' * indent}{status_icon} {span.name} ({span.span_type}) - {duration_ms:.1f}ms")  
      
            # Print children  
            for child in sorted(children.get(span.span_id, []),  
                              key=lambda s: s.start_time_ns):  
                print_tree(child, indent + 1)  
      
        print("Span Hierarchy:")  
        for root in roots:  
            print_tree(root)  
      
        # Calculate span statistics  
        total_time = sum((s.end_time_ns - s.start_time_ns) / 1_000_000  
                         for s in spans)  
        llm_time = sum((s.end_time_ns - s.start_time_ns) / 1_000_000  
                       for s in spans if s.span_type in [SpanType.LLM, SpanType.CHAT_MODEL])  
        retrieval_time = sum((s.end_time_ns - s.start_time_ns) / 1_000_000  
                            for s in spans if s.span_type == SpanType.RETRIEVER)  
      
        print(f"\nSpan Statistics:")  
        print(f"  Total spans: {len(spans)}")  
        print(f"  Total time: {total_time:.1f}ms")  
        print(f"  LLM time: {llm_time:.1f}ms ({llm_time/total_time*100:.1f}%)")  
        print(f"  Retrieval time: {retrieval_time:.1f}ms ({retrieval_time/total_time*100:.1f}%)")  
      
        # Find critical path (longest duration path from root to leaf)  
        def find_critical_path(span):  
            child_paths = []  
            for child in children.get(span.span_id, []):  
                path, duration = find_critical_path(child)  
                child_paths.append((path, duration))  
      
            span_duration = (span.end_time_ns - span.start_time_ns) / 1_000_000  
            if child_paths:  
                best_path, best_duration = max(child_paths, key=lambda x: x[1])  
                return [span] + best_path, span_duration + best_duration  
            else:  
                return [span], span_duration  
      
        if roots:  
            critical_paths = [find_critical_path(root) for root in roots]  
            critical_path, critical_duration = max(critical_paths, key=lambda x: x[1])  
      
            print(f"\nCritical Path ({critical_duration:.1f}ms total):")  
            for span in critical_path:  
                duration_ms = (span.end_time_ns - span.start_time_ns) / 1_000_000  
                print(f"  â {span.name} ({duration_ms:.1f}ms)")  
      
    # Use the analyzer  
    analyze_span_tree(trace)  
    

##  Request and response dataâ

Python
    
    
    # Get root span request/response (backward compatibility)  
    request_json = trace.data.request  
    response_json = trace.data.response  
      
    # Parse JSON strings  
    import json  
    if request_json:  
        request_data = json.loads(request_json)  
        print(f"Request: {request_data}")  
      
    if response_json:  
        response_data = json.loads(response_json)  
        print(f"Response: {response_data}")  
    

## Data export and conversionâ

### Convert to dictionaryâ

**API Reference:** [`Trace.to_dict`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace.to_dict>)

Python
    
    
    # Convert entire trace to dictionary  
    trace_dict = trace.to_dict()  
    print(f"Trace dict keys: {trace_dict.keys()}")  
    print(f"Info keys: {trace_dict['info'].keys()}")  
    print(f"Data keys: {trace_dict['data'].keys()}")  
      
    # Convert individual components  
    info_dict = trace.info.to_dict()  
    data_dict = trace.data.to_dict()  
      
    # Reconstruct trace from dictionary  
    from mlflow.entities import Trace  
    reconstructed_trace = Trace.from_dict(trace_dict)  
    print(f"Reconstructed trace ID: {reconstructed_trace.info.trace_id}")  
    

### JSON serializationâ

**API Reference:** [`Trace.to_json`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace.to_json>)

Python
    
    
    # Convert to JSON string  
    trace_json = trace.to_json()  
    print(f"JSON length: {len(trace_json)} characters")  
      
    # Pretty print JSON  
    trace_json_pretty = trace.to_json(pretty=True)  
    print("Pretty JSON (first 500 chars):")  
    print(trace_json_pretty[:500])  
      
    # Load trace from JSON  
    from mlflow.entities import Trace  
    loaded_trace = Trace.from_json(trace_json)  
    print(f"Loaded trace ID: {loaded_trace.info.trace_id}")  
    

### Pandas DataFrame conversionâ

**API Reference:** [`Trace.to_pandas_dataframe_row`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace.to_pandas_dataframe_row>)

Python
    
    
    # Convert trace to DataFrame row  
    row_data = trace.to_pandas_dataframe_row()  
    print(f"DataFrame row keys: {list(row_data.keys())}")  
      
    # Create DataFrame from multiple traces  
    import pandas as pd  
      
    # Get multiple traces  
    traces = mlflow.search_traces(max_results=5)  
      
    # If you have individual trace objects  
    trace_rows = [t.to_pandas_dataframe_row() for t in [trace]]  
    df = pd.DataFrame(trace_rows)  
      
    print(f"DataFrame shape: {df.shape}")  
    print(f"Columns: {df.columns.tolist()}")  
      
    # Access specific data from DataFrame  
    print(f"Trace IDs: {df['trace_id'].tolist()}")  
    print(f"States: {df['state'].tolist()}")  
    print(f"Durations: {df['execution_duration'].tolist()}")  
    

## Next stepsâ

  * [Examples: Analyzing traces](</aws/en/mlflow3/genai/tracing/observe-with-traces/analyze-traces>) \- Analyze traces for specific use cases.
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/span-tracing -->

On this page

Last updated on **Nov 26, 2025**

# Span tracing with context managers

Copy notebook link for import

Copy a link to the clipboard for importing this page as a notebook

Open notebook in new tab

Open a notebook containing all code in this page in a new tab

The [`mlflow.start_span()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.start_span>) context manager allows you to create spans for arbitrary code blocks. While [function decorators](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>) trace at the granularity of functions, `start_span()` can capture more fine-grained and complex interactions within your code.

Span tracing with context managers gives you fine-grained control over what code gets traced:

  * Arbitrary code blocks: Trace any code block, not just entire functions
  * Automatic context management: MLflow handles parent-child relationships and cleanup
  * Works with function decorators: Mix and match with `@mlflow.trace` for hybrid approaches
  * Exception handling: Automatic error capturing, similarly to function decorators



## Prerequisitesâ

This tutorial requires the following packages:

  * `mlflow[databricks]` 3.1 and above: Core MLflow functionality with GenAI features and Databricks connectivity.
  * `openai` 1.0.0 and above: The example app below uses the OpenAI client. In your own code, replace this with other SDKs as needed.



Install the basic requirements:

Python
    
    
    %pip install --upgrade "mlflow[databricks]>=3.1" "openai>=1.0.0"  
      
    dbutils.library.restartPython()  
    

### Prerequisites for MLflow 2â

Databricks strongly recommends installing MLflow 3.1 or newer if using `mlflow[databricks]`.

For MLflow 2, span tracing with context managers requires the following packages:

  * `mlflow[databricks]` 2.15.0 and above: Core MLflow functionality with Databricks connectivity.
  * `openai` 1.0.0 and above: (Optional) Install if your custom code uses the OpenAI client.



Python
    
    
    %pip install --upgrade "mlflow[databricks]>=2.15.0,<3.0.0"  
    pip install --upgrade openai>=1.0.0 # Install if needed  
    dbutils.library.restartPython()  
    

## Span tracing APIâ

Similarly to the function decorator, the context manager automatically captures parent-child relationship, exceptions, and execution time. It is compatible with [automatic tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>) as well.

Unlike with the function decorator, the name, inputs, and outputs of the span must be provided manually. You can set them using the [`LiveSpan`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.LiveSpan>) object that is returned from the context manager.

The code snippet below illustrates basic span tracing:

Python
    
    
    import mlflow  
      
    with mlflow.start_span(name="my_span") as span:  
        x = 1  
        y = 2  
        span.set_inputs({"x":x, "y": y})  
        z = x + y  
        span.set_outputs(z)  
    

### Span eventsâ

[`SpanEvent` objects](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanEvent>) record specific occurrences during a span's lifetime. The code snippet below shows:

  * Creating an event with the current timestamp
  * Creating an event with a specific timestamp (nanoseconds)
  * Creating an event from an `Exception`



Python
    
    
    import mlflow  
    from mlflow.entities import SpanEvent, SpanType  
    import time  
      
    with mlflow.start_span(name="manual_span", span_type=SpanType.CHAIN) as span:  
        # Create an event with current timestamp  
        event = SpanEvent(  
            name="validation_completed",  
            attributes={  
                "records_validated": 1000,  
                "errors_found": 3,  
                "validation_type": "schema"  
            }  
        )  
        span.add_event(event)  
      
        # Create an event with specific timestamp (nanoseconds)  
        specific_time_event = SpanEvent(  
            name="data_checkpoint",  
            timestamp=int(time.time() * 1e9),  
            attributes={"checkpoint_id": "ckpt_123"}  
        )  
        span.add_event(specific_time_event)  
      
        # Create an event from an exception  
        try:  
            raise ValueError("Invalid input format")  
        except Exception as e:  
            error_event = SpanEvent.from_exception(e)  
            # This creates an event with name="exception" and attributes containing:  
            # - exception.message  
            # - exception.type  
            # - exception.stacktrace  
      
            # Add to current span  
            span = mlflow.get_current_active_span()  
            span.add_event(error_event)  
    

### Span statusâ

[`SpanStatus`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanStatus>) defines the status of a span. Note that the `mlflow.start_span()` context manager overwrites the status upon exit. The code snippet below shows various ways to set status on spans:

Python
    
    
    import mlflow  
    from mlflow.entities import SpanStatus, SpanStatusCode, SpanType  
      
    with mlflow.start_span(name="manual_span", span_type=SpanType.CHAIN) as span:  
      
        # Create status objects  
        success_status = SpanStatus(SpanStatusCode.OK)  
        error_status = SpanStatus(  
            SpanStatusCode.ERROR,  
            description="Failed to connect to database"  
        )  
      
        # Set status on a live span  
        span.set_status(success_status)  
      
        # Or use string shortcuts  
        span.set_status("OK")  
        span.set_status("ERROR")  
      
        # When the context manager exits successfully, the status is overwritten with status "OK"  
    

Query status from completed spans:

Python
    
    
    last_trace_id = mlflow.get_last_active_trace_id()  
    trace = mlflow.get_trace(last_trace_id)  
      
    for span in trace.data.spans:  
        print(span.status.status_code)  
    

### `RETRIEVER` spansâ

Use [`RETRIEVER` spans](<https://mlflow.org/docs/latest/genai/concepts/span/#retriever-spans>) when retrieving documents from a data store. `RETRIEVER` spans must output a list of `Documents` as shown in the following example:

Python
    
    
    import mlflow  
    from mlflow.entities import Document, SpanType  
      
    @mlflow.trace(span_type=SpanType.RETRIEVER)  
    def retrieve_documents(query: str):  
        span = mlflow.get_current_active_span()  
      
        # Create Document objects (required for RETRIEVER spans)  
        documents = [  
            Document(  
                page_content="The content of the document...",  
                metadata={  
                    "doc_uri": "path/to/document.md",  
                    "chunk_id": "chunk_001",  
                    "relevance_score": 0.95,  
                    "source": "knowledge_base"  
                },  
                id="doc_123"  # Optional document ID  
            ),  
            Document(  
                page_content="Another relevant section...",  
                metadata={  
                    "doc_uri": "path/to/other.md",  
                    "chunk_id": "chunk_042",  
                    "relevance_score": 0.87  
                }  
            )  
        ]  
      
        # Set outputs as Document objects for proper UI rendering  
        span.set_outputs(documents)  
      
        # Return in your preferred format  
        return [doc.to_dict() for doc in documents]  
      
    retrieve_documents(query="What is ML?")  
    

Access retriever outputs:

Python
    
    
    last_trace_id = mlflow.get_last_active_trace_id()  
    trace = mlflow.get_trace(last_trace_id)  
      
    retriever_span = trace.search_spans(span_type=SpanType.RETRIEVER)[0]  
      
    if retriever_span.outputs:  
        for doc in retriever_span.outputs:  
            if isinstance(doc, dict):  
                content = doc.get('page_content', '')  
                uri = doc.get('metadata', {}).get('doc_uri', '')  
                score = doc.get('metadata', {}).get('relevance_score', 0)  
                print(f"Document from {uri} (score: {score})")  
    

## Advanced exampleâ

Below is a more complex example that combines:

  * [`mlflow.start_span()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.start_span>) context manager
  * `@mlflow.trace` function decorator
  * Auto-tracing for OpenAI



Python
    
    
    from databricks_openai import DatabricksOpenAI  
    import mlflow  
    from mlflow.entities import SpanEvent, SpanType  
    import openai  
    import time  
      
    # Enable auto-tracing for OpenAI  
    mlflow.openai.autolog()  
      
    # Create an OpenAI client that is connected to Databricks-hosted LLMs.  
    client = DatabricksOpenAI()  
      
    @mlflow.trace(span_type=SpanType.CHAIN)  
    def chat_iteration(messages, user_input):  
        with mlflow.start_span(name="User", span_type=SpanType.CHAIN) as span:  
            span.set_inputs({  
                "messages": messages,  
                "timestamp": time.time(),  
            })  
      
            # Set individual attribute  
            span.set_attribute("messages_length", len(messages))  
      
            # Set multiple attributes at once  
            span.set_attributes({  
                "environment": "production",  
                "custom_metadata": {"key": "value"}  
            })  
      
            # Add events during execution  
            span.add_event(SpanEvent(  
                name="processing_started",  
                attributes={  
                    "stage": "initialization",  
                    "memory_usage_mb": 256,  
                }  
            ))  
      
            span.set_outputs(user_input)  
      
        messages.append({"role": "user", "content": user_input})  
      
        response = client.chat.completions.create(  
            model="databricks-claude-sonnet-4-5",  
            max_tokens=100,  
            messages=messages,  
        )  
        answer = response.choices[0].message.content  
        print(f"Assistant: {answer}")  
      
        messages.append({"role": "assistant", "content": answer})  
      
      
    chat_iteration(  
        messages = [{"role": "system", "content": "You are a friendly chat bot"}],  
        user_input="What is your favorite color?",  
    )  
    

To see an example of nested tracing for longer conversations, uncomment the example below:

Python
    
    
    # @mlflow.trace(span_type=SpanType.CHAIN)  
    # def start_session():  
    #     messages = [{"role": "system", "content": "You are a friendly chat bot"}]  
    #     while True:  
    #         user_input = input(">> ")  
    #         chat_iteration(messages, user_input)  
      
    #         if user_input == "BYE":  
    #             break  
      
      
    # start_session()  
    

## Next stepsâ

  * [Function decorators](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>) \- Simpler approach for tracing entire functions
  * [Low-level client APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/low-level-api>) \- Learn advanced scenarios requiring full control
  * [Debug and analyze your app](</aws/en/mlflow3/genai/tracing/observe-with-traces/>) \- Query and analyze logged traces



## Example notebookâ

#### Span tracing with context managers

[Open notebook in new tab](<https://docs.databricks.com/aws/en/notebooks/source/mlflow3/genai/tracing/app-instrumentation/manual-tracing/span-tracing.html>)

Copy link for import

Copy to clipboard
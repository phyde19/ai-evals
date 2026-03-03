<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/haystack -->

On this page

Last updated on **Nov 6, 2025**

# Tracing Haystack

[Haystack](<https://haystack.deepset.ai/>) is an open-source AI orchestration framework for building production-ready LLM applications, semantic search systems, and question-answering systems.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) provides automatic tracing capability for Haystack. You can enable tracing for Haystack by calling the [`mlflow.haystack.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.haystack.html#mlflow.haystack.autolog>) function, and traces are automatically logged to the active MLflow Experiment upon invocation of pipelines and components.

Python
    
    
    import mlflow  
      
    mlflow.haystack.autolog()  
    

MLflow trace automatically captures the following information about Haystack pipeline runs:

  * Pipelines and components
  * Latencies
  * Component metadata
  * Token usage and cost
  * Cache hit information
  * Any exception if raised



note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call `mlflow.haystack.autolog()` to enable automatic tracing for this integration.

## Prerequisitesâ

To use MLflow Tracing with Haystack, you need to install MLflow and the Haystack packages.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and Haystack packages:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" haystack-ai  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and Haystack packages:

Bash
    
    
    pip install --upgrade mlflow-tracing haystack-ai  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is highly recommended for the best tracing experience with Haystack.

Before running the examples, you'll need to configure your environment:

**For users outside Databricks notebooks** : Set your Databricks environment variables:

Bash
    
    
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"  
    export DATABRICKS_TOKEN="your-personal-access-token"  
    

**For users inside Databricks notebooks** : These credentials are automatically set for you.

**API Keys** : Ensure your LLM provider API keys are configured. For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values for secure API key management.

Bash
    
    
    export OPENAI_API_KEY="your-openai-api-key"  
    # Add other provider keys as needed  
    

## Example Usageâ

The following example demonstrates how to use Haystack with MLflow tracing. This example creates a simple RAG (Retrieval-Augmented Generation) pipeline with a retriever, prompt builder, and LLM.

Python
    
    
    import mlflow  
    import os  
      
    from haystack import Pipeline  
    from haystack.components.builders import PromptBuilder  
    from haystack.components.generators import OpenAIGenerator  
    from haystack.components.retrievers.in_memory import InMemoryBM25Retriever  
    from haystack.document_stores.in_memory import InMemoryDocumentStore  
    from haystack import Document  
      
    # Ensure your OPENAI_API_KEY is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key" # Uncomment and set if not globally configured  
      
    # Enable auto tracing for Haystack  
    mlflow.haystack.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/haystack-tracing-demo")  
      
    # Create a simple document store with sample documents  
    document_store = InMemoryDocumentStore()  
    document_store.write_documents([  
        Document(content="Paris is the capital of France."),  
        Document(content="Berlin is the capital of Germany."),  
        Document(content="Rome is the capital of Italy."),  
    ])  
      
    # Build a simple RAG pipeline  
    template = """  
    Given the following documents, answer the question.  
      
    Documents:  
    {% for doc in documents %}  
      {{ doc.content }}  
    {% endfor %}  
      
    Question: {{ question }}  
    Answer:  
    """  
      
    pipe = Pipeline()  
    pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))  
    pipe.add_component("prompt_builder", PromptBuilder(template=template))  
    pipe.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))  
      
    pipe.connect("retriever", "prompt_builder.documents")  
    pipe.connect("prompt_builder", "llm")  
      
    # Run the pipeline - trace will be automatically logged  
    result = pipe.run({  
        "retriever": {"query": "What is the capital of France?"},  
        "prompt_builder": {"question": "What is the capital of France?"}  
    })  
      
    print(result["llm"]["replies"][0])  
    

warning

For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values for secure API key management.

## Token Usage Trackingâ

MLflow automatically tracks token usage for Haystack pipelines when using MLflow version 3.4.0 or later. Token usage information includes input tokens, output tokens, and total tokens consumed during pipeline execution.

Python
    
    
    import mlflow  
      
    mlflow.haystack.autolog()  
      
    from haystack import Pipeline  
    from haystack.components.generators import OpenAIGenerator  
      
    # Create and run a pipeline  
    pipe = Pipeline()  
    pipe.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))  
      
    # Run the pipeline and retrieve trace information  
    with mlflow.start_span(name="haystack_pipeline_run") as span:  
        result = pipe.run({"llm": {"prompt": "What is the capital of France?"}})  
        print(result["llm"]["replies"][0])  
      
    # Token usage is automatically logged and visible in the MLflow UI  
    trace_info = mlflow.get_last_active_trace()  
    print(f"Trace ID: {trace_info.request_id}")  
    

Token usage details are displayed in the MLflow tracing UI, allowing you to monitor and optimize your pipeline's performance and costs.

## Disable auto-tracingâ

Auto tracing for Haystack can be disabled globally by calling `mlflow.haystack.autolog(disable=True)` or `mlflow.autolog(disable=True)`.
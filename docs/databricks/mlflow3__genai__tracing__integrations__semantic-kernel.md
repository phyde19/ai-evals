<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/semantic-kernel -->

On this page

Last updated on **Aug 18, 2025**

# Tracing Semantic Kernel

[Semantic Kernel](<https://learn.microsoft.com/en-us/semantic-kernel/overview/>) is a lightweight, open source SDK that acts as AI middleware for C#, Python, and Java. It abstracts model interactions and composes prompts, functions, and plugins across providers.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) integrates with Semantic Kernel to automatically instrument kernel callbacks and capture comprehensive execution traces. No changes to your app logic are requiredâenable it with [`mlflow.semantic_kernel.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.semantic_kernel.html#mlflow.semantic_kernel.autolog>).

The integration provides a complete view of:

  * Prompts and completion responses
  * Chat history and messages
  * Latencies
  * Model name and provider
  * Kernel functions and plugins
  * Template variables and arguments
  * Token usage information
  * Any exceptions if raised



note

Streaming is not currently traced.

## Prerequisitesâ

To use MLflow Tracing with Semantic Kernel, you need to install MLflow and the relevant Semantic Kernel packages.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and Semantic Kernel:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" semantic_kernel openai  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and Semantic Kernel:

Bash
    
    
    pip install --upgrade mlflow-tracing semantic_kernel openai  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is recommended for the best tracing experience.

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
    

## Example usageâ

Semantic Kernel primarily uses async patterns. In notebooks, you can `await` directly; in scripts, wrap with `asyncio.run()`.

Python
    
    
    import mlflow  
      
    mlflow.semantic_kernel.autolog()  
    

note

On serverless compute clusters, autologging for genAI tracing frameworks is not automatically enabled. You must explicitly enable autologging by calling the appropriate `mlflow.<library>.autolog()` function for the specific integrations you want to trace.

Python
    
    
    import openai  
    from semantic_kernel import Kernel  
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion  
      
    openai_client = openai.AsyncOpenAI()  
      
    kernel = Kernel()  
    kernel.add_service(  
        OpenAIChatCompletion(  
            service_id="chat-gpt",  
            ai_model_id="gpt-4o-mini",  
            async_client=openai_client,  
        )  
    )  
      
    answer = await kernel.invoke_prompt("Is sushi the best food ever?")  
    print("AI says:", answer)  
    

## Token usage trackingâ

MLflow 3.2.0+ records token usage per LLM call and aggregates totals in the trace info.

Python
    
    
    import mlflow  
      
    last_trace_id = mlflow.get_last_active_trace_id()  
    trace = mlflow.get_trace(trace_id=last_trace_id)  
      
    print(trace.info.token_usage)  
    for span in trace.data.spans:  
        usage = span.get_attribute("mlflow.chat.tokenUsage")  
        if usage:  
            print(span.name, usage)  
    

## Disable auto-tracingâ

Disable Semantic Kernel auto-tracing with [`mlflow.semantic_kernel.autolog(disable=True)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.semantic_kernel.html#mlflow.semantic_kernel.autolog>) or disable all with [`mlflow.autolog(disable=True)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.autolog>).
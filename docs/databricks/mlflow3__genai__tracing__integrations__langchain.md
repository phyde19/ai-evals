<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/langchain -->

On this page

Last updated on **Aug 11, 2025**

# Tracing LangChain

[LangChain](<https://www.langchain.com/>) is an open-source framework for building LLM-powered applications.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) provides automatic tracing capability for LangChain. You can enable tracing for LangChain by calling the [`mlflow.langchain.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.langchain.html#mlflow.langchain.autolog>) function, and nested traces are automatically logged to the active MLflow Experiment upon invocation of chains.

Python
    
    
    import mlflow  
      
    mlflow.langchain.autolog()  
    

note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call `mlflow.langchain.autolog()` to enable automatic tracing for this integration.

## Prerequisitesâ

To use MLflow Tracing with LangChain, you need to install MLflow and the relevant LangChain packages (e.g., `langchain`, `langchain-openai`).

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and LangChain packages:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" langchain langchain-openai  
    # Add other langchain community/core packages if needed  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and LangChain packages:

Bash
    
    
    pip install --upgrade mlflow-tracing langchain langchain-openai  
    # Add other langchain community/core packages if needed  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is highly recommended for the best tracing experience with LangChain. Check the example below for specific compatible versions of LangChain packages if you encounter issues.

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
    

### Example Usageâ

Python
    
    
    import mlflow  
    import os  
      
    from langchain.prompts import PromptTemplate  
    from langchain_core.output_parsers import StrOutputParser  
    from langchain_openai import ChatOpenAI  
      
    # Ensure your OPENAI_API_KEY (or other LLM provider keys) is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key" # Uncomment and set if not globally configured  
      
    # Enabling autolog for LangChain will enable trace logging.  
    mlflow.langchain.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/langchain-tracing-demo")  
      
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=1000)  
      
    prompt_template = PromptTemplate.from_template(  
        "Answer the question as if you are {person}, fully embodying their style, wit, personality, and habits of speech. "  
        "Emulate their quirks and mannerisms to the best of your ability, embracing their traitsâeven if they aren't entirely "  
        "constructive or inoffensive. The question is: {question}"  
    )  
      
    chain = prompt_template | llm | StrOutputParser()  
      
    # Let's test another call  
    chain.invoke(  
        {  
            "person": "Linus Torvalds",  
            "question": "Can I just set everyone's access to sudo to make things easier?",  
        }  
    )  
    

note

This example above has been confirmed working with the following requirement versions:

Shell
    
    
    pip install openai==1.30.5 langchain==0.2.1 langchain-openai==0.1.8 langchain-community==0.2.1 mlflow==2.14.0 tiktoken==0.7.0  
    

warning

For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values for secure API key management.

### Supported APIsâ

The following APIs are supported by auto tracing for LangChain.

  * `invoke`
  * `batch`
  * `stream`
  * `ainvoke`
  * `abatch`
  * `astream`
  * `get_relevant_documents` (for retrievers)
  * `__call__` (for Chains and AgentExecutors)



### Customize Tracing Behaviorâ

Sometimes you may want to customize what information is logged in the traces. You can achieve this by creating a custom callback handler that inherits from [`mlflow.langchain.langchain_tracer.MlflowLangchainTracer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.langchain.html>). MlflowLangchainTracer is a callback handler that is injected into the langchain model inference process to log traces automatically. It starts a new span upon a set of actions of the chain such as on_chain_start, on_llm_start, and concludes it when the action is finished. Various metadata such as span type, action name, input, output, latency, are automatically recorded to the span.

The following example demonstrates how to record an additional attribute to the span when a chat model starts running.

Python
    
    
    from mlflow.langchain.langchain_tracer import MlflowLangchainTracer  
      
      
    class CustomLangchainTracer(MlflowLangchainTracer):  
        # Override the handler functions to customize the behavior. The method signature is defined by LangChain Callbacks.  
        def on_chat_model_start(  
            self,  
            serialized: Dict[str, Any],  
            messages: List[List[BaseMessage]],  
            *,  
            run_id: UUID,  
            tags: Optional[List[str]] = None,  
            parent_run_id: Optional[UUID] = None,  
            metadata: Optional[Dict[str, Any]] = None,  
            name: Optional[str] = None,  
            **kwargs: Any,  
        ):  
            """Run when a chat model starts running."""  
            attributes = {  
                **kwargs,  
                **metadata,  
                # Add additional attribute to the span  
                "version": "1.0.0",  
            }  
      
            # Call the _start_span method at the end of the handler function to start a new span.  
            self._start_span(  
                span_name=name or self._assign_span_name(serialized, "chat model"),  
                parent_run_id=parent_run_id,  
                span_type=SpanType.CHAT_MODEL,  
                run_id=run_id,  
                inputs=messages,  
                attributes=kwargs,  
            )  
    

### Disable auto-tracingâ

Auto tracing for LangChain can be disabled globally by calling `mlflow.langchain.autolog(disable=True)` or `mlflow.autolog(disable=True)`.
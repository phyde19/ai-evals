<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/ag2 -->

On this page

Last updated on **Aug 18, 2025**

# Tracing AG2

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) integrates with [AG2](<https://github.com/ag2ai/ag2>) (formerly AutoGen 0.2) to capture unified traces of multiagent conversations and workflows. The integration automatically instruments agent loops and tool executionâjust call [`mlflow.ag2.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.ag2.html#mlflow.ag2.autolog>).

Python
    
    
    import mlflow  
      
    mlflow.ag2.autolog()  
    

note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call `mlflow.ag2.autolog()` to enable automatic tracing for this integration.

The integration provides comprehensive visibility into:

  * Which agent is called at different turns
  * Messages passed between agents
  * LLM and tool calls made by each agent, organized per an agent and a turn
  * Latencies
  * Any exception if raised



## Prerequisitesâ

To use MLflow Tracing with AG2, you need to install MLflow and the relevant AG2 (AutoGen) packages.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and AutoGen:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" pyautogen  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and AutoGen:

Bash
    
    
    pip install --upgrade mlflow-tracing pyautogen  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is recommended for the best tracing experience with AG2.

Before running the examples, you'll need to configure your environment:

**For users outside Databricks notebooks** : Set your Databricks environment variables:

Bash
    
    
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"  
    export DATABRICKS_TOKEN="your-personal-access-token"  
    

**For users inside Databricks notebooks** : These credentials are automatically set for you.

## Basic exampleâ

Python
    
    
    import os  
    from typing import Annotated, Literal  
      
    from autogen import ConversableAgent  
    import mlflow  
      
    # Enable auto-tracing for AG2  
    mlflow.ag2.autolog()  
      
    # Track to Databricks (optional if already configured)  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/ag2-tracing-demo")  
      
    # Define a simple multi-agent workflow using AG2 (AutoGen 0.2)  
    config_list = [  
        {  
            "model": "gpt-4o-mini",  
            # Requires OPENAI_API_KEY in env for this example  
            "api_key": os.environ.get("OPENAI_API_KEY"),  
        }  
    ]  
      
    Operator = Literal["+", "-", "*", "/"]  
      
      
    def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:  
        if operator == "+":  
            return a + b  
        elif operator == "-":  
            return a - b  
        elif operator == "*":  
            return a * b  
        elif operator == "/":  
            return int(a / b)  
        else:  
            raise ValueError("Invalid operator")  
      
      
    assistant = ConversableAgent(  
        name="Assistant",  
        system_message=(  
            "You are a helpful AI assistant. You can help with simple calculations. "  
            "Return 'TERMINATE' when the task is done."  
        ),  
        llm_config={"config_list": config_list},  
    )  
      
    user_proxy = ConversableAgent(  
        name="Tool Agent",  
        llm_config=False,  
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],  
        human_input_mode="NEVER",  
    )  
      
    assistant.register_for_llm(name="calculator", description="A simple calculator")(calculator)  
    user_proxy.register_for_execution(name="calculator")(calculator)  
      
    response = user_proxy.initiate_chat(  
        assistant, message="What is (44231 + 13312 / (230 - 20)) * 4?"  
    )  
    

## Track token usageâ

MLflow 3.2.0+ supports token usage tracking for AG2. Perâcall usage is recorded in the `mlflow.chat.tokenUsage` span attribute; total usage appears in the trace info.

Python
    
    
    import mlflow  
      
    last_trace_id = mlflow.get_last_active_trace_id()  
    trace = mlflow.get_trace(trace_id=last_trace_id)  
      
    total = trace.info.token_usage  
    print("Input:", total["input_tokens"], "Output:", total["output_tokens"], "Total:", total["total_tokens"])  
      
    for span in trace.data.spans:  
        usage = span.get_attribute("mlflow.chat.tokenUsage")  
        if usage:  
            print(span.name, usage)  
    

## Disable auto-tracingâ

Disable AG2 auto-tracing with [`mlflow.ag2.autolog(disable=True)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.ag2.html#mlflow.ag2.autolog>) or disable all autologging with [`mlflow.autolog(disable=True)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.autolog>).
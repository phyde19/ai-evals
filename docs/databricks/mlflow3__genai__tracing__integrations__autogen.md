<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/autogen -->

On this page

Last updated on **Aug 11, 2025**

# Tracing AutoGen

[AutoGen](<https://microsoft.github.io/autogen/0.2/>) is an open-source framework for building event-driven, distributed, scalable, and resilient AI agent systems.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) provides automatic tracing capability for AutoGen, an open-source multi-agent framework. By enabling auto tracing for AutoGen by calling the [`mlflow.autogen.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.autogen.html#mlflow.autogen.autolog>) function, MLflow will capture nested traces and log them to the active MLflow Experiment upon agents execution.

Python
    
    
    import mlflow  
      
    mlflow.autogen.autolog()  
    

MLflow captures the following information about the multi-agent execution:

  * Which agent is called at different turns
  * Messages passed between agents
  * LLM and tool calls made by each agent, organized per an agent and a turn
  * Latencies
  * Any exception if raised



note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call `mlflow.autogen.autolog()` to enable automatic tracing for this integration.

## Prerequisitesâ

To use MLflow Tracing with AutoGen, you need to install MLflow and the `pyautogen` library.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and `pyautogen`:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" pyautogen  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and `pyautogen`:

Bash
    
    
    pip install --upgrade mlflow-tracing pyautogen  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is highly recommended for the best tracing experience with AutoGen.

Before running the examples, you'll need to configure your environment:

**For users outside Databricks notebooks** : Set your Databricks environment variables:

Bash
    
    
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"  
    export DATABRICKS_TOKEN="your-personal-access-token"  
    

**For users inside Databricks notebooks** : These credentials are automatically set for you.

**OpenAI API key** : Ensure your API key is configured. For production use, we recommend using [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of environment variables:

Bash
    
    
    export OPENAI_API_KEY="your-openai-api-key"  
    

### Basic Exampleâ

Python
    
    
    import os  
    from typing import Annotated, Literal  
      
    from autogen import ConversableAgent  
      
    import mlflow  
      
    # Ensure your OPENAI_API_KEY (or other LLM provider keys) is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key" # Uncomment and set if not globally configured  
      
    # Turn on auto tracing for AutoGen  
    mlflow.autogen.autolog()  
      
    # Set up MLflow tracking on Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/autogen-tracing-demo")  
      
      
    # Define a simple multi-agent workflow using AutoGen  
    config_list = [  
        {  
            "model": "gpt-4o-mini",  
            # Please set your OpenAI API Key to the OPENAI_API_KEY env var before running this example  
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
      
      
    # First define the assistant agent that suggests tool calls.  
    assistant = ConversableAgent(  
        name="Assistant",  
        system_message="You are a helpful AI assistant. "  
        "You can help with simple calculations. "  
        "Return 'TERMINATE' when the task is done.",  
        llm_config={"config_list": config_list},  
    )  
      
    # The user proxy agent is used for interacting with the assistant agent  
    # and executes tool calls.  
    user_proxy = ConversableAgent(  
        name="Tool Agent",  
        llm_config=False,  
        is_termination_msg=lambda msg: msg.get("content") is not None  
        and "TERMINATE" in msg["content"],  
        human_input_mode="NEVER",  
    )  
      
    # Register the tool signature with the assistant agent.  
    assistant.register_for_llm(name="calculator", description="A simple calculator")(  
        calculator  
    )  
    user_proxy.register_for_execution(name="calculator")(calculator)  
    response = user_proxy.initiate_chat(  
        assistant, message="What is (44231 + 13312 / (230 - 20)) * 4?"  
    )  
    

warning

For production environments, always use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values.

### Disable auto-tracingâ

Auto tracing for AutoGen can be disabled globally by calling `mlflow.autogen.autolog(disable=True)` or `mlflow.autolog(disable=True)`.
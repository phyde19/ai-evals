<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/strands -->

On this page

Last updated on **Nov 6, 2025**

# Tracing Strands Agents SDK

[Strands Agents SDK](<https://github.com/awslabs/agents-strands>) is an open-source SDK by AWS for creating autonomous AI agents that can interact with external tools and APIs.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) provides automatic tracing capability for Strands Agents SDK. By enabling auto tracing for Strands by calling the [`mlflow.strands.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.strands.html#mlflow.strands.autolog>) function, MLflow will capture traces and log them to the active MLflow Experiment upon invocation of agents.

Python
    
    
    import mlflow  
      
    mlflow.strands.autolog()  
    

MLflow trace automatically captures the following information about Strands agent calls:

  * Prompts and responses
  * Latencies
  * Agent metadata
  * Token usage and cost
  * Cache hit information
  * Any exception if raised



note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call `mlflow.strands.autolog()` to enable automatic tracing for this integration.

## Prerequisitesâ

To use MLflow Tracing with Strands Agents SDK, you need to install MLflow, the Strands SDK, and the required dependencies.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and Strands packages:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" strands strands-tools  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and Strands packages:

Bash
    
    
    pip install --upgrade mlflow-tracing strands strands-tools  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is highly recommended for the best tracing experience with Strands Agents SDK.

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

The following example demonstrates how to use Strands Agents SDK with MLflow tracing. The agent uses the OpenAI model and has access to a calculator tool for performing arithmetic operations.

Python
    
    
    import mlflow  
    import os  
      
    # Ensure your OPENAI_API_KEY is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key" # Uncomment and set if not globally configured  
      
    # Enable auto tracing for Strands Agents SDK  
    mlflow.strands.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/strands-agent-demo")  
      
    from strands import Agent  
    from strands.models.openai import OpenAIModel  
    from strands_tools import calculator  
      
    # Configure the OpenAI model  
    model = OpenAIModel(  
        client_args={"api_key": os.environ.get("OPENAI_API_KEY")},  
        model_id="gpt-4o",  
        params={  
            "max_tokens": 2000,  
            "temperature": 0.7,  
        },  
    )  
      
    # Create an agent with the calculator tool  
    agent = Agent(model=model, tools=[calculator])  
      
    # Run the agent  
    response = agent("What is 2+2?")  
    print(response)  
    

warning

For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values for secure API key management.

## Token Usage Trackingâ

MLflow automatically tracks token usage for Strands agents when using MLflow version 3.4.0 or later. Token usage information includes input tokens, output tokens, and total tokens consumed during agent execution.

Python
    
    
    import mlflow  
      
    mlflow.strands.autolog()  
      
    from strands import Agent  
    from strands.models.openai import OpenAIModel  
    from strands_tools import calculator  
      
    model = OpenAIModel(  
        client_args={"api_key": os.environ.get("OPENAI_API_KEY")},  
        model_id="gpt-4o",  
        params={  
            "max_tokens": 2000,  
            "temperature": 0.7,  
        },  
    )  
      
    agent = Agent(model=model, tools=[calculator])  
      
    # Run the agent and retrieve trace information  
    with mlflow.start_span(name="strands_agent_run") as span:  
        response = agent("Calculate the sum of 15 and 27")  
        print(response)  
      
    # Token usage is automatically logged and visible in the MLflow UI  
    trace_info = mlflow.get_last_active_trace()  
    print(f"Trace ID: {trace_info.request_id}")  
    

Token usage details are displayed in the MLflow tracing UI, allowing you to monitor and optimize your agent's performance and costs.

## Disable auto-tracingâ

Auto tracing for Strands Agents SDK can be disabled globally by calling `mlflow.strands.autolog(disable=True)` or `mlflow.autolog(disable=True)`.
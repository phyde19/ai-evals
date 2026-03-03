<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/swarm -->

On this page

Last updated on **Aug 11, 2025**

# Tracing OpenAI Swarm

warning

OpenAI Swarm integration has been deprecated because the library is being replaced by the new [OpenAI Agents SDK](</aws/en/mlflow3/genai/tracing/integrations/openai-agent>). Please consider migrating to the new SDK for the latest features and support.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) provides automatic tracing capability for [OpenAI Swarm](<https://github.com/openai/swarm>), a multi-agent framework developed by OpenAI. By enabling auto tracing for OpenAI by calling the [`mlflow.openai.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.openai.html#mlflow.openai.autolog>) function, MLflow will capture nested traces and log them to the active MLflow Experiment upon invocation of OpenAI SDK.

Python
    
    
    import mlflow  
      
    mlflow.openai.autolog()  
    

note

On serverless compute clusters, autologging for genAI tracing frameworks is not automatically enabled. You must explicitly enable autologging by calling the appropriate `mlflow.<library>.autolog()` function for the specific integrations you want to trace.

In addition to the basic LLM call tracing for OpenAI, MLflow captures the intermediate steps that the Swarm agent operates and all tool-calling by the agent.

## Prerequisitesâ

To use MLflow Tracing with OpenAI Swarm, you need to install MLflow, the OpenAI SDK, and the `openai-swarm` library.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras, `openai`, and `openai-swarm`:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" openai openai-swarm  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing`, `openai`, and `openai-swarm`:

Bash
    
    
    pip install --upgrade mlflow-tracing openai openai-swarm  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is highly recommended. Note that OpenAI Swarm itself has been deprecated in favor of the OpenAI Agents SDK.

Before running the examples, you'll need to configure your environment:

**For users outside Databricks notebooks** : Set your Databricks environment variables:

Bash
    
    
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"  
    export DATABRICKS_TOKEN="your-personal-access-token"  
    

**For users inside Databricks notebooks** : These credentials are automatically set for you.

**API Keys** : Ensure your OpenAI API key is configured. For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values for secure API key management.

Bash
    
    
    export OPENAI_API_KEY="your-openai-api-key"  
    

### Basic Exampleâ

Python
    
    
    import mlflow  
    from swarm import Swarm, Agent  
    import os  
      
    # Ensure your OPENAI_API_KEY is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key" # Uncomment and set if not globally configured  
      
    # Calling the autolog API will enable trace logging by default.  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/openai-swarm-demo")  
      
    # Define a simple multi-agent workflow using OpenAI Swarm  
    client = Swarm()  
      
      
    def transfer_to_agent_b():  
        return agent_b  
      
      
    agent_a = Agent(  
        name="Agent A",  
        instructions="You are a helpful agent.",  
        functions=[transfer_to_agent_b],  
    )  
      
    agent_b = Agent(  
        name="Agent B",  
        instructions="Only speak in Haikus.",  
    )  
      
    response = client.run(  
        agent=agent_a,  
        messages=[{"role": "user", "content": "I want to talk to agent B."}],  
    )  
    

warning

For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) instead of hardcoded values for secure API key management.

### Disable auto-tracingâ

Auto tracing for OpenAI Swarm can be disabled globally by calling `mlflow.openai.autolog(disable=True)` or `mlflow.autolog(disable=True)`.

## Next stepsâ

  * [Understand tracing concepts](</aws/en/mlflow3/genai/tracing/tracing-101>) \- Learn how MLflow captures and organizes multi-agent trace data
  * [Debug and observe your app](</aws/en/mlflow3/genai/tracing/observe-with-traces/>) \- Use the Trace UI to analyze your multi-agent application's behavior
  * [Evaluate your app's quality](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) \- Set up quality assessment for your agent-based application
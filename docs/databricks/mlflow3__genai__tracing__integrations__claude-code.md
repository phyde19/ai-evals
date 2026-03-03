<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/claude-code -->

On this page

Last updated on **Feb 2, 2025**

# Tracing Claude Code

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) automatically traces Claude Code conversations and agents authored using Claude Agent SDK, capturing user prompts, AI responses, tool usage, timing, and session metadata.

MLflow supports two approaches for Claude Code tracing:

  * **CLI tracing** : Configure tracing through the MLflow CLI to automatically trace interactive Claude Code sessions (MLflow 3.4+)
  * **SDK tracing** : Enable tracing programmatically for Python applications using the Claude Agent SDK (MLflow 3.5+)



## Requirementsâ

  * SDK tracing
  * CLI tracing



Claude Agent SDK tracing requires:

  * [Claude Agent SDK](<https://docs.claude.com/en/api/agent-sdk/overview>) 0.1.0 or later
  * MLflow 3.5 or later with Databricks extras



Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.5" "claude-agent>=0.1.0"  
    

Claude Code CLI tracing requires:

  * [Claude Code CLI](<https://claude.com/product/claude-code>)
  * MLflow 3.4 or later with Databricks extras



Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.4"  
    

## Trace Claude Code to Databricksâ

  * SDK tracing
  * CLI tracing



  1. Set Databricks and Anthropic environment variables:

Bash
         
         export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"  
         export DATABRICKS_TOKEN="your-personal-access-token"  
         export ANTHROPIC_API_KEY="your-anthropic-api-key"  
         

For production environments, use [Mosaic AI Gateway or Databricks secrets](</aws/en/mlflow3/genai/tracing/integrations/#secure-api-key-management>) for secure API key management.

  2. Enable autologging for Claude Agent SDK to trace all Claude Agent SDK interactions:

note

MLflow does not support tracing direct calls to `query`. MLflow only supports tracing interactions that use `ClaudeSDKClient`.

Python
         
         import asyncio  
         import mlflow.anthropic  
         from claude_agent_sdk import ClaudeSDKClient  
           
         # Enable autologging  
         mlflow.anthropic.autolog()  
           
         # Optionally configure MLflow experiment  
         mlflow.set_experiment("my_claude_app")  
           
           
         async def main():  
            async with ClaudeSDKClient() as client:  
               await client.query("What is the capital of France?")  
           
               async for message in client.receive_response():  
                     print(message)  
           
           
         if __name__ == "__main__":  
            asyncio.run(main())  
         

To disable autologging, call `mlflow.anthropic.autolog(disable=True)`.

  3. View your traces in the [MLflow experiment UI](</aws/en/mlflow3/genai/tracing/observe-with-traces/>) in your Databricks workspace.




  1. Configure Claude Code hooks. Use `mlflow autolog claude` to configure hooks in a `.claude/settings.json` file in your project directory:

Bash
         
         # Set up tracing in your project directory  
         mlflow autolog claude ~/my-project  
           
         # Or set up tracing in current directory  
         mlflow autolog claude  
         

  2. Additional configuration options:

Bash
         
         # Specify experiment by name  
         mlflow autolog claude -n "My AI Project"  
           
         # Specify experiment by ID  
         mlflow autolog claude -e 123456789  
           
         # Use local file-based tracking instead of Databricks  
         mlflow autolog claude -u file://./custom-mlruns  
         mlflow autolog claude -u sqlite:///mlflow.db  
           
         

note

To disable tracing, run `mlflow autolog claude --disable`. This removes the tracing configuration from `.claude/settings.json`.

  3. Add Databricks environment variables. The hooks created by `mlflow autolog claude` run in their own environment and do not inherit shell environment variables. To trace to Databricks, add the required environment variables to the `env` section of each hook in `.claude/settings.json`:

JSON
         
         {  
           "hooks": {  
             "ConversationStart": [  
               {  
                 "type": "command",  
                 "command": "python -m mlflow.anthropic.autolog.claude.init_span",  
                 "timeout": 30000,  
                 "env": {  
                   "MLFLOW_CLAUDE_TRACING_ENABLED": "true",  
                   "MLFLOW_TRACKING_URI": "databricks",  
                   "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",  
                   "DATABRICKS_TOKEN": "your-databricks-token"  
                 }  
               }  
             ],  
             "ConversationTurn": [  
               {  
                 "type": "command",  
                 "command": "python -m mlflow.anthropic.autolog.claude.end_span",  
                 "timeout": 30000,  
                 "env": {  
                   "MLFLOW_CLAUDE_TRACING_ENABLED": "true",  
                   "MLFLOW_TRACKING_URI": "databricks",  
                   "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",  
                   "DATABRICKS_TOKEN": "your-databricks-token"  
                 }  
               }  
             ],  
             "Stop": [  
               {  
                 "type": "command",  
                 "command": "python -m mlflow.anthropic.autolog.claude.end_span --end-trace",  
                 "timeout": 30000,  
                 "env": {  
                   "MLFLOW_CLAUDE_TRACING_ENABLED": "true",  
                   "MLFLOW_TRACKING_URI": "databricks",  
                   "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",  
                   "DATABRICKS_TOKEN": "your-databricks-token"  
                 }  
               }  
             ]  
           }  
         }  
         

Replace `your-workspace.cloud.databricks.com` with your Databricks workspace URL and `your-databricks-token` with your [personal access token](</aws/en/dev-tools/auth/pat>).

  4. To specify which MLflow experiment to use, add `MLFLOW_EXPERIMENT_NAME` or `MLFLOW_EXPERIMENT_ID` to the `env` section of each hook:

JSON
         
         "env": {  
           "MLFLOW_CLAUDE_TRACING_ENABLED": "true",  
           "MLFLOW_TRACKING_URI": "databricks",  
           "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",  
           "DATABRICKS_TOKEN": "your-databricks-token",  
           "MLFLOW_EXPERIMENT_NAME": "/Users/your-email@company.com/my-claude-traces"  
         }  
         

  5. Go to your project directory and use Claude Code normally. Your conversations are automatically traced to Databricks:

Bash
         
         cd ~/my-project  
         claude "help me refactor this Python function to be more efficient"  
         

  6. View your traces in the [MLflow experiment UI](</aws/en/mlflow3/genai/tracing/observe-with-traces/>) in your Databricks workspace.




## Advanced: SDK tracing with evaluationâ

You can use SDK tracing with [MLflow's GenAI evaluation framework](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>):

Python
    
    
    import asyncio  
    import pandas as pd  
    from claude_agent_sdk import ClaudeSDKClient  
      
    import mlflow.anthropic  
    from mlflow.genai import evaluate, scorer  
    from mlflow.genai.judges import make_judge  
      
    mlflow.anthropic.autolog()  
      
      
    async def run_agent(query: str) -> str:  
       """Run Claude Agent SDK and return response"""  
       async with ClaudeSDKClient() as client:  
          await client.query(query)  
      
          response_text = ""  
          async for message in client.receive_response():  
                response_text += str(message) + "\n\n"  
      
          return response_text  
      
      
    def predict_fn(query: str) -> str:  
       """Synchronous wrapper for evaluation"""  
       return asyncio.run(run_agent(query))  
      
      
    relevance = make_judge(  
       name="relevance",  
       instructions=(  
          "Evaluate if the response in {{ outputs }} is relevant to "  
          "the question in {{ inputs }}. Return either 'pass' or 'fail'."  
       ),  
       model="openai:/gpt-4o",  
    )  
      
    # Create evaluation dataset  
    eval_data = pd.DataFrame(  
       [  
          {"inputs": {"query": "What is machine learning?"}},  
          {"inputs": {"query": "Explain neural networks"}},  
       ]  
    )  
      
    # Run evaluation with automatic tracing  
    mlflow.set_experiment("claude_evaluation")  
    evaluate(data=eval_data, predict_fn=predict_fn, scorers=[relevance])  
    

## Troubleshootingâ

  * SDK tracing
  * CLI tracing



**Missing traces:**

  * Verify `mlflow.anthropic.autolog()` is called before creating the `ClaudeSDKClient`
  * Check that the environment variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) are set correctly
  * Verify your Databricks token has not expired



Verify that CLI tracing is enabled for your project:

Bash
    
    
    mlflow autolog claude --status  
    

This displays the current tracing configuration and whether it's active for the Claude Code CLI.

**Tracing not working:**

  * Ensure you're in the configured directory
  * Check that `.claude/settings.json` exists
  * Review logs in `.claude/mlflow/claude_tracing.log`



**Missing traces:**

  * Check if `MLFLOW_CLAUDE_TRACING_ENABLED=true` in your configuration
  * Verify the tracking URI is accessible
  * Review logs in `.claude/mlflow/claude_tracing.log`



**Databricks connection issues:**

  * Verify that `MLFLOW_TRACKING_URI`, `DATABRICKS_HOST`, and `DATABRICKS_TOKEN` are set in the `env` section of each hook in `.claude/settings.json`
  * Shell environment variables are not passed to Claude Code hooks; the variables must be in the settings file
  * Check that your Databricks token has not expired
  * Verify your workspace URL is correct (for example, `https://your-workspace.cloud.databricks.com`)
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/mlflow-mcp -->

On this page

Last updated on **Jan 28, 2026**

# MLflow MCP server

The MLflow MCP (Model Context Protocol) server enables AI applications and coding assistants to interact with your traces programmatically.

The MLflow MCP server exposes all MLflow trace management operations through the MCP protocol, allowing AI assistants to:

  * Search and retrieve trace data
  * Analyze trace performance and behavior
  * Log feedback and assessments
  * Manage trace tags and metadata
  * Delete traces and assessments



For complete documentation on the MLflow MCP server, including installation, configuration, and available tools, see the [open source MLflow MCP server documentation](<https://mlflow.org/docs/latest/genai/mcp/>).

## Prerequisitesâ

  * An MCP-compatible client such as VS Code, Cursor, or Claude.

  * MLflow Python library version 3.5.1 or later with the `databricks` and `mcp` extras. The `mcp` extra provides the MCP server dependencies, and the `databricks` extra provides Databricks authentication and connectivity:

Bash
        
        pip install 'mlflow[databricks,mcp]>=3.5.1'  
        




## Configure for Databricksâ

To use the MLflow MCP server with traces stored in Databricks, configure your MCP client with the following settings:

  * VS Code
  * Cursor
  * Claude Desktop



Add this configuration to `.vscode/mcp.json` in your project:

JSON
    
    
    {  
      "servers": {  
        "mlflow-mcp": {  
          "command": "uv",  
          "args": ["run", "--with", "mlflow[databricks,mcp]>=3.5.1", "mlflow", "mcp", "run"],  
          "env": {  
            "MLFLOW_TRACKING_URI": "databricks",  
            "DATABRICKS_HOST": "<your-workspace-url>",  
            "DATABRICKS_TOKEN": "<your-token>"  
          }  
        }  
      }  
    }  
    

Add this configuration to `.cursor/mcp.json` in your project:

JSON
    
    
    {  
      "mcpServers": {  
        "mlflow-mcp": {  
          "command": "uv",  
          "args": ["run", "--with", "mlflow[databricks,mcp]>=3.5.1", "mlflow", "mcp", "run"],  
          "env": {  
            "MLFLOW_TRACKING_URI": "databricks",  
            "DATABRICKS_HOST": "<your-workspace-url>",  
            "DATABRICKS_TOKEN": "<your-token>"  
          }  
        }  
      }  
    }  
    

Add this configuration to your Claude Desktop settings file:

  * **macOS** : `~/Library/Application Support/Claude/claude_desktop_config.json`
  * **Windows** : `%APPDATA%\Claude\claude_desktop_config.json`



JSON
    
    
    {  
      "mcpServers": {  
        "mlflow-mcp": {  
          "command": "uv",  
          "args": ["run", "--with", "mlflow[databricks,mcp]>=3.5.1", "mlflow", "mcp", "run"],  
          "env": {  
            "MLFLOW_TRACKING_URI": "databricks",  
            "DATABRICKS_HOST": "<your-workspace-url>",  
            "DATABRICKS_TOKEN": "<your-token>"  
          }  
        }  
      }  
    }  
    

Replace `<your-workspace-url>` with your Databricks workspace URL (for example, `https://your-workspace.cloud.databricks.com`) and `<your-token>` with your personal access token.

## Use the MLflow Tracing MCP serverâ

After configuring the MCP server, your AI assistant can interact with traces stored in Databricks. For example, you can ask your assistant to:

  * "Search for traces from experiment ID 12345"
  * "Show me the most recent traces with errors"
  * "Get trace details for trace ID tr-abc123"
  * "Add feedback to trace tr-abc123 with a rating of 5"



See the [open source MLflow MCP server documentation](<https://mlflow.org/docs/latest/genai/mcp/>) for more information.

## Next stepsâ

  * [MLflow Tracing - GenAI observability](</aws/en/mlflow3/genai/tracing/>)
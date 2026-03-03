<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/add-context-to-traces -->

On this page

Last updated on **Nov 26, 2025**

# Add context to traces

Adding context to traces enables you to track execution details, analyze user behavior, debug issues across environments, and monitor application performance. MLflow provides standardized metadata fields for common context types plus the flexibility to add custom metadata specific to your application.

## Requirementsâ

Install the appropriate package for tracing based on your environment:

  * Production
  * Development



For production deployments, install the `mlflow-tracing` package:

Bash
    
    
    pip install --upgrade mlflow-tracing  
    

The `mlflow-tracing` package is optimized for production use with minimal dependencies and better performance characteristics.

For development environments, install the full MLflow package with Databricks extras:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1"  
    

The full `mlflow[databricks]` package includes all features needed for local development and experimentation on Databricks.

note

MLflow 3 is required for context tracking. MLflow 2.x is not supported due to performance limitations and missing features essential for production use.

## Implementationâ

To add metadata and tags to traces:

  1. [Trace your application](</aws/en/mlflow3/genai/tracing/app-instrumentation/>). Most commonly, you will use the `@mlflow.trace` decorator to trace functions automatically.
  2. During your application's execution, call [`mlflow.update_current_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=trace#mlflow.update_current_trace>) to add context to traces using `tags` or `metadata`. After your application completes and a trace is logged, `tags` are mutable, but `metadata` are immutable in the logged trace.



Python
    
    
    import mlflow  
    mlflow.update_current_trace(  
        metadata={  
            "mlflow.trace.user": user_id,  
            "mlflow.trace.session": session_id,  
        },  
        tags={  
            "query_category": "chat",  # Example of a custom tag  
        },  
    )  
    

To access metadata and tags in trace logs, use the `metadata` and `tags` fields in the pandas DataFrame returned by `mlflow.search_traces()`, or use the [`Trace.info.trace_metadata`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo.trace_metadata>) and [`Trace.info.tags`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo.tags>) fields from [`Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) objects.

See [Tutorial: Trace and analyze users and environments](</aws/en/mlflow3/genai/tracing/add-context-to-traces-tutorial>) for a full tutorial.

## Types of context metadataâ

Production applications need to track multiple pieces of context simultaneously. MLflow has standardized metadata fields to capture important contextual information:

Context type| Use cases| MLflow field| Client request ID| Link traces to specific client requests or API calls for end-to-end debugging| [`TraceInfo` parameter `client_request_id`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>)| User session ID| Group traces from multi-turn conversations, allowing you to analyze the full conversational flow| [`mlflow.trace.session` metadata](<https://mlflow.org/docs/latest/genai/tracing/track-environments-context/#reserved-standard-tags>)| User ID| Associate traces with specific users for personalization, cohort analysis, and user-specific debugging| [`mlflow.trace.user` metadata](<https://mlflow.org/docs/latest/genai/tracing/track-environments-context/#reserved-standard-tags>)| Environment data| Track deployment context (environment, version, region) for operational insights and debugging across different deployments| [automatic metadata](<https://mlflow.org/docs/latest/genai/tracing/track-environments-context/#automatically-populated-tags>) and custom metadata| Custom metadata| Add application-specific metadata for organization, search, and filtering traces| (your metadata keys)  
---|---|---  
  
## Track users and sessionsâ

Tracking users and sessions in your GenAI application provides essential context for understanding user behavior, analyzing conversation flows, and improving personalization.

### Why track users and sessions?â

User and session tracking enables powerful analytics and improvements:

  1. **User behavior analysis** \- Understand how different users interact with your application
  2. **Conversation flow tracking** \- Analyze multi-turn conversations and context retention
  3. **Personalization insights** \- Identify patterns to improve user-specific experiences
  4. **Quality per user** \- Track performance metrics across different user segments
  5. **Session continuity** \- Maintain context across multiple interactions



### Standard metadata fields for users and sessionsâ

MLflow provides two standard metadata fields for session and user tracking:

  * `mlflow.trace.user` \- Associates traces with specific users
  * `mlflow.trace.session` \- Groups traces belonging to multi-turn conversations



When you use these standard metadata fields, MLflow automatically enables filtering and grouping in the UI. Unlike tags, metadata cannot be updated once the trace is logged, making it ideal for immutable identifiers like user and session IDs.

## Track environments and versionsâ

Tracking the execution environment and application version of your GenAI application allows you to debug performance and quality issues relative to the code. This metadata enables:

  * **Environment-specific analysis** across `development`, `staging`, and `production`
  * **Performance/quality tracking** and regression detection across app versions
  * **Faster root cause analysis** when issues occur



For deployment metadata such as environments and versions, your application should generally extract the metadata from environment variables, rather than having the metadata hard-coded into the application. Environment variables simplify the deployment process. For example:

Python
    
    
    import mlflow  
    import os  
      
    # In your application logic  
    mlflow.update_current_trace(  
        metadata={  
            "mlflow.source.type": os.getenv("APP_ENVIRONMENT", "development"),  # Override default  
        }  
    )  
    

note

For a comprehensive overview of how versioning works, see [Version Tracking](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>).

### Automatically populated metadataâ

MLflow automatically sets [certain standard metadata fields](<https://mlflow.org/docs/latest/genai/tracing/track-environments-context/#automatically-populated-tags>) based on your execution environment.

You can override any of the automatically populated metadata fields using [`mlflow.update_current_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>). This is useful when the automatic detection does not meet your requirements. For example, override the execution environment value using `mlflow.update_current_trace(metadata={"mlflow.source.name": "custom_name"})`.

Category| Metadata Field| Description| Automatic Setting Logic| **Execution environment**| `mlflow.source.name`| The entry point or script that generated the trace.| Automatically populated with the filename for Python scripts, notebook name for Databricks/Jupyter notebooks.| | `mlflow.source.git.commit`| Git commit hash.| If run from a Git repository, the commit hash is automatically detected and populated.| | `mlflow.source.git.branch`| Git branch.| If run from a Git repository, the current branch name is automatically detected and populated.| | `mlflow.source.git.repoURL`| Git repo URL.| If run from a Git repository, the repository URL is automatically detected and populated.| | `mlflow.source.type`| Captures the execution environment.| Automatically set to `NOTEBOOK` if running in Jupyter or Databricks notebook, `LOCAL` if running a local Python script, else `UNKNOWN` (automatically detected)._In your deployed app, we suggest updating this variable based on the environment e.g.,`PRODUCTION`, `STAGING`, etc._| | `mlflow.sourceRun`| The run ID of the source run that generated the trace.| Automatically set to the run ID of the source run that generated the trace.| **Application version**| `metadata.mlflow.modelId`| MLflow [LoggedModel](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>) ID.| Automatically set to the model ID value in the environment variable `MLFLOW_ACTIVE_MODEL_ID` or the model ID set via [`mlflow.set_active_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_active_model>) function.  
---|---|---|---  
  
### Add custom metadataâ

You use custom `metadata` keys to capture any other application-specific context. For example, you might want to attach information such as:

  * Application version
  * Deployment ID
  * Deployment region
  * Feature flags



## Best practicesâ

  1. **Consistent ID formats** \- Use standardized formats for user and session IDs across your application
  2. **Session boundaries** \- Define clear rules for when sessions start and end
  3. **Environment variables** \- Populate metadata from environment variables rather than hard-coding values
  4. **Combine context types** \- Track user, session, and environment context together for complete traceability
  5. **Regular analysis** \- Set up dashboards to monitor user behavior, session patterns, and version performance
  6. **Override defaults thoughtfully** \- Only override automatically populated metadata when necessary



## Next stepsâ

  * [Tutorial: Trace and analyze users and environments](</aws/en/mlflow3/genai/tracing/add-context-to-traces-tutorial>) \- See a full example of adding user, session, environment, and app version metadata to traces.
  * [Search traces programmatically](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-via-sdk>) \- Learn more about using [`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_traces>).
  * [Examples: Analyzing traces](</aws/en/mlflow3/genai/tracing/observe-with-traces/analyze-traces>) \- See examples of trace analytics.
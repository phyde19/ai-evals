<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/tracing-101 -->

On this page

Last updated on **Nov 26, 2025**

# Trace concepts

Tracing is an observability technique that captures the complete execution flow of a request through your application. Unlike traditional logging that records isolated events, tracing creates a detailed map of how data flows through your systems and records every operation along the way.

For GenAI applications, tracing is essential because these systems involve complex, multi-step workflows with multiple components (LLMs, retrievers, tools, agents) that are difficult to debug without complete visibility into the execution flow.

## Trace structureâ

An MLflow [Trace](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) comprises two primary objects:

  1. `Trace.info` of type [`TraceInfo`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>): Metadata explaining the trace's origination, status, and execution time. Includes tags for additional context such as user, session, and developer-provided key-value pairs used for searching or filtering traces.

  2. `Trace.data` of type [`TraceData`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceData>): The actual payload containing instrumented [Span](</aws/en/mlflow3/genai/tracing/span-concepts>) objects that capture your application's step-by-step execution from input to output.




MLflow Traces are compatible with [OpenTelemetry specifications](<https://opentelemetry.io/docs/concepts/signals/traces/>), a widely adopted industry standard for observability. This ensures interoperability with other observability tools while MLflow enhances the OpenTelemetry model with GenAI-specific structures and attributes.

### TraceInfoâ

[`TraceInfo`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>) provides lightweight metadata about the overall trace. Key fields include:

Field| Description| `trace_id`| Unique identifier for the trace| `trace_location`| Where the trace is stored (MLflow Experiment or Databricks Inference Table)| `request_time`| Start time of the trace in milliseconds| `state`| Trace status: `OK`, `ERROR`, `IN_PROGRESS`, or `STATE_UNSPECIFIED`| `execution_duration`| Duration of the trace in milliseconds| `request_preview`| JSON-encoded preview of the input (root span input)| `response_preview`| JSON-encoded preview of the output (root span output)| `tags`| Key-value pairs for filtering and searching traces  
---|---  
  
### TraceDataâ

The [`TraceData`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceData>) object is a container of [Span](</aws/en/mlflow3/genai/tracing/span-concepts>) objects where the execution details are stored. Each span captures information about a specific operation, including:

  * Requests and responses
  * Latency measurements
  * LLM messages and tool parameters
  * Retrieved documents and context
  * Metadata and attributes



Spans form a hierarchical structure through parent-child connections, creating a tree that represents your application's execution flow.

### Tagsâ

Tags are mutable key-value pairs attached to traces for organization and filtering. MLflow defines standard tags for common use cases:

  * `mlflow.trace.session`: Session identifier for grouping related traces
  * `mlflow.trace.user`: User identifier for tracking per-user interactions
  * `mlflow.source.name`: Entry point or script that generated the trace
  * `mlflow.source.git.commit`: Git commit hash of the source code (if applicable)
  * `mlflow.source.type`: Source type (`PROJECT`, `NOTEBOOK`, etc.)



You can also add custom tags for your specific needs. Learn more in [Add context to traces](</aws/en/mlflow3/genai/tracing/add-context-to-traces>) and [Attach custom tags / metadata](</aws/en/mlflow3/genai/tracing/attach-tags/>).

## Storage layoutâ

MLflow optimizes trace storage for performance and cost. You can customize trace storage locations using Unity Catalog volumes when [creating experiments](</aws/en/mlflow/experiments#create-experiment-from-the-workspace>). Trace data access is then governed by [Unity Catalog volume privileges](</aws/en/data-governance/unity-catalog/manage-privileges/privileges#read-volume>) for enhanced security and compliance.

**TraceInfo** is stored directly in a relational database as single rows with indexed fields, enabling fast queries for searching and filtering traces.

**TraceData** (Spans) is stored in artifact storage rather than in the database due to its larger size. This enables cost-effective handling of large trace volumes with minimal performance impact on queries.

## Active vs. finished tracesâ

An active trace is one being actively logged, such as in a [function decorated with `@mlflow.trace`](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>). Once the decorated function has exited, the trace is finished but can still be annotated with new data.

Important methods for working with active or recent traces include [`mlflow.get_active_trace_id()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_active_trace_id>) and [`mlflow.get_last_active_trace_id()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_last_active_trace_id>).

## Next stepsâ

  * [Span concepts](</aws/en/mlflow3/genai/tracing/span-concepts>) \- Learn about spans and how they capture individual operations
  * [Tracing in a notebook](</aws/en/mlflow3/genai/getting-started/tracing/tracing-notebook>) \- Get hands-on experience with tracing
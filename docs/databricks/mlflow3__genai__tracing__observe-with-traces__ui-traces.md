<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/ui-traces -->

On this page

Last updated on **Jan 5, 2026**

# View traces in the Databricks MLflow UI

All captured traces are logged to an MLflow Experiment. You can access them through the MLflow UI in your Databricks workspace.

tip

Traces are stored and served by the managed MLflow Tracking service in your Databricks workspace when `MLFLOW_TRACKING_URI` is set to `databricks`. This productionâready backend requires no additional hosting. See [Trace agents deployed on Databricks](</aws/en/mlflow3/genai/tracing/prod-tracing>).

  1. **Navigate to your Experiment** : Go to the experiment where your traces are logged. For example, the experiment set by `mlflow.set_experiment("/Shared/my-genai-app-traces")`).

  2. **Open the Traces tab** : In the experiment view, click on the **Traces** tab to see a list of all traces logged to that experiment.




## Understand the trace listâ

The trace list provides a high-level overview of your traces, with sortable columns that typically include:

  * **Trace ID** : The unique identifier for each trace.
  * **Request** : A preview of the initial input that triggered the trace.
  * **Response** : A preview of the final output of the trace.
  * **Session** : The session identifier, if provided, grouping related traces (e.g., in a conversation).
  * **User** : The user identifier, if provided.
  * **Execution time** : Total time taken for the trace to complete.
  * **Request time** : The timestamp when the trace was initiated.
  * **Run name** : If the trace is associated with an MLflow Run, its name will be displayed here, linking them.
  * **Source** : The origin of the trace, often indicating the instrumented library or component (e.g., `openai`, `langchain`, or a custom trace name).
  * **State** : The current status of the trace (e.g., `OK`, `ERROR`, `IN_PROGRESS`).
  * **Trace name** : The specific name assigned to this trace, often the root span's name.
  * **Assessments** : Individual columns for each assessment type (e.g., `my_scorer`, `professional`). The UI also often displays a summary section above the list showing aggregated assessment metrics (like averages or pass/fail rates) across the currently visible traces.
  * **Tags** : Individual tags can be displayed as columns (e.g., `persona`, `style`). A summary count of tags might also be present.



## Search and filter tracesâ

The UI offers several ways to find and focus on relevant traces:

  * **Search bar** (often labeled "Search evaluations by request" or similar): This allows you to quickly find traces by searching the content of their `Request` (input) field.
  * **Filters Dropdown** : For more structured filtering, use the "Filters" dropdown. This typically allows you to build queries based on:
    * **Attributes** : Such as `Request` content, `Session time`, `Execution time`, or `Request time`.
    * **Assessments** : Filter by the presence or specific values of assessments like `my_scorer` or `professional`.
    * Other fields like `State`, `Trace name`, `Session`, `User`, and `Tags` (e.g., `tags.persona = 'expert'`).
  * **Sort Dropdown** : Use the "Sort" dropdown to order traces by various columns like `Request time`, `Execution time`, etc.
  * **Columns Dropdown** : Customize which columns are visible in the trace list, including specific tags or assessment metrics.



### Metadata filtersâ

In the MLflow UI (Traces tab), you can view the attached metadata:

Filter traces in the MLflow UI using these search queries:
    
    
    # Find all traces for a specific user  
    metadata.`mlflow.trace.user` = 'user-123'  
      
    # Find all traces in a session  
    metadata.`mlflow.trace.session` = 'session-abc-456'  
      
    # Find traces for a user within a specific session  
    metadata.`mlflow.trace.user` = 'user-123' AND metadata.`mlflow.trace.session` = 'session-abc-456'  
      
    # Find traces from production environment  
    metadata.`mlflow.source.type` = 'production'  
      
    # Find traces from a specific app version  
    metadata.app_version = '1.0.0'  
    

## Explore an individual traceâ

To dive deep into a specific trace, click on its **Request** or **Trace Name** in the list. This opens the detailed trace view, which typically has a few main panels:

  1. **Trace breakdown (Left Panel)** :

     * This panel (often titled "Trace breakdown") displays the **span hierarchy** as a tree or waterfall chart. It shows all operations (spans) within the trace, their parent-child relationships, and their execution order and duration.
     * You can select individual spans from this breakdown to inspect their specific details.
  2. **Span Details (Center Panel)** :

     * When a span is selected from the Trace breakdown, this panel shows its detailed information, usually organized into tabs such as:
       * **Chat** : For LLM interactions that are chat-based, this tab often provides a rendered view of the conversation flow (user, assistant, tool messages).

       * **Inputs / Outputs** : Displays the raw input data passed to the operation and the raw output data it returned. For large content, a "See more" / "See less" toggle may be available to expand or collapse the view.

       * **Attributes** : Shows key-value metadata specific to the span (e.g., `model` name, `temperature` for an LLM call; `doc_uri` for a retriever span).

       * **Events** : For spans that encountered errors, this tab typically shows exception details and stack traces. For streaming spans, it may show individual data chunks as they were yielded.

       * Some output fields might also have a **Markdown toggle** to switch between raw and rendered views if the content is in Markdown format.

  3. **Assessments (Right Panel)** :

     * This panel displays any assessments (user feedback or evaluations) that have been logged for the **entire trace** or for the **currently selected span**.
     * Crucially, this panel often includes an **"+ Add new assessment"** button, allowing you to log new feedback or evaluation scores directly from the UI while reviewing a trace. This is very useful for manual review and labeling workflows.




**Trace-Level Information** : Beyond individual span details, the view also provides access to overall trace information. This includes trace-level tags and any assessments logged for the entire trace (often visible in the Assessments panel when no specific span or the root span is selected), which may originate from [direct user feedback](</aws/en/mlflow3/genai/tracing/collect-user-feedback/>) or [systematic evaluations](</aws/en/mlflow3/genai/eval-monitor/>).

## Common debugging scenariosâ

Here's how you can use the MLflow Tracing UI to address common debugging and observability needs:

  1. **Identify slow traces (latency bottlenecks)** :

     * **In the Trace List View** : Use the "Sort" dropdown to sort traces by "Execution time" in descending order. This will bring the slowest traces to the top.
     * **In the Detailed Trace View** : Once you open a slow trace, examine the "Trace breakdown" panel. The waterfall display of spans will visually highlight operations that took the longest, helping you pinpoint latency bottlenecks within your application's flow.

  2. **Find traces from a particular user** :

     * **Use filters** : If you have [tracked user information](</aws/en/mlflow3/genai/tracing/add-context-to-traces>) and it's available as a filter option (e.g., under "Attributes" or a dedicated "User" filter in the "Filters" dropdown), you can select or enter the specific user ID.
     * **Use search and tags** : Alternatively, if user IDs are stored as tags (e.g., `mlflow.trace.user`), use the search bar with a query like `tags.mlflow.trace.user = 'user_example_123'`.

  3. **Locate traces with failures (Errors)** :

     * **Use Filters** : In the "Filters" dropdown, select the `State` attribute and choose `ERROR` to see only traces that failed.
     * **In the Detailed Trace View** : For an error trace, select the span marked with an error in the "Trace breakdown". Navigate to its "Events" tab in the Span Details panel to view the exception message and stack trace, which are crucial for diagnosing the root cause of the failure.

  4. **Identify traces with negative feedback or issues** :

     * **Use assessment filters** : If you are [collecting user feedback or running evaluations](</aws/en/mlflow3/genai/tracing/collect-user-feedback/>) that result in assessments (e.g., a boolean `is_correct` or a numeric `relevance_score`), the "Filters" dropdown might allow you to filter by these assessment names and their values (e.g., filter for `is_correct = false` or `relevance_score < 0.5`).
     * **View assessments** : Open a trace and check the "Assessments" panel (on the right in the detailed view) or individual span assessments. This will show any logged feedback, scores, and rationales, helping you understand why a response was marked as poor quality.




These examples demonstrate how the detailed information captured by MLflow Tracing, combined with the UI's viewing and filtering capabilities, empowers you to efficiently debug issues and observe your application's behavior.

## Tracing in Databricks notebooksâ

MLflow Tracing offers a seamless experience within Databricks notebooks, allowing you to view traces directly as part of your development and experimentation workflow.

note

The MLflow Tracing Databricks Notebook integration is available in MLflow 2.20 and above.

When working in a Databricks notebook and your MLflow Tracking URI is set to `"databricks"` (which is often the default or can be set using [`mlflow.set_tracking_uri("databricks")`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=set_tracking#mlflow.set_tracking_uri>)), the trace UI can be automatically displayed in the output of a cell.

This typically occurs when:

  1. A cell's code execution generates a trace (e.g., by calling a function decorated with `@mlflow.trace` or an [auto-instrumented library call](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>)).
  2. You explicitly call [`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=get_trace#mlflow.get_trace>) and the result is displayed.
  3. An [`mlflow.entities.Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) object (e.g., from [`mlflow.get_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_trace>) is the last expression in a cell or is passed to `display()`.



This in-notebook view provides the same rich, interactive trace exploration capabilities found in the main MLflow Experiments UI, helping you iterate faster without context switching.

### Control notebook displayâ

To enable or disable the automatic display of traces in notebook cell outputs, run: [`mlflow.tracing.disable_notebook_display()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html?highlight=disable_notebook_disp#mlflow.tracing.enable>) or [`mlflow.tracing.enable_notebook_display()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html?highlight=disable_notebook_disp#mlflow.tracing.enable_notebook_display>)

## Next stepsâ

  * [Query traces via SDK](</aws/en/mlflow3/genai/tracing/observe-with-traces/query-via-sdk>) \- Programmatically search and analyze traces for custom workflows
  * [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) \- Select and convert traces into test data for systematic evaluation and quality improvement
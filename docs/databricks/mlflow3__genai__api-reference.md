<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/api-reference -->

On this page

Last updated on **Aug 7, 2025**

# MLflow API Reference

This page provides an index of important MLflow APIs used in GenAI applications, with direct links to the official MLflow documentation.

MLflow features marked as "Databricks only" are only available on Databricks-managed MLflow.

## Quick linksâ

  * [All MLflow Python APIs](<https://mlflow.org/docs/latest/api_reference/python_api/index.html#>)
  * [MLflow Core APIs](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html>)
  * [MLflow GenAI Module](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html>)
    * [MLflow Tracing APIs](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow-tracing-apis>)
    * [Evaluation dataset reference](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-datasets>)
    * [Production monitoring reference](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>)
  * [MLflow Client APIs](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html>)
  * [MLflow Entities](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html>)



Beta and Experimental Features

Some of the APIs referenced on this page are currently in the [Beta](</aws/en/release-notes/release-types>) or [Experimental](</aws/en/release-notes/release-types>) stages. These APIs are subject to change or removal in future releases. Experimental APIs are available to all customers, and Beta APIs are available to most customers automatically. If you do not have access to a Beta API and need to request access, contact your Databricks support representative.

## Experiment managementâ

Manage MLflow experiments and runs for tracking GenAI application development:

### SDKâ

  * [`mlflow.search_runs()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_runs>) \- Search and filter runs by criteria
  * [`mlflow.set_experiment()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_experiment>) \- Set the active MLflow experiment
  * [`mlflow.start_run()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.start_run>) \- Start a new MLflow run for tracking



### Entitiesâ

  * [`mlflow.entities.Experiment`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Experiment>) \- Experiment metadata and configuration
  * [`mlflow.entities.Run`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Run>) \- Run metadata, metrics, and parameters



## Tracingâ

Instrument and capture execution traces from GenAI applications:

### SDKâ

  * [`mlflow.delete_trace_tag()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.delete_trace_tag>) \- Remove a tag from a trace
  * [`mlflow.get_current_active_span()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_current_active_span>) \- Get the currently active span
  * [`mlflow.get_last_active_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html>) \- Retrieve the most recently completed trace
  * [`mlflow.get_last_active_trace_id()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_last_active_trace_id>) \- Get ID of the last active trace
  * [`mlflow.get_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.get_trace>) \- Retrieve a trace by ID
  * [`mlflow.search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_traces>) \- Search and filter traces
  * [`mlflow.set_trace_tag()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.set_trace_tag>) \- Add a tag to a trace
  * [`mlflow.start_span()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.start_span>) \- Manually start a new span
  * [`mlflow.trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.trace>) \- Decorator to automatically trace function execution
  * [`mlflow.traceName`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html>) \- Context manager to set trace name
  * [`mlflow.traceOutputs`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html>) \- Context manager to set trace outputs
  * [`mlflow.tracing`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html>) \- Tracing module with configuration functions
  * [`mlflow.tracing.disable`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.disable>) \- Disable tracing globally
  * [`mlflow.tracing.disable_notebook_display()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.disable_notebook_display>) \- Disable trace display in notebooks
  * [`mlflow.tracing.enable`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.enable>) \- Enable tracing globally
  * [`mlflow.tracing.enable_notebook_display()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html#mlflow.tracing.enable_notebook_display>) \- Enable trace display in notebooks
  * [`mlflow.update_current_trace()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.update_current_trace>) \- Update metadata for the current trace



### Entitiesâ

  * [`mlflow.entities.Trace`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>) \- Complete trace with all spans and metadata
  * [`mlflow.entities.TraceData`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceData>) \- Trace execution data
  * [`mlflow.entities.TraceInfo`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.TraceInfo>) \- Trace metadata and summary information
  * [`mlflow.entities.Span`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Span>) \- Individual span within a trace
  * [`mlflow.entities.SpanEvent`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanEvent>) \- Event occurring within a span
  * [`mlflow.entities.SpanType`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.SpanType>) \- Span type classification enum
  * [`mlflow.entities.Document`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Document>) \- Document entity for RAG applications



### Tracing integrationsâ

Auto-instrumentation for popular GenAI frameworks and libraries:

  * [`mlflow.anthropic.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.anthropic.html#mlflow.anthropic.autolog>) \- Anthropic Claude integration
  * [`mlflow.autogen.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.autogen.html#mlflow.autogen.autolog>) \- Microsoft AutoGen integration
  * [`mlflow.bedrock.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.bedrock.html#mlflow.bedrock.autolog>) \- AWS Bedrock integration
  * [`mlflow.crewai.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.crewai.html#mlflow.crewai.autolog>) \- CrewAI integration
  * [`mlflow.dspy.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.dspy.html#mlflow.dspy.autolog>) \- DSPy integration
  * [`mlflow.gemini.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.gemini.html#mlflow.gemini.autolog>) \- Google Gemini integration
  * [`mlflow.groq.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.groq.html#mlflow.groq.autolog>) \- Groq integration
  * [`mlflow.langchain.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.langchain.html#mlflow.langchain.autolog>) \- LangChain integration
  * [`mlflow.litellm.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.litellm.html#mlflow.litellm.autolog>) \- LiteLLM integration
  * [`mlflow.llama_index.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.llama_index.html#mlflow.llama_index.autolog>) \- LlamaIndex integration
  * [`mlflow.mistral.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.mistral.html#mlflow.mistral.autolog>) \- Mistral AI integration
  * [`mlflow.openai.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.openai.html#mlflow.openai.autolog>) \- OpenAI integration



## Evaluation and monitoringâ

### Core evaluation SDKâ

Core APIs for offline evaluation and production monitoring:

  * [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>) \- Evaluation harness to orchestrate offline evaluation with scorers and datasets
  * [`mlflow.genai.to_predict_fn()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.to_predict_fn>) \- Convert model output to standardized prediction function format
  * [`mlflow.genai.Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer>) \- Custom scorer class for object-oriented implementation with state management
  * [`mlflow.genai.scorer()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorer>) \- Scorer decorator for scorer creation and evaluation logic



### Built-in scorersâ

Quality assessment scorers ready for immediate use:

  * [`mlflow.genai.scorers.Safety`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Safety>) \- Content safety evaluation
  * [`mlflow.genai.scorers.Correctness`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Correctness>) \- Answer accuracy assessment
  * [`mlflow.genai.scorers.RelevanceToQuery`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RelevanceToQuery>) \- Query relevance scoring
  * [`mlflow.genai.scorers.Guidelines`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Guidelines>) \- Custom guideline compliance
  * [`mlflow.genai.scorers.ExpectationsGuidelines`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.ExpectationsGuidelines>) \- Guideline evaluation with expectations
  * [`mlflow.genai.scorers.RetrievalGroundedness`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RetrievalGroundedness>) \- RAG grounding assessment
  * [`mlflow.genai.scorers.RetrievalRelevance`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RetrievalRelevance>) \- Retrieved context relevance
  * [`mlflow.genai.scorers.RetrievalSufficiency`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RetrievalSufficiency>) \- Context sufficiency evaluation



Built-in scorer helpers:

  * [`mlflow.genai.scorers.get_all_scorers()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.get_all_scorers>) \- Retrieve all built-in scorers



### Judge functionsâ

LLM-based assessment functions for direct use or scorer wrapping:

  * [`mlflow.genai.judges.is_safe()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.is_safe>) \- Safety assessment
  * [`mlflow.genai.judges.is_correct()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.is_correct>) \- Correctness evaluation
  * [`mlflow.genai.judges.is_grounded()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.is_grounded>) \- Grounding verification
  * [`mlflow.genai.judges.is_context_relevant()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.is_context_relevant>) \- Context relevance
  * [`mlflow.genai.judges.is_context_sufficient()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.is_context_sufficient>) \- Context sufficiency
  * [`mlflow.genai.judges.meets_guidelines()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.meets_guidelines>) \- Custom guideline assessment
  * [`mlflow.genai.make_judge()`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/make-judge/>) \- Create custom judges



#### Judge output entitiesâ

  * [`mlflow.genai.judges.CategoricalRating`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.CategoricalRating>) \- Enum for categorical judge responses
    * [`mlflow.genai.judges.CategoricalRating.YES`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.CategoricalRating.YES>) \- Positive rating
    * [`mlflow.genai.judges.CategoricalRating.NO`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.CategoricalRating.NO>) \- Negative rating
    * [`mlflow.genai.judges.CategoricalRating.UNKNOWN`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.CategoricalRating.UNKNOWN>) \- Uncertain rating



###  Production monitoring scorer lifecycle SDK (Databricks only)â

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

Scorer lifecycle management for continuous quality tracking in production:

#### Scorer instance methodsâ

  * [`Scorer.register()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.register>) \- Register custom scorer with server
  * [`Scorer.start()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.start>) \- Begin online evaluation with sampling
  * [`Scorer.update()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.update>) \- Modify sampling configuration
  * [`Scorer.stop()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.stop>) \- Stop online evaluation



#### Scorer registry functionsâ

  * [`mlflow.genai.scorers.get_scorer()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.get_scorer>) \- Retrieve registered scorer by name
  * [`mlflow.genai.scorers.list_scorers()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.list_scorers>) \- List all registered scorers
  * [`mlflow.genai.scorers.delete_scorer()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.delete_scorer>) \- Delete registered scorers by name



#### Scorer propertiesâ

  * [`Scorer.sample_rate`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.sample_rate>) \- Current sampling rate (0.0-1.0)
  * [`Scorer.filter_string`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.filter_string>) \- Current trace filter



#### Configuration classesâ

  * [`mlflow.genai.ScorerSamplingConfig`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.ScorerSamplingConfig>) \- Sampling configuration data class



### Assessment entitiesâ

Data structures for storing evaluation results and feedback:

  * [`mlflow.entities.Assessment`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Assessment>) \- Evaluation result container
  * [`mlflow.entities.AssessmentError`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.AssessmentError>) \- Assessment error details
  * [`mlflow.entities.AssessmentSource`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.AssessmentSource>) \- Source of the assessment
  * [`mlflow.entities.AssessmentSourceType`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.AssessmentSourceType>) \- Assessment source type enum
  * [`mlflow.entities.Expectation`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Expectation>) \- Expected ground truth outcome
  * [`mlflow.entities.Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>) \- Scorer output with value and rationale



## Evaluation datasetsâ

Create and manage versioned test datasets for systematic evaluation:

### SDKâ

  * [`mlflow.genai.create_dataset()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.create_dataset>) \- Create a new evaluation dataset
  * [`mlflow.genai.delete_dataset()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.delete_dataset>) \- Delete an evaluation dataset
  * [`mlflow.genai.get_dataset()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.get_dataset>) \- Retrieve an existing evaluation dataset



### Entitiesâ

  * [`mlflow.genai.datasets.EvaluationDataset`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.EvaluationDataset>) \- Versioned test data container
    * [`merge_records()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.EvaluationDataset.merge_records>) \- Combine records from multiple sources
    * [`set_profile()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.EvaluationDataset.set_profile>) \- Configure dataset profile settings
    * [`to_df()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.EvaluationDataset.to_df>) \- Convert dataset to pandas DataFrame
    * [`to_evaluation_dataset()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.datasets.EvaluationDataset.to_evaluation_dataset>) \- Convert to evaluation dataset format



## Human labeling and review app (Databricks only)â

Human feedback collection and review workflows for systematic quality assessment:

### Labeling session SDKâ

  * [`mlflow.genai.create_labeling_session()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.create_labeling_session>) \- Create a new labeling session
  * [`mlflow.genai.delete_labeling_session()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.delete_labeling_session>) \- Delete a labeling session
  * [`mlflow.genai.get_labeling_session()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.get_labeling_session>) \- Retrieve labeling session by ID
  * [`mlflow.genai.get_labeling_sessions()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.get_labeling_sessions>) \- List all labeling sessions
  * [`mlflow.genai.get_review_app()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.get_review_app>) \- Retrieve review app instance



### Label schema typesâ

  * [`mlflow.genai.label_schemas.InputCategorical`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.InputCategorical>) \- Categorical input field type
  * [`mlflow.genai.label_schemas.InputCategoricalList`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.InputCategoricalList>) \- Multi-select categorical input
  * [`mlflow.genai.label_schemas.InputNumeric`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.InputNumeric>) \- Numeric input field type
  * [`mlflow.genai.label_schemas.InputText`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.InputText>) \- Text input field type
  * [`mlflow.genai.label_schemas.InputTextList`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.InputTextList>) \- Multi-text input field type
  * [`mlflow.genai.label_schemas.LabelSchema`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.LabelSchema>) \- Label schema definition
  * [`mlflow.genai.label_schemas.LabelSchemaType`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.LabelSchemaType>) \- Schema type enum
    * [`mlflow.genai.label_schemas.LabelSchemaType.EXPECTATION`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.LabelSchemaType.EXPECTATION>) \- Expectation schema type
    * [`mlflow.genai.label_schemas.LabelSchemaType.FEEDBACK`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.LabelSchemaType.FEEDBACK>) \- Feedback schema type



### Label schema SDKâ

  * [`mlflow.genai.label_schemas.create_label_schema()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.create_label_schema>) \- Create a new label schema
  * [`mlflow.genai.label_schemas.delete_label_schema()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.delete_label_schema>) \- Delete an existing label schema
  * [`mlflow.genai.label_schemas.get_label_schema()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.label_schemas.get_label_schema>) \- Retrieve label schema by name



### Entitiesâ

  * [`mlflow.genai.Agent`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Agent>) \- Agent configuration for review app testing

  * [`mlflow.genai.LabelingSession`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.LabelingSession>) \- Human labeling workflow manager

    * [`add_dataset()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.LabelingSession.add_dataset>) \- Add evaluation dataset to labeling session
    * [`add_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.LabelingSession.add_traces>) \- Add traces for human review
    * [`set_assigned_users()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.LabelingSession.set_assigned_users>) \- Assign reviewers to session
    * [`sync()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.LabelingSession.sync>) \- Synchronize session state
  * [`mlflow.genai.ReviewApp`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.ReviewApp>) \- Interactive review application

    * [`add_agent()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.ReviewApp.add_agent>) \- Add agent for testing
    * [`remove_agent()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.ReviewApp.remove_agent>) \- Remove agent from review app



## Prompt managementâ

Version control and lifecycle management for prompts used in GenAI applications:

### SDKâ

  * [`mlflow.genai.load_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.load_prompt>) \- Load a versioned prompt from the registry
  * [`mlflow.genai.optimize_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.optimize_prompt>) \- Automatically improve prompts using optimization algorithms
  * [`mlflow.genai.register_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.register_prompt>) \- Register a new prompt to the registry
  * [`mlflow.genai.search_prompts()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.search_prompts>) \- Search for prompts by name or tags
  * [`mlflow.genai.delete_prompt_alias()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.delete_prompt_alias>) \- Remove an alias from a prompt version
  * [`mlflow.genai.set_prompt_alias()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.set_prompt_alias>) \- Assign an alias to a prompt version



### Entitiesâ

  * [`mlflow.entities.Prompt`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Prompt>) \- Prompt metadata and version information



## Prompt optimizationâ

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

Automated prompt improvement using data-driven optimization algorithms:

### SDKâ

  * [`mlflow.genai.optimize.optimize_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.optimize.optimize_prompt>) \- Run prompt optimization process



### Entitiesâ

  * [`mlflow.genai.optimize.LLMParams`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.optimize.LLMParams>) \- LLM configuration parameters
  * [`mlflow.genai.optimize.OptimizerConfig`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.optimize.OptimizerConfig>) \- Optimization algorithm configuration
  * [`mlflow.genai.optimize.PromptOptimizationResult`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.optimize.PromptOptimizationResult>) \- Optimization results and metrics



## App version trackingâ

Track and manage GenAI application versions in production:

### SDKâ

  * [`mlflow.set_active_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_active_model>) \- Set the active model for version tracking
  * [`mlflow.clear_active_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.clear_active_model>) \- Clear the active model context
  * [`mlflow.get_active_model_id()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_active_model_id>) \- Get the current active model ID
  * [`mlflow.create_external_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.create_external_model>) \- Register an external model deployment
  * [`mlflow.delete_logged_model_tag()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.delete_logged_model_tag>) \- Remove a tag from logged model
  * [`mlflow.finalize_logged_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.finalize_logged_model>) \- Finalize a logged model
  * [`mlflow.get_logged_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.get_logged_model>) \- Retrieve logged model by ID
  * [`mlflow.initialize_logged_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.initialize_logged_model>) \- Initialize a new logged model
  * [`mlflow.last_logged_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.last_logged_model>) \- Get the most recently logged model
  * [`mlflow.search_logged_models()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.search_logged_models>) \- Search for logged models
  * [`mlflow.set_logged_model_tags()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_logged_model_tags>) \- Add tags to logged model
  * [`mlflow.log_model_params()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.log_model_params>) \- Log parameters for a model



### Entitiesâ

  * [`mlflow.entities.LoggedModel`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.LoggedModel>) \- Logged model metadata and information
  * [`mlflow.entities.LoggedModelStatus`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.LoggedModelStatus>) \- Logged model status enum
  * [`mlflow.ActiveModel`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.ActiveModel>) \- Active model context manager
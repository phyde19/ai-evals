<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/concepts/ -->

On this page

Last updated on **Dec 18, 2025**

# Concepts & data model

MLflow for GenAI provides a comprehensive data model designed specifically for developing, evaluating, and monitoring generative AI applications. This page explains the core concepts and how they work together.

## Overviewâ

MLflow organizes all GenAI application data within experiments. An experiment is a project folder that contains every trace, evaluation run, app version, prompt, and quality assessment from throughout an app's lifecycle.

The data model structure is outlined below. For details, see  Data model.

  * Experiment: Container for a single application's data
    * Observability data
      * Traces: App execution logs
        * Assessments: Quality measurements attached to a trace
    * Evaluation data
      * Evaluation datasets: Inputs for quality evaluation
      * Evaluation runs: Results of quality evaluation
    * Human labeling data
      * Labeling sessions: Queues of traces for human labeling
      * Labeling schemas: Structured questions to ask labelers
    * Application versioning data
      * Logged models: App version snapshots
      * Prompts: LLM prompt templates



note

MLflow only requires you to use traces. All other aspects of the data model are optional, but highly recomended.

MLflow provides the following SDKs for interacting with an app's data to evaluate and improve quality. For details, see  MLflow SDKs for evaluating quality.

  * `mlflow.genai.scorers.*`: Functions that analyze a trace's quality, creating feedback assessments.
  * `mlflow.genai.evaluate()`: SDK for evaluating an app's version using evaluation datasets and scorers to identify and improve quality issues.
  * `mlflow.genai.add_scheduled_scorer()`: SDK for running scorers on production traces to monitor quality.



MLflow provides the following UIs for viewing and managing your app's data:

  * Review app: Web UI for collecting domain expert assessments.
  * MLflow experiment UI: UIs for viewing and interacting with traces, evaluation results, labeling sessions, app versions, and prompts.



##  Data modelâ

This section briefly describes each entity in the MLflow data model.

### Experimentsâ

An experiment in MLflow is a named container that organizes and groups together all artifacts related to a single GenAI application. If you are familar with MLflow for classic ML, the experiment container is the same between classic ML and GenAI.

### Observability dataâ

#### Tracesâ

[Traces](</aws/en/mlflow3/genai/tracing/>) capture the complete execution of your GenAI application, including inputs, outputs, and every intermediate step (LLM calls, retrievals, tool use). Traces:

  * Are created automatically for every execution of your application in development and production.
  * Are (optionally) linked to the specific application versions that generated them.
  * Have attached assessments that contain:
    * Quality feedback from scorers, end users, and domain experts.
    * Ground truth expectations from domain experts.



Traces are used to:

  * Observe and debug application behavior and performance (such as latency and cost).
  * Create evaluation datasets based on production logs to use in quality evaluation.



Learn more in [trace concepts](</aws/en/mlflow3/genai/tracing/tracing-101>), follow the [quickstart](</aws/en/mlflow3/genai/getting-started/tracing/tracing-notebook>) to log your first trace, or follow the [instrument your app](</aws/en/mlflow3/genai/tracing/app-instrumentation/>) guide to implement tracing in your app.

#### Assessmentsâ

[Assessments](</aws/en/mlflow3/genai/human-feedback/dev-annotations>) are quality measurements and ground truth labels that are attached to a trace. There are two types of assessments, _feedback_ and _expectations_.

Feedback refers to judgments about the quality of your app's outputs. It is added by end users, domain experts, or automated scorers and is used to identify quality issues. Some examples are thumbs up or thumbs down ratings from end users and the LLM judge's assessment fo a response's correctness.

Expectations are ground truth labels that define the correct output for a given input. It is added by domain experts and is used as a "gold standard" to evaluate if your app produced the right response. Some examples are the expected response to a question and the required facts that must be present in a response.

note

Ground truth labels (expectations) are not required to measure quality with MLflow. Most applications will not have ground truth labels or will have only a small set.

Learn more about [logging assessments](</aws/en/mlflow3/genai/human-feedback/dev-annotations>), see how to [collect user feedback](</aws/en/mlflow3/genai/tracing/collect-user-feedback/>), or explore [using scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) to create automated assessments.

### Evaluation dataâ

#### Evaluation datasetsâ

[Evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) are curated collections of test cases for systematically testing your application. Evaluation datasets:

  * Are typically created by selecting representative traces from production or development.
  * Include inputs and optionally expectations (ground truth).
  * Are versioned over time to track how your test suite evolves.



Evaluation datasets are used to:

  * Iteratively evaluate and improve your app's quality.
  * Validate changes to prevent regressions in quality.



Learn more in the [evaluation datasets reference](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-datasets>), or follow the guide to [build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) which includes techniques for selecting and using production traces.

#### Evaluation runsâ

[Evaluation runs](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>) are the results of testing an application version against an evaluation dataset using a set of scorers. Evaluation runs:

  * Contain the traces (and their assessments) generated by evaluation.
  * Contain aggregated metrics based on the assessments.



Evaluation runs are used to:

  * Determine if application changes improved (or regressed) quality.
  * Compare versions of your application side-by-side.
  * Track quality evaluations over time.



note

Evaluation runs are a special type of MLflow Run and can be queried via [`mlflow.search_runs()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_runs>).

Learn more about the [evaluation harness](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>), follow the guide to [use evaluation to improve your app](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>).

### Human labeling dataâ

#### Labeling sessionsâ

[Labeling sessions](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-sessions>) organize traces for human review by domain experts. Labeling sessions:

  * Queue selected traces that need expert review and contain the assessments from that review.
  * Use labeling schemas to structure the assessments for experts to label.



Labeling sessions are used to:

  * Collect expert feedback on complex or ambiguous cases.
  * Create ground truth data for evaluation datasets.



note

Labeling sessions are a special type of MLflow Run and can be queried via [`mlflow.search_runs()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_runs>).

Learn more about [labeling sessions](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-sessions>), follow the guide to [collect domain expert feedback](</aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces>), or see how to [label during development](</aws/en/mlflow3/genai/human-feedback/dev-annotations>).

#### Labeling schemasâ

[Labeling schemas](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-schemas>) define the assessments that are collected in a labeling session, ensuring consistent label collection across domain experts. Labeling schemas:

  * Specify what questions to ask reviewers (for example, "Is this response accurate?").
  * Define the valid responses to a question (for example, thumbs up/down, 1-5 scales, or free text comments).



Learn more in the [labeling schemas reference](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-schemas>).

### Application versioning dataâ

#### Promptsâ

[Prompts](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/>) are version-controlled templates for LLM prompts. Prompts:

  * Are tracked with Git-like version history.
  * Include `{{variables}}` for dynamic generation.
  * Are linked to evaluation-runs to track their quality over time.
  * Support aliases like "production" for deployment management.



#### Logged modelsâ

[Logged models](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>) represent snapshots of your application at specific points in time. Logged models:

  * Link to the traces they generate and the prompts they use.
  * Link to evaluation runs to track their quality.
  * Track application parameters such as LLM temperature.



Logged models can act as a metadata hub, linking a conceptual application version to its specific external code (for example, a pointer to the Git commit). You can also use a logged model to package your application's code and configuration as a fully deployable artifact.

Learn more about [version tracking](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>), see how to [track application versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>), or learn about [linking traces to versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/link-production-traces-to-app-versions>).

##  MLflow SDKs for evaluating qualityâ

These are the key processes that evaluate the quality of traces, attaching assessments to the trace containing the evaluation's results.

### Scorersâ

**[`mlflow.genai.scorers.*`](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)** are functions that evaluate a trace's quality. Scorers:

  * Parse a trace for the relevant data fields to be evaluated.
  * Use that data to evaluate quality using either deterministic code or LLM judge based evaluation criteria.
  * Return feedback entities with the results of that evaluation.



The same scorer can be used for evaluation in development and production.

note

**Scorers vs. Judges** : If you're familiar with LLM judges, you might wonder how they relate to scorers. In MLflow, a _judge_ is a callable SDK (like [`mlflow.genai.judges.is_correct`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.is_correct>)) that evaluates text based on specific criteria. However, judges can't directly process traces - they only understand text inputs. Scorers extract the relevant data from a trace (such as the request, response, and retrieved context) and pass it to the judge for evaluation. Think of scorers as the "adapter" that connects your traces to evaluation logic, whether that's an LLM judge or custom code.

Learn more about [built-in and custom scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>).

### Evaluation in developmentâ

**[`mlflow.genai.evaluate()`](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>)** is MLflow's SDK for systematically evaluating the quality of your application. The evaluation harness takes an evaluation dataset, a set of scorers, and your application's prediction function as input and creates an evaluation run that contains traces with feedback assessments by:

  * Running your app for every record in the evaluation dataset, producing traces.
  * Running each scorer on the resulting traces to assess quality, producing feedback.
  * Attaching each feedback to the appropriate trace.



The evaluation harness is used to iteratively evaluate potential improvements to your application, helping you:

  * Validate if the improvement improved (or regressed) quality.
  * Identify additional improvements to further improve quality.



Learn more about the [evaluation harness](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>), follow the guide to [evaluate your app](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>).

### Evaluation in productionâ

**[`mlflow.genai.Scorer.start()`](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>)** allows you to schedule scorers to automatically evaluate traces from your deployed application. When a scorer is scheduled, the production monitoring service:

  * Runs the scorers on production traces, producing feedback.
  * Attaches each feedback to the source trace.



Production monitoring is used to detect quality issues quickly and identify problematic queries or use cases to improve in development.

  * Learn more about [production monitoring concepts](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>).
  * See the guide to [Monitor GenAI in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>).



## MLflow user interfacesâ

### Review appâ

The review app is a web UI where domain experts label traces with assessments. It presents traces from labeling sessions and collects assessments based on labeling schemas.

### MLflow Experiment UIâ

The MLflow experiment UI provides visual access to many elements of the data model. Using the UI, you can do the following:

  * Search for and view traces.
  * Review feedback and expectations.
  * View and analyze evaluation results.
  * Manage evaluation datasets.
  * Manage versions and prompts.



## Next stepsâ

  * **Get started** : Follow the [quickstart guide](</aws/en/mlflow3/genai/getting-started/>) to trace your first application.
  * **Deep dive** : Explore detailed guides for [tracing](</aws/en/mlflow3/genai/tracing/>), [evaluation](</aws/en/mlflow3/genai/eval-monitor/>), or [human feedback](</aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces>).
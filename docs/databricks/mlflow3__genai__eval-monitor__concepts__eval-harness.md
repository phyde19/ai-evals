<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness -->

On this page

Last updated on **Dec 18, 2025**

# Evaluate GenAI during development

The [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>) function provides an evaluation harness for GenAI applications. Instead of manually running your app and checking outputs one by one, MLflow Evaluation provides a structured way to feed in test data, run your app, and automatically score the results. This makes it easier to compare versions, track improvements, and share results across teams.

MLflow Evaluation connects offline testing with production monitoring. That means the same evaluation logic you use in development can also run in production, giving you a consistent view of quality across the entire AI lifecycle.

The [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>) function systematically tests GenAI app quality by running it against test data ([evaluation datasets](</aws/en/mlflow3/genai/concepts/#evaluation-data>) and applying [scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)).

If you are new to evaluation, start with [10-minute demo: Evaluate a GenAI app](</aws/en/mlflow3/genai/getting-started/eval>).

## When to useâ

  * Nightly or weekly checks of your app against curated evaluation datasets
  * Validating prompt or model changes across app versions
  * Before a release or PR to prevent quality regressions



## Quick referenceâ

The `mlflow.genai.evaluate()` function runs your GenAI app against an evaluation dataset using specified scorers and optionally a prediction function or model ID, returning an `EvaluationResult`.

Python
    
    
    def mlflow.genai.evaluate(  
        data: Union[pd.DataFrame, List[Dict], mlflow.genai.datasets.EvaluationDataset],  # Test data.  
        scorers: list[mlflow.genai.scorers.Scorer],  # Quality metrics, built-in or custom.  
        predict_fn: Optional[Callable[..., Any]] = None,  # App wrapper. Used for direct evaluation only.  
        model_id: Optional[str] = None,  # Optional version tracking.  
    ) -> mlflow.models.evaluation.base.EvaluationResult:  
    

  * For API details, see  Parameters for `mlflow.genai.evaluate()` or the [MLflow documentation](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>).
  * For details on `EvaluationDataset`, see [Building MLflow evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>).
  * For details on evaluation runs and logging, see [Evaluation runs](</aws/en/mlflow3/genai/eval-monitor/concepts/evaluation-runs>).



## Requirementsâ

  1. Install MLflow and required packages.

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.1.0" openai "databricks-connect>=16.1"  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




### (Optional) Configure parallelizationâ

MLflow by default uses background threadpool to speed up the evaluation process. To configure the number of workers, set the environment variable `MLFLOW_GENAI_EVAL_MAX_WORKERS`.

Bash
    
    
    export MLFLOW_GENAI_EVAL_MAX_WORKERS=10  
    

## Evaluation modesâ

There are two evaluation modes:

  * Direct evaluation (recommended). MLflow calls your app directly to generate traces for evaluation:

    1. Runs your app on test inputs, capturing [traces](</aws/en/mlflow3/genai/tracing/>).
    2. Applies [scorers or LLM judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) to assess quality, creating [feedback](</aws/en/mlflow3/genai/human-feedback/dev-annotations>).
    3. Stores results in an [Evaluation Run](</aws/en/mlflow3/genai/eval-monitor/concepts/evaluation-runs>) in the active MLflow experiment.
  * Answer sheet evaluation. You provide pre-computed outputs or existing traces for evaluation:

    1. Applies [scorers or LLM judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) to assess quality on pre-computed outputs or [traces](</aws/en/mlflow3/genai/tracing/>), creating [feedback](</aws/en/mlflow3/genai/human-feedback/dev-annotations>).
    2. Stores results in an [Evaluation Run](</aws/en/mlflow3/genai/eval-monitor/concepts/evaluation-runs>) in the active MLflow experiment.



## Direct evaluation (recommended)â

MLflow calls your GenAI app directly to generate and evaluate traces. You can either pass your application's entry point wrapped in a Python function (`predict_fn`) or, if your app is deployed as a Databricks Model Serving endpoint, pass that endpoint wrapped in [`to_predict_fn`](</aws/en/mlflow3/genai/eval-monitor/eval-examples#eval-endpoint>).

By calling your app directly, this mode enables you to reuse the scorers defined for offline evaluation in [production monitoring](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>) since the resulting traces will be identical.

As shown in the diagram, data, your app, and selected scorers are provided as inputs to `mlflow.genai.evaluate()`, which runs the app and scorers in parallel and records output as traces and feedback.

### Data formats for direct evaluationâ

For schema details, see [Evaluation dataset reference](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-datasets>).

Field| Data type| Required| Description| `inputs`| `dict[Any, Any]`| Yes| Dictionary passed to your `predict_fn`| `expectations`| `dict[str, Any]`| No| Optional ground truth for scorers  
---|---|---|---  
  
### Example using direct evaluationâ

The following code shows an example of how to run the evaluation:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery, Safety  
      
    # Your GenAI app with MLflow tracing  
    @mlflow.trace  
    def my_chatbot_app(question: str) -> dict:  
        # Your app logic here  
        if "MLflow" in question:  
            response = "MLflow is an open-source platform for managing ML and GenAI workflows."  
        else:  
            response = "I can help you with MLflow questions."  
      
        return {"response": response}  
      
    # Evaluate your app  
    results = mlflow.genai.evaluate(  
        data=[  
            {"inputs": {"question": "What is MLflow?"}},  
            {"inputs": {"question": "How do I get started?"}}  
        ],  
        predict_fn=my_chatbot_app,  
        scorers=[RelevanceToQuery(), Safety()]  
    )  
    

You can then view the results in the UI:

### Rate limiting model callsâ

When evaluating models with rate limits (such as third-party APIs or foundation model endpoints), wrap your predict function with rate-limiting logic. This example uses the library `ratelimit`:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery, Safety  
    from ratelimit import limits, sleep_and_retry  
      
    # You can replace this with your own predict_fn  
    predict_fn = mlflow.genai.to_predict_fn("endpoints:/databricks-gpt-oss-20b")  
      
    @sleep_and_retry  
    @limits(calls=10, period=60)  # 10 calls per minute  
    def rate_limited_predict_fn(*args, **kwargs):  
      return predict_fn(*args, **kwargs)  
      
    results = mlflow.genai.evaluate(  
        data=[{"inputs": {"messages": [{"role": "user", "content": "How does MLflow work?"}]}}],  
        predict_fn=predict_fn,  
        scorers=[RelevanceToQuery(), Safety()]  
    )  
    

The above rate limit controls calls to your predict_fn. You can also control the number of workers used to evaluate your agent by configuring parallelization.

## Answer sheet evaluationâ

Use this mode when you can't - or don't want to - run your GenAI app directly during evaluation. For example, you already have outputs (for example, from external systems, historical traces, or batch jobs) and you just want to score them. You provide the inputs and the output, and `evaluate()` runs scorers and logs an evaluation run.

important

If you use an answer sheet with different traces than your production environment, you may need to re-write your scorer functions to use them for [production monitoring](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>).

As shown in the diagram, you provide evaluation data and selected scorers as inputs to `mlflow.genai.evaluate()`. Evaluation data can consist of existing traces, or of inputs and pre-computed outputs. If inputs and pre-computed outputs are provided, `mlflow.genai.evaluate()` constructs traces from the inputs and outputs. For both input options, `mlflow.genai.evaluate()` runs the scorers on the traces and outputs feedback from the scorers.

### Data formats for answer sheet evaluationâ

For schema details, see [Evaluation dataset reference](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-datasets>).

**If inputs and outputs are provided**

Field| Data type| Required| Description| `inputs`| `dict[Any, Any]`| Yes| Original inputs to your GenAI app| `outputs`| `dict[Any, Any]`| Yes| Pre-computed outputs from your app| `expectations`| `dict[str, Any]`| No| Optional ground truth for scorers  
---|---|---|---  
  
**If existing traces are provided**

Field| Data type| Required| Description| `trace`| `mlflow.entities.Trace`| Yes| MLflow Trace objects with inputs/outputs| `expectations`| `dict[str, Any]`| No| Optional ground truth for scorers  
---|---|---|---  
  
### Example using inputs and outputsâ

The following code shows an example of how to run the evaluation:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import Safety, RelevanceToQuery  
      
    # Pre-computed results from your GenAI app  
    results_data = [  
        {  
            "inputs": {"question": "What is MLflow?"},  
            "outputs": {"response": "MLflow is an open-source platform for managing machine learning workflows, including tracking experiments, packaging code, and deploying models."},  
        },  
        {  
            "inputs": {"question": "How do I get started?"},  
            "outputs": {"response": "To get started with MLflow, install it using 'pip install mlflow' and then run 'mlflow ui' to launch the web interface."},  
        }  
    ]  
      
    # Evaluate pre-computed outputs  
    evaluation = mlflow.genai.evaluate(  
        data=results_data,  
        scorers=[Safety(), RelevanceToQuery()]  
    )  
    

You can then view the results in the UI:

### Example using existing tracesâ

The following code shows how to run the evaluation using existing traces:

Python
    
    
    import mlflow  
      
    # Retrieve traces from production  
    traces = mlflow.search_traces(  
        filter_string="trace.status = 'OK'",  
    )  
      
    # Evaluate problematic traces  
    evaluation = mlflow.genai.evaluate(  
        data=traces,  
        scorers=[Safety(), RelevanceToQuery()]  
    )  
    

##  Parameters for `mlflow.genai.evaluate()`â

This section describes each of the parameters used by `mlflow.genai.evaluate()`.

Python
    
    
    def mlflow.genai.evaluate(  
        data: Union[pd.DataFrame, List[Dict], mlflow.genai.datasets.EvaluationDataset],  # Test data.  
        scorers: list[mlflow.genai.scorers.Scorer],  # Quality metrics, built-in or custom.  
        predict_fn: Optional[Callable[..., Any]] = None,  # App wrapper. Used for direct evaluation only.  
        model_id: Optional[str] = None,  # Optional version tracking.  
    ) -> mlflow.models.evaluation.base.EvaluationResult:  
    

### `data`â

The evaluation dataset must be in one of the following formats:

  * `EvaluationDataset` (recommended).
  * List of dictionaries, Pandas DataFrame, or Spark DataFrame.



If the data argument is provided as a DataFrame or list of dictionaries, it must follow the following schema. This is consistent with the schema used by [EvaluationDataset](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>). Databricks recommends using an `EvaluationDataset` as it enforces schema validation, in addition to tracking the lineage of each record.

Field| Data type| Description| Use with direct evaluation| Use with answer sheet| `inputs`| `dict[Any, Any]`| A `dict` that is passed to your `predict_fn` using `**kwargs`. Must be JSON serializable. Each key must correspond to a named argument in `predict_fn`.| Required| Either `inputs` \+ `outputs` or `trace` is required. Cannot pass both.Derived from `trace` if not provided.| `outputs`| `dict[Any, Any]`| A `dict` with the outputs of your GenAI app for the corresponding `input`. Must be JSON serializable.| Must **not** be provided, generated by MLflow from the Trace.| Either `inputs` \+ `outputs` or `trace` is required. Cannot pass both.Derived from `trace` if not provided.| `expectations`| `dict[str, Any]`| A `dict` with ground-truth labels corresponding to `input`. Used by `scorers` to check quality. Must be JSON serializable and each key must be a `str`.| Optional| Optional| `trace`| `mlflow.entities.Trace`| The trace object for the request. If the `trace` is provided, the `expectations` can be provided as [`Assessment`](</aws/en/mlflow3/genai/tracing/collect-user-feedback/>)s on the `trace` rather than as a separate column.| Must **not** be provided, generated by MLflow from the Trace.| Either `inputs` \+ `outputs` or `trace` is required. Cannot pass both.  
---|---|---|---|---  
  
### `scorers`â

List of quality metrics to apply. You can provide:

  * [Built-in scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)
  * [Custom scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>)



See [Scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) for more details.

### `predict_fn`â

The GenAI app's entry point. This parameter is only used with direct evaluation. `predict_fn` must meet the following requirements:

  * Accept the keys from the `inputs` dictionary in `data` as keyword arguments.
  * Return a JSON-serializable dictionary.
  * Be instrumented with [MLflow Tracing](</aws/en/mlflow3/genai/tracing/>).
  * Emit exactly one trace per call.



### `model_id`â

Optional model identifier to link results to your app version (for example, `"models:/my-app/1"`). See [Version Tracking](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>) for more details.

## Next stepsâ

  * [Evaluate your app](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) \- Step-by-step guide to running your first evaluation.
  * [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) \- Create structured test data from production logs or scratch.
  * [Define custom scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>) \- Build metrics tailored to your specific use case.
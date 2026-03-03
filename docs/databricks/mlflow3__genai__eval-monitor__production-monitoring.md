<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/production-monitoring -->

On this page

Last updated on **Feb 10, 2026**

# Monitor GenAI in production

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

Production monitoring for GenAI on Databricks lets you automatically run MLflow 3 scorers on traces from your production GenAI apps to continuously monitor quality.

You can schedule scorers to automatically evaluate a sample of your production traffic. Scorer assessment results are automatically attached as feedback to evaluated traces.

Production monitoring includes the following:

  * Automated quality assessment using built-in or custom scorers.
  * Configurable sampling rates so you can control the tradeoff between coverage and computational cost.
  * Use the same scorers in development and production to ensure consistent evaluation.
  * Continuous quality assessment with monitoring running in the background.



note

MLflow 3 production monitoring is compatible with traces logged from MLflow 2.

For information about legacy production monitoring, see [Production monitoring API reference (legacy)](</aws/en/mlflow3/genai/eval-monitor/concepts/production-monitoring>).

## Prerequisitesâ

Before setting up quality monitoring, ensure you have:

  * **MLflow Experiment** : An MLflow experiment where traces are being logged. If no experiment is specified, the active experiment is used.
  * **Instrumented production application** : Your GenAI app must be logging traces using MLflow Tracing. See the [Production Tracing guide](</aws/en/mlflow3/genai/tracing/prod-tracing>).
  * **Defined scorers** : Tested [scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) that work with your application's trace format. If you used your production app as the `predict_fn` in `mlflow.genai.evaluate()` during development, your scorers are likely already compatible.


  * **SQL warehouse ID (for Unity Catalog traces)**: If your traces are stored in Unity Catalog, you must configure a SQL warehouse ID for monitoring to work. See [Enable production monitoring](</aws/en/mlflow3/genai/tracing/trace-unity-catalog#enable-production-monitoring>).



## Get started with production monitoringâ

This section includes example code showing how to create the different types of scorers.

For more information about scorers, see the following:

  * [Scorers and LLM judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)
  * [Custom judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>)
  * [Create custom code-based scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>)



note

At any given time, at most 20 scorers can be associated with an experiment for continuous quality monitoring.

### Create and schedule LLM judges using the UIâ

You can use the MLflow UI to create and test scorers based on LLM judges.

  1. Navigate to the **Scorers** tab in the MLflow Experiment UI.
  2. Click **New Scorer**.
  3. Select your built-in LLM judge from the **LLM Template** drop-down menu.
  4. (Optional) Click **Run Scorer** to run on a subset of your traces.
  5. (Optional) Adjust **Evaluation settings** for production monitoring on future traces.
  6. Click **Create scorer**.



### Use built-in LLM judgesâ

MLflow provides several [built-in LLM judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) that you can use out-of-the-box for monitoring.

Python
    
    
    from mlflow.genai.scorers import Safety, ScorerSamplingConfig  
      
    # Register the scorer with a name and start monitoring  
    safety_judge = Safety().register(name="my_safety_judge")  # name must be unique to experiment  
    safety_judge = safety_judge.start(sampling_config=ScorerSamplingConfig(sample_rate=0.7))  
    

By default, each judge uses a Databricks-hosted LLM designed to perform GenAI quality assessments. You can change the judge model to instead use a Databricks model serving endpoint by using the `model` argument in the scorer definition. The model must be specified in the format `databricks:/<databricks-serving-endpoint-name>`.

Python
    
    
    safety_judge = Safety(model="databricks:/databricks-gpt-oss-20b").register(name="my_custom_safety_judge")  
    

### Use Guidelines LLM Judgesâ

[Guidelines LLM Judges](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/guidelines>) evaluate inputs and outputs using pass/fail natural language criteria.

Python
    
    
    from mlflow.genai.scorers import Guidelines  
      
    # Create and register the guidelines scorer  
    english_judge = Guidelines(  
      name="english",  
      guidelines=["The response must be in English"]  
    ).register(name="is_english")  # name must be unique to experiment  
      
    # Start monitoring with the specified sample rate  
    english_judge = english_judge.start(sampling_config=ScorerSamplingConfig(sample_rate=0.7))  
    

Like built-in judges, you can change the judge model to instead use a Databricks model serving endpoint.

Python
    
    
    english_judge = Guidelines(  
      name="english",  
      guidelines=["The response must be in English"],  
      model="databricks:/databricks-gpt-oss-20b",  
    ).register(name="custom_is_english")  
    

### Use LLM Judges with custom promptsâ

For more flexibility than Guidelines judges, use [LLM Judges with custom prompts](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>) which allow for multi-level quality assessment with customizable choice categories.

Python
    
    
    from typing import Literal  
    from mlflow.genai import make_judge  
    from mlflow.genai.scorers import ScorerSamplingConfig  
      
    # Create a custom judge using make_judge  
    formality_judge = make_judge(  
        name="formality",  
        instructions="""You will look at the response and determine the formality of the response.  
      
    Request: {{ inputs }}  
    Response: {{ outputs }}  
      
    Evaluate whether the response is formal, somewhat formal, or not formal.  
    A response is somewhat formal if it mentions friendship, etc.""",  
        feedback_value_type=Literal["formal", "semi_formal", "not_formal"],  
        model="databricks:/databricks-gpt-oss-20b",  # optional  
    )  
      
    # Register the custom judge and start monitoring  
    registered_judge = formality_judge.register(name="my_formality_judge")  # name must be unique to experiment  
    registered_judge = registered_judge.start(sampling_config=ScorerSamplingConfig(sample_rate=0.1))  
    

### Use custom scorer functionsâ

For maximum flexibility, define and use a [custom scorer function](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>).

When defining custom scorers, do not use type hints that need to be imported in the function signature. If the scorer function body uses packages that need to be imported, import these packages inline within the function to ensure proper serialization.

Some packages are available by default without the need for an inline import. These include `databricks-agents`, `mlflow-skinny`, `openai`, and all packages included in [Serverless environment version 2](</aws/en/release-notes/serverless/environment-version/two>).

Python
    
    
    from mlflow.genai.scorers import scorer, ScorerSamplingConfig  
      
      
    # Custom metric: Check if response mentions Databricks  
    @scorer  
    def mentions_databricks(outputs):  
        """Check if the response mentions Databricks"""  
        return "databricks" in str(outputs.get("response", "")).lower()  
      
    # Custom metric: Response length check  
    @scorer(aggregations=["mean", "min", "max"])  
    def response_length(outputs):  
        """Measure response length in characters"""  
        return len(str(outputs.get("response", "")))  
      
    # Custom metric with multiple inputs  
    @scorer  
    def response_relevance_score(inputs, outputs):  
        """Score relevance based on keyword matching"""  
        query = str(inputs.get("query", "")).lower()  
        response = str(outputs.get("response", "")).lower()  
      
        # Simple keyword matching (replace with your logic)  
        query_words = set(query.split())  
        response_words = set(response.split())  
      
        if not query_words:  
            return 0.0  
      
        overlap = len(query_words & response_words)  
        return overlap / len(query_words)  
      
    # Register and start monitoring custom scorers  
    databricks_scorer = mentions_databricks.register(name="databricks_mentions")  
    databricks_scorer = databricks_scorer.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  
      
    length_scorer = response_length.register(name="response_length")  
    length_scorer = length_scorer.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))  
      
    relevance_scorer = response_relevance_score.register(name="response_relevance_score")  # name must be unique to experiment  
    relevance_scorer = relevance_scorer.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))  
    

### Multiple scorer configurationâ

For comprehensive monitoring setup, register and start multiple scorers individually.

Python
    
    
    from mlflow.genai.scorers import Safety, Guidelines, ScorerSamplingConfig, list_scorers  
      
    # # Register multiple scorers for comprehensive monitoring  
    safety_judge = Safety().register(name="safety") # name must be unique within an MLflow experiment  
    safety_judge = safety_judge.start(  
        sampling_config=ScorerSamplingConfig(sample_rate=1.0), # Check all traces  
    )  
      
    guidelines_judge = Guidelines(  
        name="english",  
        guidelines=["Response must be in English"]  
    ).register(name="english_check")  
    guidelines_judge = guidelines_judge.start(  
        sampling_config=ScorerSamplingConfig(sample_rate=0.5), # Sample 50%  
    )  
      
    # List and manage all scorers  
    all_scorers = list_scorers()  
    for scorer in all_scorers:  
        if scorer.sample_rate > 0:  
            print(f"{scorer.name} is active")  
        else:  
            print(f"{scorer.name} is stopped")  
    

## Scorer lifecycleâ

Scorer lifecycles are centered around MLflow experiments. The following table lists the scorer lifecycle states.

Scorers are _immutable_ , so a lifecycle operation does not modify the original scorer. Instead, it returns a new scorer instance.

State| Description| API| Unregistered| Scorer function is defined but is not known to the server.| | Registered| Scorer is registered to the active MLflow experiment.| [`.register()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.register>)| Active| Scorer is running with a sample rate > 0.| [`.start()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.start>)| Stopped| Scorer is registered but not running (sample rate = 0).| [`.stop()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.Scorer.stop>)| Deleted| The scorer has been removed from the server and is no longer associated with its MLflow experiment.| [`delete_scorer()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.delete_scorer>)  
---|---|---  
  
### Basic scorer lifecycleâ

Python
    
    
    from mlflow.genai.scorers import Safety, scorer, ScorerSamplingConfig  
      
    # Built-in scorer lifecycle  
    safety_judge = Safety().register(name="safety_check")  
    safety_judge = safety_judge.start(  
        sampling_config=ScorerSamplingConfig(sample_rate=1.0),  
    )  
    safety_judge = safety_judge.update(  
        sampling_config=ScorerSamplingConfig(sample_rate=0.8),  
    )  
    safety_judge = safety_judge.stop()  
    delete_scorer(name="safety_check")  
      
    # Custom scorer lifecycle  
    @scorer  
    def response_length(outputs):  
        return len(str(outputs.get("response", "")))  
      
    length_scorer = response_length.register(name="length_check")  
    length_scorer = length_scorer.start(  
        sampling_config=ScorerSamplingConfig(sample_rate=0.5),  
    )  
    

## Manage scorersâ

The following APIs are available to manage scorers.

API| Description| Example| [`list_scorers()`](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring#list-scorers>)| List all registered scorers for the current experiment.|  List current scorers| [`get_scorer()`](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring#get-scorer>)| Retrieve a registered scorer by name.|  Get and update a scorer| [`Scorer.update()`](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring#update>)| Modify the sampling configuration of an active scorer. This is an immutable operation.|  Get and update a scorer| [`backfill_scorer()`](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring#backfill-scorers>)| Retroactively apply new or updated metrics to historical traces.|  Evaluate historical traces (metric backfill)| [`delete_scorer()`](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring#delete-scorers>)| Delete a registered scorer by name.|  Stop and delete scorers  
---|---|---  
  
###  List current scorersâ

To view all registered scorers for your experiment:

Python
    
    
    from mlflow.genai.scorers import list_scorers  
      
    # List all registered scorers  
    scorers = list_scorers()  
    for scorer in scorers:  
        print(f"Name: {scorer._server_name}")  
        print(f"Sample rate: {scorer.sample_rate}")  
        print(f"Filter: {scorer.filter_string}")  
        print("---")  
    

###  Get and update a scorerâ

To modify existing scorer configurations:

Python
    
    
    from mlflow.genai.scorers import get_scorer  
      
    # Get existing scorer and update its configuration (immutable operation)  
    safety_judge = get_scorer(name="safety_monitor")  
    updated_judge = safety_judge.update(sampling_config=ScorerSamplingConfig(sample_rate=0.8))  # Increased from 0.5  
      
    # Note: The original scorer remains unchanged; update() returns a new scorer instance  
    print(f"Original sample rate: {safety_judge.sample_rate}")  # Original rate  
    print(f"Updated sample rate: {updated_judge.sample_rate}")   # New rate  
    

###  Stop and delete scorersâ

To stop monitoring or remove a scorer entirely:

Python
    
    
    from mlflow.genai.scorers import get_scorer, delete_scorer  
      
    # Get existing scorer  
    databricks_scorer = get_scorer(name="databricks_mentions")  
      
    # Stop monitoring (sets sample_rate to 0, keeps scorer registered)  
    stopped_scorer = databricks_scorer.stop()  
    print(f"Sample rate after stop: {stopped_scorer.sample_rate}")  # 0  
      
    # Remove scorer entirely from the server  
    delete_scorer(name=databricks_scorer.name)  
      
    # Or restart monitoring from a stopped scorer  
    restarted_scorer = stopped_scorer.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  
    

### Immutable updatesâ

Scorers, including LLM Judges, are immutable objects. When you update a scorer, you do not modify the original scorer. Instead, an updated copy of the scorer is created. This immutability helps ensure that scorers meant for production are not accidentally modified. The following code snippet shows how immutable updates work.

Python
    
    
    # Demonstrate immutability  
    original_judge = Safety().register(name="safety")  
    original_judge = original_judge.start(  
       sampling_config=ScorerSamplingConfig(sample_rate=0.3),  
    )  
      
    # Update returns new instance  
    updated_judge = original_judge.update(  
        sampling_config=ScorerSamplingConfig(sample_rate=0.8),  
    )  
      
    # Original remains unchanged  
    print(f"Original: {original_judge.sample_rate}")  # 0.3  
    print(f"Updated: {updated_judge.sample_rate}")    # 0.8  
    

##  Evaluate historical traces (metric backfill)â

You can retroactively apply new or updated metrics to historical traces.

### Basic metric backfill using current sample ratesâ

Python
    
    
    from databricks.agents.scorers import backfill_scorers  
      
    safety_judge = Safety()  
    safety_judge.register(name="safety_check")  
    safety_judge.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  
      
    #custom scorer  
    @scorer(aggregations=["mean", "min", "max"])  
    def response_length(outputs):  
        """Measure response length in characters"""  
        return len(outputs)  
      
    response_length.register(name="response_length")  
    response_length.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  
      
    # Use existing sample rates for specified scorers  
    job_id = backfill_scorers(  
        scorers=["safety_check", "response_length"]  
    )  
    

### Metric backfill using custom sample rates and time rangeâ

Python
    
    
    from databricks.agents.scorers import backfill_scorers, BackfillScorerConfig  
    from datetime import datetime  
    from mlflow.genai.scorers import Safety, Correctness  
      
    safety_judge = Safety()  
    safety_judge.register(name="safety_check")  
    safety_judge.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  
      
    #custom scorer  
    @scorer(aggregations=["mean", "min", "max"])  
    def response_length(outputs):  
        """Measure response length in characters"""  
        return len(outputs)  
      
    response_length.register(name="response_length")  
    response_length.start(sampling_config=ScorerSamplingConfig(sample_rate=0.5))  
      
    # Define custom sample rates for backfill  
    custom_scorers = [  
        BackfillScorerConfig(scorer=safety_judge, sample_rate=0.8),  
        BackfillScorerConfig(scorer=response_length, sample_rate=0.9)  
    ]  
      
    job_id = backfill_scorers(  
        experiment_id=YOUR_EXPERIMENT_ID,  
        scorers=custom_scorers,  
        start_time=datetime(2024, 6, 1),  
        end_time=datetime(2024, 6, 30)  
    )  
    

### Recent data backfillâ

Python
    
    
    from datetime import datetime, timedelta  
      
    # Backfill last week's data with higher sample rates  
    one_week_ago = datetime.now() - timedelta(days=7)  
      
    job_id = backfill_scorers(  
        scorers=[  
            BackfillScorerConfig(scorer=safety_judge, sample_rate=0.8),  
            BackfillScorerConfig(scorer=response_length, sample_rate=0.9)  
        ],  
        start_time=one_week_ago  
    )  
    

## View resultsâ

After scheduling scorers, allow 15-20 minutes for initial processing. Then:

  1. Navigate to your MLflow experiment.
  2. Open the **Traces** tab to see assessments attached to traces.
  3. Use the monitoring dashboards to track quality trends.



## Best practicesâ

### Scorer state managementâ

  * Check the scorer state before operations using `sample_rate`.
  * Use the immutable pattern. Assign the results of `.start()`, `.update()`, `.stop()` to variables.
  * Understand the scorer lifecycle. `.stop()` preserves registration, `delete_scorer()` removes the scorer entirely.



### Metric backfillâ

  * Start small. Begin with smaller time ranges to estimate job duration and resource usage.
  * Use appropriate sample rates. Consider the cost and time implications of using high sample rates.



### Sampling strategyâ

  * For critical scorers such as safety and security checks, use `sample_rate=1.0`.

  * For expensive scorers, such as complex LLM judges, use lower sample rates (0.05-0.2).

  * For iterative improvement during development, use moderate rates (0.3-0.5).

  * Balance coverage with cost, as shown in the following examples:

Python
        
        # High-priority scorers: higher sampling  
        safety_judge = Safety().register(name="safety")  
        safety_judge = safety_judge.start(sampling_config=ScorerSamplingConfig(sample_rate=1.0))  # 100% coverage for critical safety  
          
        # Expensive scorers: lower sampling  
        complex_scorer = ComplexCustomScorer().register(name="complex_analysis")  
        complex_scorer = complex_scorer.start(sampling_config=ScorerSamplingConfig(sample_rate=0.05))  # 5% for expensive operations  
        




### Custom scorer designâ

Keep custom scorers self-contained, as shown in the following example:

Python
    
    
    @scorer  
    def well_designed_scorer(inputs, outputs):  
        # All imports inside the function  
        import re  
        import json  
      
        # Handle missing data gracefully  
        response = outputs.get("response", "")  
        if not response:  
            return 0.0  
      
        # Return consistent types  
        return float(len(response) > 100)  
    

## Troubleshootingâ

### Scorers not runningâ

If scorers aren't executing, check the following:

  1. **Check experiment** : Ensure that traces are logged to the experiment, not to individual runs.
  2. **Sampling rate** : With low sample rates, it might take time to see results.
  3. **Verify filter string** : Ensure your `filter_string` matches actual traces.



### Serialization issuesâ

When you create a custom scorer, include imports in the function definition.

Python
    
    
    # â Avoid external dependencies  
    import external_library  # Outside function  
      
    @scorer  
    def bad_scorer(outputs):  
        return external_library.process(outputs)  
      
    # â Include imports in the function definition  
    @scorer  
    def good_scorer(outputs):  
        import json  # Inside function  
        return len(json.dumps(outputs))  
      
    # â Avoid using type hints in scorer function signature that requires imports  
    from typing import List  
      
    @scorer  
    def scorer_with_bad_types(outputs: List[str]):  
        return False  
    

### Metric backfill issuesâ

**"Scheduled scorer 'X' not found in experiment"**

  * Ensure the scorer name matches a registered scorer in your experiment.
  * Check available scorers using `list_scorers` method.



## Archive tracesâ

You can save traces and their associated assessments to a Unity Catalog Delta table for long-term storage and advanced analysis. This is useful for building custom dashboards, performing in-depth analytics on trace data, and maintaining a durable record of your application's behavior.

note

You must have the necessary permissions to write to the specified Unity Catalog Delta table. The target table will be created if it does not already exist.

If the table already exists, traces are appended to it.

### Enable archiving tracesâ

  * MLflow API
  * Databricks UI



To begin archiving traces for an experiment, use the `enable_databricks_trace_archival` function. You must specify the full name of the target Delta table, including catalog and schema. If you don't provide an `experiment_id`, archiving traces is enabled for the currently active experiment.

Python
    
    
    from mlflow.tracing.archival import enable_databricks_trace_archival  
      
    # Archive traces from a specific experiment to a Unity Catalog Delta table  
    enable_databricks_trace_archival(  
        delta_table_fullname="my_catalog.my_schema.archived_traces",  
        experiment_id="YOUR_EXPERIMENT_ID",  
    )  
    

Stop archiving traces for an experiment at any time by using the `disable_databricks_trace_archival` function.

Python
    
    
    from mlflow.tracing.archival import disable_databricks_trace_archival  
      
    # Stop archiving traces for the specified experiment  
    disable_databricks_trace_archival(experiment_id="YOUR_EXPERIMENT_ID")  
    

To archive traces for an experiment in the UI:

  1. Go to Experiments page in the Databrick workspace.
  2. Click **Delta sync: Not enabled**.
  3. Specify the full name of the target Delta table, including catalog and schema.



To disable trace archiving:

  1. Go to Experiments page in the Databrick workspace.
  2. Click **Delta sync: Enabled** > **Disable syncing**.



## Next stepsâ

  * [Create custom scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>) \- Build scorers tailored to your needs.
  * [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) \- Use monitoring results to improve quality.



## Reference guidesâ

  * [Scorer lifecycle management API reference](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>) \- API and examples for managing scorers for monitoring.
  * [Scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) \- Understand the metrics that power monitoring.
  * [Evaluation Harness](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>) \- How offline evaluation relates to production.
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring -->

On this page

Last updated on **Sep 30, 2025**

# Scorer lifecycle management API reference

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

This page describes the methods used to implement production monitoring. For a guide to production monitoring on Databricks, see [Monitor GenAI in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>).

## Scorer instance methodsâ

### `Scorer.register()`â

**API Reference:** [`Scorer.register`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer.register>)

Register a custom scorer function with the server. Used for scorers created with the [`@scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.scorer>) decorator.

Python
    
    
    @scorer  
    def custom_scorer(outputs):  
        return len(str(outputs.get("response", "")))  
      
    # Register the custom scorer  
    my_scorer = custom_scorer.register(name="response_length")  
    

**Parameters:**

  * `name` (str): Unique name for the scorer within the experiment. Defaults to the existing name of the scorer.



**Returns:** New [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) instance with server registration

### `Scorer.start()`â

**API Reference:** [`Scorer.start`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer.start>)

Begin online evaluation with the specified sampling configuration.

Python
    
    
    from mlflow.genai.scorers import ScorerSamplingConfig  
      
    # Start monitoring with sampling  
    active_scorer = registered_scorer.start(  
        sampling_config=ScorerSamplingConfig(  
            sample_rate=0.5,  
            filter_string="trace.status = 'OK'"  
        ),  
    )  
    

**Parameters:**

  * `name` (str): Name of the scorer. If not provided, defaults to the current name of the scorer.
  * `sampling_config` ([`ScorerSamplingConfig`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.ScorerSamplingConfig>)): Trace sampling configuration
    * `sample_rate` (float): Fraction of traces to evaluate (0.0-1.0). Default: 1.0
    * `filter_string` (str, optional): MLflow-compatible filter for trace selection



**Returns:** New [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) instance in active state

###  `Scorer.update()`â

**API Reference:** [`Scorer.update`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer.update>)

Modify the sampling configuration of an active scorer. This is an immutable operation.

Python
    
    
    # Update sampling rate (returns new scorer instance)  
    updated_scorer = active_scorer.update(  
        sampling_config=ScorerSamplingConfig(  
            sample_rate=0.8,  
        ),  
    )  
      
    # Original scorer remains unchanged  
    print(f"Original: {active_scorer.sample_rate}")  # 0.5  
    print(f"Updated: {updated_scorer.sample_rate}")   # 0.8  
    

**Parameters:**

  * `name` (str): Name of the scorer. If not provided, defaults to the current name of the scorer.
  * `sampling_config` ([`ScorerSamplingConfig`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.ScorerSamplingConfig>)): Trace sampling configuration
    * `sample_rate` (float): Fraction of traces to evaluate (0.0-1.0). Default: 1.0
    * `filter_string` (str, optional): MLflow-compatible filter for trace selection



**Returns:** New [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) instance with updated configuration

### `Scorer.stop()`â

**API Reference:** [`Scorer.stop`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer.stop>)

Stop online evaluation by setting sample rate to 0. Keeps the scorer registered.

Python
    
    
    # Stop monitoring but keep scorer registered  
    stopped_scorer = active_scorer.stop()  
    print(f"Sample rate: {stopped_scorer.sample_rate}")  # 0  
    

**Parameters:**

  * `name` (str): Name of the scorer. If not provided, defaults to the current name of the scorer.



**Returns:** New [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) instance with sample_rate=0

## Scorer registry functionsâ

###  `mlflow.genai.scorers.get_scorer()`â

**API Reference:** [`get_scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.get_scorer>)

Retrieve a registered scorer by name.

Python
    
    
    from mlflow.genai.scorers import get_scorer  
      
    # Get existing scorer by name  
    existing_scorer = get_scorer(name="safety_monitor")  
    print(f"Current sample rate: {existing_scorer.sample_rate}")  
    

**Parameters:**

  * `name` (str): Name of the registered scorer



**Returns:** [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) instance

### `mlflow.genai.scorers.list_scorers()`â

**API Reference:** [`list_scorers`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.list_scorers>)

List all registered scorers for the current experiment.

Python
    
    
    from mlflow.genai.scorers import list_scorers  
      
    # List all registered scorers  
    all_scorers = list_scorers()  
    for scorer in all_scorers:  
        print(f"Name: {scorer._server_name}")  
        print(f"Sample rate: {scorer.sample_rate}")  
        print(f"Filter: {scorer.filter_string}")  
    

**Returns:** List of [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) instances

###  `mlflow.genai.scorers.delete_scorer()`â

**API Reference:** [`delete_scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.delete_scorer>)

Delete a registered scorer by name.

Python
    
    
    from mlflow.genai.scorers import delete_scorer  
      
    # Delete existing scorer by name  
    delete_scorer(name="safety_monitor")  
    

**Parameters:**

  * `name` (str): Name of the registered scorer



**Returns:** None

## Scorer propertiesâ

### `Scorer.sample_rate`â

Current sampling rate (0.0-1.0). Returns 0 for stopped scorers.

Python
    
    
    print(f"Sampling {scorer.sample_rate * 100}% of traces")  
    

### `Scorer.filter_string`â

Current trace filter string for MLflow trace selection.

Python
    
    
    print(f"Filter: {scorer.filter_string}")  
    

## Configuration classesâ

### `ScorerSamplingConfig`â

**API Reference:** [`ScorerSamplingConfig`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.ScorerSamplingConfig>)

Data class that holds sampling configuration for a scorer.

Python
    
    
    from mlflow.genai import ScorerSamplingConfig  
      
    config = ScorerSamplingConfig(  
        sample_rate=0.5,  
        filter_string="trace.status = 'OK'"  
    )  
    

**Attributes:**

  * `sample_rate` (float, optional): Sampling rate between 0.0 and 1.0
  * `filter_string` (str, optional): MLflow trace filter



##  Metric backfillâ

### `backfill_scorers()`â

Python
    
    
    from databricks.agents.scorers import backfill_scorers, BackfillScorerConfig  
      
    job_id = backfill_scorers(  
        experiment_id="your-experiment-id",  
        scorers=[  
            BackfillScorerConfig(scorer=safety_scorer, sample_rate=0.8),  
            BackfillScorerConfig(scorer=response_length, sample_rate=0.9)  
        ],  
        start_time=datetime(2024, 1, 1),  
        end_time=datetime(2024, 1, 31)  
    )  
    

**Parameters:**

All parameters are keyword-only.

  * **`experiment_id`** _(str, optional)_ : The ID of the experiment to backfill. If not provided, uses the current experiment context
  * **`scorers`** _(Union[List[BackfillScorerConfig], List[str]], required)_ : List of `BackfillScorerConfig` objects with custom sample rates (if sample_rate is not provided in BackfillScorerConfig, defaults to the registered scorer's sample rate), OR list of scorer names (strings) to use current sample rates from the experiment's scheduled scorers. Cannot be empty.
  * **`start_time`** _(datetime, optional)_ : Start time for backfill evaluation. If not provided, no start time constraint is applied
  * **`end_time`** _(datetime, optional)_ : End time for backfill evaluation. If not provided, no end time constraint is applied



**Returns:** Job ID of the created backfill job for status tracking (str)
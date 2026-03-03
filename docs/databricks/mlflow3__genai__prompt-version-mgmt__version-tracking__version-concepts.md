<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/version-concepts -->

On this page

Last updated on **Oct 24, 2025**

# Version tracking and `LoggedModel`

MLflow version tracking enables you to create versioned representations of your GenAI applications. Versioning provides the following benefits:

  * Reproducibility and auditability. Each app or model version links to its specific code, such as the Git commit hash, and its configuration.
  * Help with debugging. Compare code, configurations, evaluation results, and traces between model versions.
  * Systematic evaluation. Use [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>) to compare metrics like quality scores, cost, and latency side-by-side.



To create an app or model version, you use a `LoggedModel`. In MLflow, a `LoggedModel` represents a specific version of your GenAI application. Each distinct state of your application that you want to evaluate, deploy, or refer back to can be captured as a new `LoggedModel`.

This page is an introduction to MLflow version tracking. For a step-by-step tutorial, see [Track versions of Git-based applications with MLflow](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>).

## Methods for version trackingâ

MLflow provides two methods for version tracking:

  * [`mlflow.set_active_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_active_model>): Simple version tracking. Automatically creates a `LoggedModel` if needed and links subsequent traces.
  * [`mlflow.create_external_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.create_external_model>): Full control over version creation. You can provide extensive metadata, parameters, and tags.



### `set_active_model`â

Links traces to a specific `LoggedModel` version. If a model with the given name doesn't exist, it automatically creates one.

Python
    
    
    def set_active_model(  
        name: Optional[str] = None,  
        model_id: Optional[str] = None  
    ) -> ActiveModel:  
    

#### Parametersâ

Parameter| Type| Required| Description| `name`| `str | None`| No*| Name of the model. If model doesn't exist, creates a new one| `model_id`| `str | None`| No*| ID of an existing LoggedModel  
---|---|---|---  
  
*Either `name` or `model_id` must be provided.

#### Return Valueâ

Returns an `ActiveModel` object (subclass of `LoggedModel`) that can be used as a context manager.

#### Example Usageâ

Python
    
    
    import mlflow  
      
    # Simple usage - creates model if it doesn't exist  
    mlflow.set_active_model(name="my-agent-v1.0")  
      
    # Use as context manager  
    with mlflow.set_active_model(name="my-agent-v2.0") as model:  
        print(f"Model ID: {model.model_id}")  
        # Traces within this context are linked to this model  
      
    # Use with existing model ID  
    mlflow.set_active_model(model_id="existing-model-id")  
    

### `create_external_model`â

Creates a new `LoggedModel` for applications whose code and artifacts are stored outside MLflow (e.g., in Git).

Python
    
    
    def create_external_model(  
        name: Optional[str] = None,  
        source_run_id: Optional[str] = None,  
        tags: Optional[dict[str, str]] = None,  
        params: Optional[dict[str, str]] = None,  
        model_type: Optional[str] = None,  
        experiment_id: Optional[str] = None,  
    ) -> LoggedModel:  
    

#### Parametersâ

Parameter| Type| Required| Description| `name`| `str | None`| No| Model name. If not specified, a random name is generated| `source_run_id`| `str | None`| No| ID of the associated run. Defaults to active run ID if within a run context| `tags`| `dict[str, str] | None`| No| Key-value pairs for organization and filtering| `params`| `dict[str, str] | None`| No| Model parameters and configuration (must be strings)| `model_type`| `str | None`| No| User-defined type for categorization (e.g., "agent", "rag-system")| `experiment_id`| `str | None`| No| Experiment to associate with. Uses active experiment if not specified  
---|---|---|---  
  
#### Return Valueâ

Returns a `LoggedModel` object with:

  * `model_id`: Unique identifier for the model
  * `name`: The assigned model name
  * `experiment_id`: Associated experiment ID
  * `creation_timestamp`: When the model was created
  * `status`: Model status (always "READY" for external models)
  * `tags`: Dictionary of tags
  * `params`: Dictionary of parameters



#### Example Usageâ

Python
    
    
    import mlflow  
      
    # Basic usage  
    model = mlflow.create_external_model(  
        name="customer-support-agent-v1.0"  
    )  
      
    # With full metadata  
    model = mlflow.create_external_model(  
        name="recommendation-engine-v2.1",  
        model_type="rag-agent",  
        params={  
            "llm_model": "gpt-4",  
            "temperature": "0.7",  
            "max_tokens": "1000",  
            "retrieval_k": "5"  
        },  
        tags={  
            "team": "ml-platform",  
            "environment": "staging",  
            "git_commit": "abc123def"  
        }  
    )  
      
    # Within a run context  
    with mlflow.start_run() as run:  
        model = mlflow.create_external_model(  
            name="my-agent-v3.0",  
            source_run_id=run.info.run_id  
        )  
    

## LoggedModel Classâ

The `LoggedModel` class represents a versioned model in MLflow.

### Propertiesâ

Property| Type| Description| `model_id`| `str`| Unique identifier for the model| `name`| `str`| Model name| `experiment_id`| `str`| Associated experiment ID| `creation_timestamp`| `int`| Creation time (milliseconds since epoch)| `last_updated_timestamp`| `int`| Last update time (milliseconds since epoch)| `model_type`| `str | None`| User-defined model type| `source_run_id`| `str | None`| ID of the run that created this model| `status`| `LoggedModelStatus`| Model status (READY, FAILED_REGISTRATION, etc.)| `tags`| `dict[str, str]`| Dictionary of tags| `params`| `dict[str, str]`| Dictionary of parameters| `model_uri`| `str`| URI for referencing the model (e.g., "models:/model_id")  
---|---|---  
  
## Common Patternsâ

### Version Tracking with Git Integrationâ

Python
    
    
    import mlflow  
    import subprocess  
      
    # Get current git commit  
    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()[:8]  
      
    # Create versioned model name  
    model_name = f"my-app-git-{git_commit}"  
      
    # Track the version  
    model = mlflow.create_external_model(  
        name=model_name,  
        tags={"git_commit": git_commit}  
    )  
    

### Linking Traces to Versionsâ

Python
    
    
    import mlflow  
      
    # Set active model - all subsequent traces will be linked  
    mlflow.set_active_model(name="my-agent-v1.0")  
      
    # Your application code with tracing  
    @mlflow.trace  
    def process_request(query: str):  
        # This trace will be automatically linked to my-agent-v1.0  
        return f"Processing: {query}"  
      
    # Run the application  
    result = process_request("Hello world")  
    

### Production Deploymentâ

In production, use environment variables instead of calling `set_active_model()`:

Bash
    
    
    # Set the model ID that traces should be linked to  
    export MLFLOW_ACTIVE_MODEL_ID="my-agent-v1.0"  
    

## Best Practicesâ

  1. **Use semantic versioning** in model names (e.g., "app-v1.2.3")
  2. **Include git commits** in tags for traceability
  3. **Parameters must be strings** \- convert numbers and booleans
  4. **Use model_type** to categorize similar applications
  5. **Set active model before tracing** to ensure proper linkage



## Common Issuesâ

**Invalid parameter types** :

Python
    
    
    # Error: Parameters must be strings  
    # Wrong:  
    params = {"temperature": 0.7, "max_tokens": 1000}  
      
    # Correct:  
    params = {"temperature": "0.7", "max_tokens": "1000"}  
    

## Next stepsâ

  * [Track application versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>) \- Step-by-step guide to version your GenAI app
  * [Link production traces](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/link-production-traces-to-app-versions>) \- Connect production data to app versions
  * [Package for deployment](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/optionally-package-app-code-and-files-for-databricks-model-serving>) \- Deploy versioned apps to Model Serving
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow -->

On this page

Last updated on **Aug 13, 2025**

# Track versions of Git-based applications with MLflow

This guide demonstrates how to track versions of your GenAI application when your app's code resides in Git or a similar version control system. In this workflow, an MLflow `LoggedModel` acts as a **metadata hub** , linking each conceptual application version to its specific external code (such as a Git commit), configurations. This `LoggedModel` can then be associated MLflow entities like traces and evaluation runs.

The [`mlflow.set_active_model(name=...)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=set_active_model#mlflow.set_active_model>) is key to version tracking: calling this function links your application's traces to a [`LoggedModel`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html?highlight=loggedmodel#mlflow.entities.LoggedModel>). If the `name` does not exist, a new `LoggedModel` is automatically created.

This guide covers the following:

  * Track versions of your application using `LoggedModels`.
  * Link evaluation runs to your `LoggedModel`.



tip

Databricks suggests using `LoggedModels` alongside MLflow's prompt registry. If you use prompt registry, each prompt's version is automatically associated with your `LoggedModel`. See [track prompt versions alongside application versions](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/track-prompts-app-versions>).

## Prerequisitesâ

  1. Install MLflow and required packages

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.1.0" openai  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




## Step 1: Create a sample applicationâ

The following code creates a simple application that prompts an LLM for a response.

  1. Initialize an OpenAI client to connect to either Databricks-hosted LLMs or LLMs hosted by OpenAI.

     * Databricks-hosted LLMs
     * OpenAI-hosted LLMs

Use `databricks-openai` to get an OpenAI client that connects to Databricks-hosted LLMs. Select a model from the [available foundation models](</aws/en/machine-learning/foundation-model-apis/supported-models>).

Python
    
    import mlflow  
    from databricks_openai import DatabricksOpenAI  
      
    # Enable MLflow's autologging to instrument your application with Tracing  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/docs-demo")  
      
    # Create an OpenAI client that is connected to Databricks-hosted LLMs  
    client = DatabricksOpenAI()  
      
    # Select an LLM  
    model_name = "databricks-claude-sonnet-4"  
    

Use the native OpenAI SDK to connect to OpenAI-hosted models. Select a model from the [available OpenAI models](<https://platform.openai.com/docs/models>).

Python
    
    import mlflow  
    import os  
    import openai  
      
    # Ensure your OPENAI_API_KEY is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "<YOUR_API_KEY>" # Uncomment and set if not globally configured  
      
    # Enable auto-tracing for OpenAI  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/docs-demo")  
      
    # Create an OpenAI client connected to OpenAI SDKs  
    client = openai.OpenAI()  
      
    # Select an LLM  
    model_name = "gpt-4o-mini"  
    

  2. Create the sample application:

Python
         
         # Use the trace decorator to capture the application's entry point  
         @mlflow.trace  
         def my_app(input: str):  
             # This call is automatically instrumented by `mlflow.openai.autolog()`  
             response = client.chat.completions.create(  
                 model=model_name,  # This example uses a Databricks hosted LLM - you can replace this with any AI Gateway or Model Serving endpoint. If you provide your own OpenAI credentials, replace with a valid OpenAI model e.g., gpt-4o, etc.  
                 messages=[  
                     {  
                         "role": "system",  
                         "content": "You are a helpful assistant.",  
                     },  
                     {  
                         "role": "user",  
                         "content": input,  
                     },  
                 ],  
             )  
             return response.choices[0].message.content  
           
         result = my_app(input="What is MLflow?")  
         print(result)  
         




## Step 2: Add version tracking to your app's codeâ

A `LoggedModel` version serves as a central record (metadata hub) for a specific version of your application. It doesn't need to store the application code itself. Instead, it points to where your code is managed (such as a Git commit hash).

Use `mlflow.set_active_model()` to declare the `LoggedModel` that you are currently working with, or to create a new one. This function returns an `ActiveModel` object containing the `model_id` which is useful for subsequent operations.

tip

In production, you can set the environment variable `MLFLOW_ACTIVE_MODEL_ID` instead of calling `set_active_model()`. See the [version tracking in production guide](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/link-production-traces-to-app-versions>).

note

The following code uses the current Git commit hash as the model's name, so your model version only increments when you commit. To create a new LoggedModel for every change in your code base, see the helper function that creates a unique LoggedModel for any change in your code base, even if not committed to Git.

Insert the following code at the top of your application from step 1. **In your application, you must call`set_active_model()` BEFORE you execute your app's code**.

Python
    
    
    # Keep original imports  
    ### NEW CODE  
    import subprocess  
      
    # Define your application and its version identifier  
    app_name = "customer_support_agent"  
      
    # Get current git commit hash for versioning  
    try:  
        git_commit = (  
            subprocess.check_output(["git", "rev-parse", "HEAD"])  
            .decode("ascii")  
            .strip()[:8]  
        )  
        version_identifier = f"git-{git_commit}"  
    except subprocess.CalledProcessError:  
        version_identifier = "local-dev"  # Fallback if not in a git repo  
    logged_model_name = f"{app_name}-{version_identifier}"  
      
    # Set the active model context  
    active_model_info = mlflow.set_active_model(name=logged_model_name)  
    print(  
        f"Active LoggedModel: '{active_model_info.name}', Model ID: '{active_model_info.model_id}'"  
    )  
      
    ### END NEW CODE  
      
    ### ORIGINAL CODE BELOW  
    ### ...  
    

## Step 3: (Optional) Record parametersâ

You can log key configuration parameters that define this version of your application directly to the `LoggedModel` using [`mlflow.log_model_params()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.log_model_params>). This is useful for recording things like LLM names, temperature settings, or retrieval strategies that are tied to this code version.

Add the following code below the code from step 3:

Python
    
    
    app_params = {  
        "llm": "gpt-4o-mini",  
        "temperature": 0.7,  
        "retrieval_strategy": "vector_search_v3",  
    }  
      
    # Log params  
    mlflow.log_model_params(model_id=active_model_info.model_id, params=app_params)  
    

## Step 4: Run the applicationâ

  1. Call the application to see how the LoggedModel is created and tracked.



Python
    
    
    # These 2 invocations will be linked to the same LoggedModel  
    result = my_app(input="What is MLflow?")  
    print(result)  
      
    result = my_app(input="What is Databricks?")  
    print(result)  
    

  2. To simulate a change without committing, add the following lines to manually create a new logged model.



Python
    
    
      
    # Set the active model context  
    active_model_info = mlflow.set_active_model(name="new-name-set-manually")  
    print(  
        f"Active LoggedModel: '{active_model_info.name}', Model ID: '{active_model_info.model_id}'"  
    )  
      
    app_params = {  
        "llm": "gpt-4o",  
        "temperature": 0.7,  
        "retrieval_strategy": "vector_search_v4",  
    }  
      
    # Log params  
    mlflow.log_model_params(model_id=active_model_info.model_id, params=app_params)  
      
    # This will create a new LoggedModel  
    result = my_app(input="What is GenAI?")  
    print(result)  
    

## Step 5: View traces linked to the LoggedModelâ

### Use the UIâ

Go to the MLflow Experiment UI. In the **Traces** tab, you can see the version of the app that generated each trace (note, the first trace will not have a version attached since we called the app without calling `set_active_model()` first). In the **Versions** tab, you can see each `LoggedModel` alongside its parameters and linked traces.

### Use the SDKâ

You can use [`search_traces()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=search_traces#mlflow.search_traces>) to query for traces from a `LoggedModel`:

Python
    
    
    import mlflow  
      
    traces = mlflow.search_traces(  
        filter_string=f"metadata.`mlflow.modelId` = '{active_model_info.model_id}'"  
    )  
    print(traces)  
    

You can use [`get_logged_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=t_logged_mod#mlflow.get_logged_model>) to get details of the `LoggedModel`:

Python
    
    
    import mlflow  
    import datetime  
    # Get LoggedModel metadata  
    logged_model = mlflow.get_logged_model(model_id=active_model_info.model_id)  
      
    # Inspect basic properties  
    print(f"\n=== LoggedModel Information ===")  
    print(f"Model ID: {logged_model.model_id}")  
    print(f"Name: {logged_model.name}")  
    print(f"Experiment ID: {logged_model.experiment_id}")  
    print(f"Status: {logged_model.status}")  
    print(f"Model Type: {logged_model.model_type}")  
    creation_time = datetime.datetime.fromtimestamp(logged_model.creation_timestamp / 1000)  
    print(f"Created at: {creation_time}")  
      
    # Access the parameters  
    print(f"\n=== Model Parameters ===")  
    for param_name, param_value in logged_model.params.items():  
        print(f"{param_name}: {param_value}")  
      
    # Access tags if any were set  
    if logged_model.tags:  
        print(f"\n=== Model Tags ===")  
        for tag_key, tag_value in logged_model.tags.items():  
            print(f"{tag_key}: {tag_value}")  
    

## Step 6: Link evaluation results to the LoggedModelâ

To evaluate your application and link the results to this `LoggedModel` version, see [Link Evaluation Results and Traces to App Versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>). This guide covers how to use `mlflow.genai.evaluate()` to assess your application's performance and automatically associate the metrics, evaluation tables, and traces with your specific `LoggedModel` version.

Python
    
    
    import mlflow  
    from mlflow.genai import scorers  
      
    eval_dataset = [  
        {  
            "inputs": {"input": "What is the most common aggregate function in SQL?"},  
        }  
    ]  
      
    mlflow.genai.evaluate(data=eval_dataset, predict_fn=my_app, model_id=active_model_info.model_id, scorers=scorers.get_all_scorers())  
    

View the results in the **Versions** and **Evaluations** tabs in the MLflow Experiment UI:

## Helper function to compute a unique hash for any file changeâ

The below helper function automatically generates a name for each `LoggedModel` based on the status of your repo. To use this function, call `set_active_model(name=get_current_git_hash())`.

`get_current_git_hash()` generates a unique, deterministic identifier for the current state of a Git repository by returning either the HEAD commit hash (for clean repos) or a combination of the HEAD hash and a hash of uncommitted changes (for dirty repos). It ensures that different states of the repository always produce different identifiers, so every code change results in a new `LoggedModel`.

Python
    
    
    import subprocess  
    import hashlib  
    import os  
      
    def get_current_git_hash():  
        """  
        Get a deterministic hash representing the current git state.  
        For clean repositories, returns the HEAD commit hash.  
        For dirty repositories, returns a combination of HEAD + hash of changes.  
        """  
        try:  
            # Get the git repository root  
            result = subprocess.run(  
                ["git", "rev-parse", "--show-toplevel"],  
                capture_output=True, text=True, check=True  
            )  
            git_root = result.stdout.strip()  
      
            # Get the current HEAD commit hash  
            result = subprocess.run(  
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True  
            )  
            head_hash = result.stdout.strip()  
      
            # Check if repository is dirty  
            result = subprocess.run(  
                ["git", "status", "--porcelain"], capture_output=True, text=True, check=True  
            )  
      
            if not result.stdout.strip():  
                # Repository is clean, return HEAD hash  
                return head_hash  
      
            # Repository is dirty, create deterministic hash of changes  
            # Collect all types of changes  
            changes_parts = []  
      
            # 1. Get staged changes  
            result = subprocess.run(  
                ["git", "diff", "--cached"], capture_output=True, text=True, check=True  
            )  
            if result.stdout:  
                changes_parts.append(("STAGED", result.stdout))  
      
            # 2. Get unstaged changes to tracked files  
            result = subprocess.run(  
                ["git", "diff"], capture_output=True, text=True, check=True  
            )  
            if result.stdout:  
                changes_parts.append(("UNSTAGED", result.stdout))  
      
            # 3. Get all untracked/modified files from status  
            result = subprocess.run(  
                ["git", "status", "--porcelain", "-uall"],  
                capture_output=True, text=True, check=True  
            )  
      
            # Parse status output to handle all file states  
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []  
            file_contents = []  
      
            for line in status_lines:  
                if len(line) >= 3:  
                    status_code = line[:2]  
                    filepath = line[3:]  # Don't strip - filepath starts exactly at position 3  
      
                    # For any modified or untracked file, include its current content  
                    if '?' in status_code or 'M' in status_code or 'A' in status_code:  
                        try:  
                            # Use absolute path relative to git root  
                            abs_filepath = os.path.join(git_root, filepath)  
                            with open(abs_filepath, 'rb') as f:  
                                # Read as binary to avoid encoding issues  
                                content = f.read()  
                                # Create a hash of the file content  
                                file_hash = hashlib.sha256(content).hexdigest()  
                                file_contents.append(f"{filepath}:{file_hash}")  
                        except (IOError, OSError):  
                            file_contents.append(f"{filepath}:unreadable")  
      
            # Sort file contents for deterministic ordering  
            file_contents.sort()  
      
            # Combine all changes  
            all_changes_parts = []  
      
            # Add diff outputs  
            for change_type, content in changes_parts:  
                all_changes_parts.append(f"{change_type}:\n{content}")  
      
            # Add file content hashes  
            if file_contents:  
                all_changes_parts.append("FILES:\n" + "\n".join(file_contents))  
      
            # Create final hash  
            all_changes = "\n".join(all_changes_parts)  
            content_to_hash = f"{head_hash}\n{all_changes}"  
            changes_hash = hashlib.sha256(content_to_hash.encode()).hexdigest()  
      
            # Return HEAD hash + first 8 chars of changes hash  
            return f"{head_hash[:32]}-dirty-{changes_hash[:8]}"  
      
        except subprocess.CalledProcessError as e:  
            raise RuntimeError(f"Git command failed: {e}")  
        except FileNotFoundError:  
            raise RuntimeError("Git is not installed or not in PATH")  
    

## Next stepsâ

  * If you need to bundle code with the `LoggedModel`, see [Package code for Databricks Model Serving](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/optionally-package-app-code-and-files-for-databricks-model-serving>).
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/track-prompts-app-versions -->

On this page

Last updated on **Aug 11, 2025**

# Track prompt versions alongside application versions

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

This guide shows you how to integrate prompts from the MLflow Prompt Registry into your GenAI applications while tracking both prompt and application versions together. When you use [`mlflow.set_active_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=set_active#mlflow.set_active_model>) with prompts from the registry, MLflow automatically creates lineage between your prompt versions and application versions.

This guide covers the following steps:

  * Load and use prompts from the MLflow Prompt Registry in your application.
  * Track application versions using `LoggedModels`.
  * View automatic lineage between prompt versions and application versions.
  * Update prompts and see how changes flow through to your application.



All of the code on this page is included in the example notebook.

## Prerequisitesâ

  1. Install MLflow and required packages

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.1.0" openai  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).

  3. Make sure you have access to a Unity Catalog schema with the `CREATE FUNCTION`, `EXECUTE`, and `MANAGE` permissions to use the prompt registry.




note

A Unity Catalog schema with `CREATE FUNCTION`, `EXECUTE`, and `MANAGE` permissions is required in order to view or create prompts. If you are using a [Databricks trial account](</aws/en/getting-started/express-setup>), you have the required permissions on the Unity Catalog schema `workspace.default`.

## Step 1: Create a prompt in the registryâ

First, let's create a prompt that we'll use in our application. If you've already created a prompt following the [Create and edit prompts](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts>) guide, you can skip this step.

Python
    
    
    import mlflow  
      
    # Replace with a Unity Catalog schema where you have CREATE FUNCTION, EXECUTE, and MANAGE permission  
    uc_schema = "workspace.default"  
    prompt_name = "customer_support_prompt"  
      
    # Define the prompt template with variables  
    initial_template = """\  
    You are a helpful customer support assistant for {{company_name}}.  
      
    Please help the customer with their inquiry about: {{topic}}  
      
    Customer Question: {{question}}  
      
    Provide a friendly, professional response that addresses their concern.  
    """  
      
    # Register a new prompt  
    prompt = mlflow.genai.register_prompt(  
        name=f"{uc_schema}.{prompt_name}",  
        template=initial_template,  
        commit_message="Initial customer support prompt",  
        tags={  
            "author": "support-team@company.com",  
            "use_case": "customer_service",  
            "department": "customer_support",  
            "language": "en"  
        }  
    )  
      
    print(f"Created prompt '{prompt.name}' (version {prompt.version})")  
    

## Step 2: Create an application with versioning enabled that uses the promptâ

Now let's create a GenAI application that loads and uses this prompt from the registry. We'll use `mlflow.set_active_model()` to track the application version.

When you call [`mlflow.set_active_model()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=set_active#mlflow.set_active_model>), MLflow creates a [`LoggedModel`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html?highlight=loggedmodel#mlflow.entities.LoggedModel>) that serves as a metadata hub for your application version. This LoggedModel doesn't store your actual application code - instead, it acts as a central record that links to your external code (like a Git commit), configuration parameters, and automatically tracks which prompts from the registry your application uses. For a detailed explanation of how application version tracking works, see [track application versions with MLflow](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>).

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
    

  2. Define your application with versioning:

Python
         
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
           
         # Set the active model context - this creates a LoggedModel that represents this version of your application  
         active_model_info = mlflow.set_active_model(name=logged_model_name)  
         print(  
             f"Active LoggedModel: '{active_model_info.name}', Model ID: '{active_model_info.model_id}'"  
         )  
           
         # Log application parameters  
         # These parameters help you track the configuration of this app version  
         app_params = {  
             "llm": model_name,  
             "temperature": 0.7,  
             "max_tokens": 500  
         }  
         mlflow.log_model_params(model_id=active_model_info.model_id, params=app_params)  
           
         # Load the prompt from the registry  
         # NOTE: Loading the prompt AFTER calling set_active_model() is what enables  
         # automatic lineage tracking between the prompt version and the LoggedModel  
         prompt = mlflow.genai.load_prompt(f"prompts:/{uc_schema}.{prompt_name}/1")  
         print(f"Loaded prompt version {prompt.version}")  
           
         # Use the trace decorator to capture the application's entry point  
         # Each trace created by this function is automatically linked to the LoggedModel (application version) we set above. In turn, the LoggedModel is linked to the prompt version that was loaded from the registry  
         @mlflow.trace  
         def customer_support_app(company_name: str, topic: str, question: str):  
             # Format the prompt with variables  
             formatted_prompt = prompt.format(  
                 company_name=company_name,  
                 topic=topic,  
                 question=question  
             )  
           
             # Call the LLM  
             response = client.chat.completions.create(  
                 model=model_name,  # Replace with your model  
                 messages=[  
                     {  
                         "role": "user",  
                         "content": formatted_prompt,  
                     },  
                 ],  
                 temperature=0.7,  
                 max_tokens=500  
             )  
             return response.choices[0].message.content  
           
         # Test the application  
         result = customer_support_app(  
             company_name="TechCorp",  
             topic="billing",  
             question="I was charged twice for my subscription last month. Can you help?"  
         )  
         print(f"\nResponse: {result}")  
         




## Step 3: View automatic lineage in the UIâ

When you use prompts from the registry in an application that has an active model set, MLflow automatically tracks the relationship between the prompt version and the application version.

Navigate to your experiment in the MLflow Experiment UI. On the Experiment page, click the **Versions** tab. The prompt version appears in the table as shown.

## Step 4: Update the prompt and track the changeâ

Let's improve our prompt and see how the new version is automatically tracked when we use it in our application.

Python
    
    
    # Create an improved version of the prompt  
    improved_template = """\  
    You are a helpful and empathetic customer support assistant for {{company_name}}.  
      
    Customer Topic: {{topic}}  
    Customer Question: {{question}}  
      
    Please provide a response that:  
    1. Acknowledges the customer's concern with empathy  
    2. Provides a clear solution or next steps  
    3. Offers additional assistance if needed  
    4. Maintains a friendly, professional tone  
      
    Remember to:  
    - Use the customer's name if provided  
    - Be concise but thorough  
    - Avoid technical jargon unless necessary  
    """  
      
    # Register the new version  
    updated_prompt = mlflow.genai.register_prompt(  
        name=f"{uc_schema}.{prompt_name}",  
        template=improved_template,  
        commit_message="Added structured response guidelines for better customer experience",  
        tags={  
            "author": "support-team@company.com",  
            "improvement": "Added empathy guidelines and response structure"  
        }  
    )  
      
    print(f"Created version {updated_prompt.version} of '{updated_prompt.name}'")  
    

## Step 5: Use the updated prompt in your applicationâ

Now let's use the new prompt version and create a new application version to track this change:

Python
    
    
    # Create a new application version  
    new_version_identifier = "v2-improved-prompt"  
    new_logged_model_name = f"{app_name}-{new_version_identifier}"  
      
    # Set the new active model  
    active_model_info_v2 = mlflow.set_active_model(name=new_logged_model_name)  
    print(  
        f"Active LoggedModel: '{active_model_info_v2.name}', Model ID: '{active_model_info_v2.model_id}'"  
    )  
      
    # Log updated parameters  
    app_params_v2 = {  
        "llm": "databricks-claude-sonnet-4",  
        "temperature": 0.7,  
        "max_tokens": 500,  
        "prompt_version": "2"  # Track which prompt version we're using  
    }  
    mlflow.log_model_params(model_id=active_model_info_v2.model_id, params=app_params_v2)  
      
    # Load the new prompt version  
    prompt_v2 = mlflow.genai.load_prompt(f"prompts:/{uc_schema}.{prompt_name}/2")  
      
    # Update the app to use the new prompt  
    @mlflow.trace  
    def customer_support_app_v2(company_name: str, topic: str, question: str):  
        # Format the prompt with variables  
        formatted_prompt = prompt_v2.format(  
            company_name=company_name,  
            topic=topic,  
            question=question  
        )  
      
        # Call the LLM  
        response = client.chat.completions.create(  
            model="databricks-claude-sonnet-4",  
            messages=[  
                {  
                    "role": "user",  
                    "content": formatted_prompt,  
                },  
            ],  
            temperature=0.7,  
            max_tokens=500  
        )  
        return response.choices[0].message.content  
      
    # Test with the same question to see the difference  
    result_v2 = customer_support_app_v2(  
        company_name="TechCorp",  
        topic="billing",  
        question="I was charged twice for my subscription last month. Can you help?"  
    )  
    print(f"\nImproved Response: {result_v2}")  
    

##  Example notebookâ

The following notebook includes all of the code on this page.

#### Track prompt and app versions notebook

[Open notebook in new tab](<https://docs.databricks.com/aws/en/notebooks/source/mlflow3/track-prompt-app-versions.html>)

Copy link for import

Copy to clipboard

## Next steps: Evaluate prompt versionsâ

Now that you've tracked different versions of your prompts and applications, you can systematically evaluate which prompt versions perform best. MLflow's evaluation framework allows you to compare multiple prompt versions side-by-side using LLM judges and custom metrics.

To learn how to evaluate the quality of different prompt versions, see [evaluate prompts](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/evaluate-prompts>). This guide shows you how to:

  * Run evaluations on different prompt versions.
  * Compare results across versions using the evaluation UI.
  * Use both built-in LLM judges and custom metrics.
  * Make data-driven decisions about which prompt version to deploy.



By combining prompt versioning with evaluation, you can iteratively improve your prompts with confidence, knowing exactly how each change impacts quality metrics.

To learn about using production traces to track versions in production environments, see [Link Production Traces to App Versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/link-production-traces-to-app-versions>).
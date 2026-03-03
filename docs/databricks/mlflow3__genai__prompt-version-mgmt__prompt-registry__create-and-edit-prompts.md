<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts -->

On this page

Last updated on **Feb 24, 2026**

# Create and edit prompts

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

This page shows you how to create new prompts and manage their versions in the MLflow Prompt Registry using the MLflow Python SDK. It includes instructions for using the MLflow Python SDK and the Databricks MLflow UI. All of the code on this page is included in the example notebook.

## Prerequisitesâ

  1. Install MLflow and required packages

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.1.0" openai  
         

  2. Create an MLflow experiment by following the [set up your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).

  3. Create or identify a Unity Catalog schema for storing prompts. You must have the `CREATE FUNCTION`, `EXECUTE`, and `MANAGE` privileges on the Unity Catalog schema.




note

A Unity Catalog schema with `CREATE FUNCTION`, `EXECUTE`, and `MANAGE` permissions is required in order to view or create prompts. If you are using a [Databricks trial account](</aws/en/getting-started/express-setup>), you have the required permissions on the Unity Catalog schema `main.default`.

## Step 1. Create a new promptâ

You can create prompts in the Databricks MLflow UI, or programmatically using the MLflow Python SDK.

### Use the Databricks MLflow UIâ

To create a prompt in the UI:

  1. Navigate to your MLflow experiment.

  2. Click the **Prompts** tab.

  3. Click . A dialog appears.

  4. If no prompts have yet been created for this experiment, you must specify the Unity Catalog schema to use.

     1. Click **Choose** or type in the search box. As you type in the search box, matching Unity Catalog assets appear.
     2. Select the schema you want and click **Confirm**. You must have the following permissions on the schema: `CREATE FUNCTION`, `EXECUTE`, and `MANAGE`.
  5. Type a name for the prompt, and click **Create**.

  6. Click **Create new version**.

  7. Type your prompt and click **Save**. You can use variables in the prompt text by using `{{variable_name}}` syntax.




The prompt appears in the UI:

### Use the Python SDKâ

  1. Link your MLflow experiment to a default Prompt Registry location by setting an experiment tag using [`mlflow.set_experiment_tags`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.set_experiment_tags>). This lets SDKs and tools infer your Unity Catalog prompt schema automatically.

Use the `mlflow.promptRegistryLocation` tag with the value `catalog.schema`:

Python
         
         import mlflow  
           
         # Link the current MLflow experiment to a UC schema for prompts  
         mlflow.set_experiment_tags({  
             "mlflow.promptRegistryLocation": "main.default"  
         })  
         

  2. Create prompts using [`mlflow.genai.register_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.register_prompt>). Prompts use double-brace syntax (`{{variable}}`) for template variables.

Python
         
         # Replace with a Unity Catalog schema where you have CREATE FUNCTION, EXECUTE, and MANAGE privileges  
         uc_schema = "main.default"  
         # This table is created in the UC schema specified in the previous line  
         prompt_name = "summarization_prompt"  
           
         # Define the prompt template with variables  
         initial_template = """\  
          Summarize content you are provided with in {{num_sentences}} sentences.  
           
         Content: {{content}}  
         """  
           
         # Register a new prompt  
         prompt = mlflow.genai.register_prompt(  
             name=f"{uc_schema}.{prompt_name}",  
             template=initial_template,  
             # all following parameters are optional  
             commit_message="Initial version of summarization prompt",  
             tags={  
                  "author": "data-science-team@company.com",  
                  "use_case": "document_summarization",  
                  "task": "summarization",  
                  "language": "en",  
                  "model_compatibility": "gpt-4"  
              }  
          )  
           
         print(f"Created prompt '{prompt.name}' (version {prompt.version})")  
         




## Step 2: Use the prompt in your applicationâ

The following steps create a simple application that uses your prompt template using the Python SDK.

### Load the prompt from the registryâ

Python
    
    
    # Load a specific version using URI syntax  
    prompt = mlflow.genai.load_prompt(name_or_uri=f"prompts:/{uc_schema}.{prompt_name}/1")  
      
    # Alternative syntax without URI  
    prompt = mlflow.genai.load_prompt(name_or_uri=f"{uc_schema}.{prompt_name}", version="1")  
    

### Use the prompt in your applicationâ

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
    

  2. Define your application:

Python
         
         # Use the trace decorator to capture the application's entry point  
         @mlflow.trace  
         def my_app(content: str, num_sentences: int):  
             # Format with variables  
             formatted_prompt = prompt.format(  
                 content=content,  
                 num_sentences=num_sentences  
             )  
           
             response = client.chat.completions.create(  
                 model=model_name,  # This example uses a Databricks hosted LLM. You can replace this with any AI Gateway or Model Serving endpoint, or with a valid OpenAI model like gpt-4o.  
                 messages=[  
                     {  
                         "role": "system",  
                         "content": "You are a helpful assistant.",  
                     },  
                     {  
                         "role": "user",  
                         "content": formatted_prompt,  
                     },  
                 ],  
             )  
             return response.choices[0].message.content  
           
         result = my_app(content="This guide shows you how to integrate prompts from the MLflow Prompt Registry into your GenAI applications. You'll learn to load prompts, format them with dynamic data, and ensure complete lineage by linking prompt versions to your MLflow Models.", num_sentences=1)  
         print(result)  
         




## Step 3. Edit the promptâ

Prompt versions are immutable after you create them. To edit a prompt, you must create a new version. This Git-like versioning maintains complete history and enables rollbacks.

### Use the Databricks MLflow UIâ

To create a new version:

  1. On the **Prompts** tab, click  next to the prompt you want to edit.

  2. Type your prompt and click **Save**.




#### Compare prompt versionsâ

To compare prompt versions:

  1. On the **Prompts** tab, click the name of the prompt.

  2. At the upper left, click **Compare** and select the versions to compare.




### Use the Python SDKâ

Create a new version by calling [`mlflow.genai.register_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.register_prompt>) with an existing prompt name:

Python
    
    
    import mlflow  
      
    # Define the improved template  
    new_template = """\  
    You are an expert summarizer. Condense the following content into exactly {{ num_sentences }} clear and informative sentences that capture the key points.  
      
    Content: {{content}}  
      
    Your summary should:  
    - Contain exactly {{num_sentences}} sentences  
    - Include only the most important information  
    - Be written in a neutral, objective tone  
    - Maintain the same level of formality as the original text  
    """  
      
    # Register a new version  
    updated_prompt = mlflow.genai.register_prompt(  
        name=f"{uc_schema}.{prompt_name}",  
        template=new_template,  
        commit_message="Added detailed instructions for better output quality",  
        tags={  
            "author": "data-science-team@company.com",  
            "improvement": "Added specific guidelines for summary quality"  
        }  
    )  
      
    print(f"Created version {updated_prompt.version} of '{updated_prompt.name}'")  
    

## Step 4. Use the new promptâ

The following code shows how to use the prompt.

Python
    
    
    # Load a specific version using URI syntax  
    prompt = mlflow.genai.load_prompt(name_or_uri=f"prompts:/{uc_schema}.{prompt_name}/2")  
      
    # Or load from specific version  
    prompt = mlflow.genai.load_prompt(name_or_uri=f"{uc_schema}.{prompt_name}", version="2")  
    

## Step 5. Search and discover promptsâ

To find prompts in your Unity Catalog schema:

Python
    
    
    # REQUIRED format for Unity Catalog - specify catalog and schema  
    results = mlflow.genai.search_prompts("catalog = 'main' AND schema = 'default'")  
      
    # Using variables for your schema  
    catalog_name = uc_schema.split('.')[0]  # 'main'  
    schema_name = uc_schema.split('.')[1]   # 'default'  
    results = mlflow.genai.search_prompts(f"catalog = '{catalog_name}' AND schema = '{schema_name}'")  
      
    # Limit results  
    results = mlflow.genai.search_prompts(  
        filter_string=f"catalog = '{catalog_name}' AND schema = '{schema_name}'",  
        max_results=50  
    )  
    

##  Example notebookâ

#### Create and edit prompts example notebook

[Open notebook in new tab](<https://docs.databricks.com/aws/en/notebooks/source/mlflow3/create-edit-prompts.html>)

Copy link for import

Copy to clipboard

## Next stepsâ

  * [Evaluate prompt versions](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/evaluate-prompts>) \- Compare different prompt versions to identify the best performer.
  * [Track prompts with app versions](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/track-prompts-app-versions>) \- Link prompt versions to your application versions.
  * [Use prompts in deployed apps](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps>) \- Deploy prompts to production with aliases.
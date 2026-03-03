<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/examples -->

On this page

Last updated on **Nov 6, 2025**

# Prompt Registry examples

This page offers examples for the Prompt Registry operations.

## register_prompt()â

**API reference:** [`mlflow.genai.register_prompt`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.register_prompt>)

Python
    
    
    prompt = mlflow.genai.register_prompt(  
        name="mycatalog.myschema.summarization",  
        template="""Summarize the following text in {{num_sentences}} sentences:  
      
    Text: {{content}}  
      
    Focus on: {{focus_areas}}""",  
        commit_message="Added focus areas parameter",  
        tags={  
            "tested_with": "gpt-4",  
            "avg_latency_ms": "1200",  
            "team": "content",  
            "project": "summarization-v2"  
        }  
    )  
    

## load_prompt()â

**API reference:** [`mlflow.genai.load_prompt`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.load_prompt>)

The following example loads a specific version using URI format

Python
    
    
    # Load specific version using URI format  
    v2 = mlflow.genai.load_prompt(name_or_uri="prompts:/mycatalog.myschema.qa_prompt/2")  
      
    # Load specific version using name + version parameter  
    v3 = mlflow.genai.load_prompt(name_or_uri="mycatalog.myschema.qa_prompt", version=3)  
      
    # Load with allow_missing flag (returns None if not found)  
    optional_prompt = mlflow.genai.load_prompt(  
        name_or_uri="mycatalog.myschema.qa_prompt",  
        version=3,  
        allow_missing=True  
    )  
      
    # Use the prompt  
    if optional_prompt is not None:  
        response = llm.invoke(optional_prompt.format(  
            question="What is MLflow?",  
            context="MLflow is an open source platform..."  
        ))  
    

The following example loads by alias using URI format

Python
    
    
      
    # Load by alias using URI  
    prod = mlflow.genai.load_prompt(name_or_uri="prompts:/mycatalog.myschema.qa_prompt@production")  
      
    # Load with allow_missing flag (returns None if not found)  
    optional_prompt = mlflow.genai.load_prompt(  
        name_or_uri="mycatalog.myschema.qa_prompt",  
        version=3,  
        allow_missing=True  
    )  
      
    # Use the prompt  
    if optional_prompt is not None:  
        response = llm.invoke(optional_prompt.format(  
            question="What is MLflow?",  
            context="MLflow is an open source platform..."  
        ))  
    

## search_prompts()â

**API Reference:** [`mlflow.genai.search_prompts`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.search_prompts>)

### Unity Catalog Requirementsâ

**For Unity Catalog prompt registries, you must specify both catalog and schema:**

Python
    
    
    # REQUIRED format - list all prompts in a catalog.schema  
    results = mlflow.genai.search_prompts("catalog = 'mycatalog' AND schema = 'myschema'")  
      
    # This is the ONLY supported filter format  
    results = mlflow.genai.search_prompts("catalog = 'rohit' AND schema = 'default'")  
    

### Limitationsâ

**The following filters are NOT supported in Unity Catalog:**

  * Name patterns: `name LIKE '%pattern%'`
  * Tag filtering: `tags.field = 'value'`
  * Exact name matching: `name = 'specific.name'`
  * Combined filters beyond catalog + schema



**To find specific prompts, use the returned list and filter programmatically:**

Python
    
    
    # Get all prompts in schema  
    all_prompts = mlflow.genai.search_prompts("catalog = 'mycatalog' AND schema = 'myschema'")  
      
    # Filter programmatically  
    customer_prompts = [p for p in all_prompts if 'customer' in p.name.lower()]  
    tagged_prompts = [p for p in all_prompts if p.tags.get('team') == 'support']  
    

## set_prompt_alias()â

**API Reference:** [`mlflow.genai.set_prompt_alias`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.set_prompt_alias>)

Python
    
    
    # Promote version 3 to production  
    mlflow.genai.set_prompt_alias(  
        name="mycatalog.myschema.chat_assistant",  
        alias="production",  
        version=3  
    )  
      
    # Set up staging for testing  
    mlflow.genai.set_prompt_alias(  
        name="mycatalog.myschema.chat_assistant",  
        alias="staging",  
        version=4  
    )  
    

## delete_prompt() and delete_prompt_version()â

### delete_prompt_version()â

**API Reference:** [`MlflowClient.delete_prompt_version`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.delete_prompt_version>)

Deletes a specific version of a prompt:

Python
    
    
    from mlflow import MlflowClient  
      
    client = MlflowClient()  
      
    # Delete specific versions first (required for Unity Catalog)  
    client.delete_prompt_version("mycatalog.myschema.chat_assistant", "1")  
    client.delete_prompt_version("mycatalog.myschema.chat_assistant", "2")  
    client.delete_prompt_version("mycatalog.myschema.chat_assistant", "3")  
      
    # Then delete the entire prompt  
    client.delete_prompt("mycatalog.myschema.chat_assistant")  
      
    # For convenience with Unity Catalog, you can also search and delete all versions:  
    search_response = client.search_prompt_versions("mycatalog.myschema.chat_assistant")  
    for version in search_response.prompt_versions:  
        client.delete_prompt_version("mycatalog.myschema.chat_assistant", str(version.version))  
      
    client.delete_prompt("mycatalog.myschema.chat_assistant")  
    

### delete_prompt()â

After you delete the prompt version, you can delete the prompt.

important

  * For Unity Catalog registries, `delete_prompt()` fails if any versions still exist. All versions must be deleted first using `delete_prompt_version()`.
  * For other registry types, `delete_prompt()` works normally without version checking.



**API Reference:** [`MlflowClient.delete_prompt`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.delete_prompt>)

Python
    
    
    from mlflow import MlflowClient  
      
    client = MlflowClient()  
      
    # Delete specific versions first (required for Unity Catalog)  
    client.delete_prompt_version("mycatalog.myschema.chat_assistant", "1")  
    client.delete_prompt_version("mycatalog.myschema.chat_assistant", "2")  
    client.delete_prompt_version("mycatalog.myschema.chat_assistant", "3")  
      
    # Then delete the entire prompt  
    client.delete_prompt("mycatalog.myschema.chat_assistant")  
      
    # For convenience with Unity Catalog, you can also search and delete all versions:  
    search_response = client.search_prompt_versions("mycatalog.myschema.chat_assistant")  
    for version in search_response.prompt_versions:  
        client.delete_prompt_version("mycatalog.myschema.chat_assistant", str(version.version))  
      
    client.delete_prompt("mycatalog.myschema.chat_assistant")
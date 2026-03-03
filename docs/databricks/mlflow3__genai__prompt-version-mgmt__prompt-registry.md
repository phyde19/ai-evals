<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/ -->

On this page

Last updated on **Nov 6, 2025**

# Prompt Registry

Beta

This feature is in [Beta](</aws/en/release-notes/release-types>). Workspace admins can control access to this feature from the **Previews** page. See [Manage Databricks previews](</aws/en/admin/workspace-settings/manage-previews>).

## Overviewâ

The MLflow Prompt Registry is a centralized repository for managing prompt templates across their lifecycle. It enables teams to:

  * **Version and track prompts** with Git-like versioning, commit messages, and rollback capabilities
  * **Deploy safely with aliases** using mutable references (e.g., "production", "staging") for A/B testing and gradual rollouts
  * **Collaborate without code changes** by allowing non-engineers to modify prompts through the UI
  * **Integrate with any framework** including LangChain, LlamaIndex, and other GenAI frameworks
  * **Maintain governance** through Unity Catalog integration for access control and audit trails
  * **Track lineage** by linking prompts to experiments and evaluation results



The Prompt Registry follows a Git-like model:

  * **Prompts** : Named entities in Unity Catalog
  * **Versions** : Immutable snapshots with auto-incrementing numbers
  * **Aliases** : Mutable pointers to specific versions
  * **Tags** : Version-specific key-value pairs



## Prerequisitesâ

  1. Install MLflow with Unity Catalog support:

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.1.0"  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).
  3. Make sure you have access to a Unity Catalog schema with the `CREATE FUNCTION`, `EXECUTE`, and `MANAGE` permissions to view or create prompts in the prompt registry.



## Quick startâ

The following code shows the essential workflow for using the Prompt Registry. Notice the double-brace syntax for template variables:

Python
    
    
    import mlflow  
      
    # Register a prompt template  
    prompt = mlflow.genai.register_prompt(  
        name="mycatalog.myschema.customer_support",  
        template="You are a helpful assistant. Answer this question: {{question}}",  
        commit_message="Initial customer support prompt"  
    )  
    print(f"Created version {prompt.version}")  # "Created version 1"  
      
    # Set a production alias  
    mlflow.genai.set_prompt_alias(  
        name="mycatalog.myschema.customer_support",  
        alias="production",  
        version=1  
    )  
      
    # Load and use the prompt in your application  
    prompt = mlflow.genai.load_prompt(name_or_uri="prompts:/mycatalog.myschema.customer_support@production")  
    response = llm.invoke(prompt.format(question="How do I reset my password?"))  
    

## SDK overviewâ

The following table summarizes the six main functions that Prompt Registry provides. For examples, see [Prompt Registry examples](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/examples>).

Function| Purpose| [`register_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.register_prompt>)| Create new prompts or add new versions| [`load_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.load_prompt>)| Retrieve specific prompt versions or aliases| [`search_prompts()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.search_prompts>)| Find prompts by name, tags, or metadata| [`set_prompt_alias()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.set_prompt_alias>)| Create or update alias pointers| [`delete_prompt_alias()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.delete_prompt_alias>)| Remove aliases (versions remain)| [`delete_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html#mlflow.client.MlflowClient.delete_prompt>)| Delete entire prompts or specific versions  
---|---  
  
## Prompt template formatsâ

Prompt templates can be stored in two formats: simple prompts or conversations. For both, prompt strings can be templatized using the double-brace syntax `"Hello {{name}}"`.

Format| Python type| Description| Example| Simple prompt| `str`| Single-message prompt template| `"Summarize the content below in {{num_sentences}} sentences. Content: {{content}}"`| Conversation| `List[dict]`| Each `dict` is one message with 'role' and 'content' keys| `[{"role": "user", "content": "Hello {{name}}"}, ...]`  
---|---|---|---  
  
The following example shows both simple and conversation-style prompts, using the double-brace format for template variables:

Python
    
    
    # Simple prompt  
    simple_prompt = mlflow.genai.register_prompt(  
        name="mycatalog.myschema.greeting",  
        template="Hello {{name}}, how can I help you today?",  
        commit_message="Simple greeting"  
    )  
      
    # Conversation or chat-style prompt  
    complex_prompt = mlflow.genai.register_prompt(  
        name="mycatalog.myschema.analysis",  
        template=[  
            {"role": "system", "content": "You are a helpful {{style}} assistant."},  
            {"role": "user", "content": "{{question}}"},  
        ],  
        commit_message="Multi-variable analysis template"  
    )  
      
    # Use the prompt  
    rendered = complex_prompt.format(  
        style="edgy",  
        question="What is a good costume for a rainy Halloween?"  
    )  
    

### Single-brace format compatibilityâ

LangChain, LlamaIndex, and some other libraries support single-brace syntax (Python f-string syntax) for prompt templates: `"Hello {name}"`. For compatibility, MLflow supports converting prompts to single-brace format:

  * LangChain
  * LlamaIndex



Python
    
    
    from langchain_core.prompts import ChatPromptTemplate  
      
    # Load from registry  
    mlflow_prompt = mlflow.genai.load_prompt("prompts:/mycatalog.myschema.chat@production")  
      
    # Convert to LangChain format  
    langchain_template = mlflow_prompt.to_single_brace_format()  
    chat_prompt = ChatPromptTemplate.from_template(langchain_template)  
      
    # Use in chain  
    chain = chat_prompt | llm | output_parser  
    

Python
    
    
    from llama_index.core import PromptTemplate  
      
    # Load and convert  
    mlflow_prompt = mlflow.genai.load_prompt("prompts:/mycatalog.myschema.rag@production")  
    llama_template = PromptTemplate(mlflow_prompt.to_single_brace_format())  
      
    # Use in query engine  
    query_engine.update_prompts({"response_synthesizer:text_qa_template": llama_template})  
    

## Next stepsâ

  * [Create and edit prompts](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts>) \- Get started with your first prompt
  * [Use prompts in deployed apps](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps>) \- Deploy prompts to production with aliases
  * [Evaluate prompts](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/evaluate-prompts>) \- Compare prompt versions systematically
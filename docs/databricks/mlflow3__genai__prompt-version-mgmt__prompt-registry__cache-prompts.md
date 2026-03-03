<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/cache-prompts -->

On this page

Last updated on **Dec 29, 2025**

# Prompt caching

MLflow automatically caches loaded prompts in memory to improve performance and reduce repeated API calls. The caching strategy varies based on whether you access prompts by version or alias.

## Prerequisitesâ

  * Prompt caching is supported on MLflow version 3.8 and above.



## Default caching behaviorâ

MLflow implements differentiated caching:

  * **Version-based prompts** : Cached indefinitely because prompt versions are immutable after creation. For example, `prompts:/summarization-prompt/1`.
  * **Alias-based prompts** : Cached for 60 seconds by default because aliases can point to different versions over time. For example, `prompts:/summarization-prompt@production`.



## Per-request cache controlâ

Override caching behavior using the `cache_ttl_seconds` parameter in [`load_prompt()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.load_prompt>):

Python
    
    
    import mlflow  
      
    # Custom TTL: cache for 5 minutes  
    prompt = mlflow.genai.load_prompt(  
        "prompts:/summarization-prompt/1",  
        cache_ttl_seconds=300  
    )  
      
    # Bypass cache: always fetch fresh data  
    prompt = mlflow.genai.load_prompt(  
        "prompts:/summarization-prompt@production",  
        cache_ttl_seconds=0  
    )  
      
    # Infinite caching for alias-based prompts  
    prompt = mlflow.genai.load_prompt(  
        "prompts:/summarization-prompt@production",  
        cache_ttl_seconds=float("inf")  
    )  
    

## Global cache configurationâ

Set system-wide cache defaults using environment variables:

  * `MLFLOW_ALIAS_PROMPT_CACHE_TTL_SECONDS`: Default TTL for alias-based prompts
  * `MLFLOW_VERSION_PROMPT_CACHE_TTL_SECONDS`: Default TTL for version-based prompts



To disable caching globally, set the variable to `0`.

## Cache invalidationâ

The cache automatically clears when a prompt is modified, including:

  * Tag updates
  * Alias changes
  * Version deletions



## Next stepsâ

  * [Use prompts in deployed apps](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps>)
  * [Create and edit prompts](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts>)
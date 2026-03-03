<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/instructor -->

On this page

Last updated on **Aug 11, 2025**

# Tracing Instructor

[Instructor](<https://python.useinstructor.com/>) is an open-source Python library built on top of Pydantic, simplifying structured LLM outputs with validation, retries, and streaming.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) works with Instructor by enabling auto-tracing for the underlying LLM libraries. For example, if you use Instructor for OpenAI LLMs, you can enable tracing with [`mlflow.openai.autolog()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.openai.html#mlflow.openai.autolog>) and the generated traces will capture the structured outputs from Instructor.

Similarly, you can also trace Instructor with other LLM providers, such as Anthropic, Gemini, and LiteLLM, by enabling the corresponding autologging in MLflow.

note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call the appropriate autolog function (for example `mlflow.openai.autolog()` or`mlflow.anthropic.autolog()`) to enable automatic tracing for this integration.

### Example Usageâ

The following example shows how to trace Instructor call that wraps an OpenAI API.

Python
    
    
    import instructor  
    from pydantic import BaseModel  
    from openai import OpenAI  
    import mlflow  
      
    # Use other autologging function e.g., mlflow.anthropic.autolog() if you are using Instructor with different LLM providers  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking on Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/instructor-demo")  
      
      
    # Use Instructor as usual  
    class ExtractUser(BaseModel):  
        name: str  
        age: int  
      
      
    client = instructor.from_openai(OpenAI())  
      
    res = client.chat.completions.create(  
        model="gpt-4o-mini",  
        response_model=ExtractUser,  
        messages=[{"role": "user", "content": "John Doe is 30 years old."}],  
    )  
    print(f"Name: {res.name}, Age:{res.age}")  
    

## Next stepsâ

  * [Understand tracing concepts](</aws/en/mlflow3/genai/tracing/tracing-101>) \- Learn how MLflow captures and organizes trace data
  * [Debug and observe your app](</aws/en/mlflow3/genai/tracing/observe-with-traces/>) \- Use the Trace UI to analyze your Instructor application's behavior
  * [Evaluate your app's quality](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) \- Set up quality assessment for your structured output application
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/app-instrumentation/ -->

On this page

Last updated on **Nov 26, 2025**

# Add traces to applications: automatic and manual tracing

Learn about the different approaches you can take to add traces to Python and TypeScript generative AI application.

MLflow has three approaches to tracing for Python and [TypeScript](</aws/en/mlflow3/genai/tracing/app-instrumentation/typescript-sdk>).

  * [**Automatic**](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>) \- Add one line [`mlflow.<library>.autolog()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.autolog>) to automatically capture app logic for 20+ [supported libraries](</aws/en/mlflow3/genai/tracing/integrations/>).
  * [**Manual**](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/>) \- Designed for custom logic and complex workflows, control what gets traced using [Function Decorator APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>) or [low-level APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/low-level-api>).
  * [**Combined**](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic#combine-manual-automatic>) \- Mix both approaches for complete coverage.



## Which approach should I use?â

Start with automatic tracing. It's the fastest way to get traces working. Add manual tracing later if you need more control.

**Scenario**| **Recommendations**| **Use one GenAI library**|  Use [automatic tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>) for your selected library| **Use LLM SDKs directly**| 

  * Use [automatic tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>) for the API library
  * Add manual tracing decorators to [combine](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic#combine-manual-automatic>) multiple LLM calls into a single trace

| **Use multiple GenAI libraries or SDKs**| 

  * Enable [automatic tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>) for each framework / SDK
  * Add manual tracing decorators to [combine](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic#combine-manual-automatic>) calls to multiple frameworks or SDKs into a single trace

| **All other scenarios or you need more control**|  Use manual tracing:

  * Start with the [Function Decorator APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>)
  * Use the [low-level APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/low-level-api>) only if the Function Decorator APIs don't give you enough control

  
---|---
<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/ -->

On this page

Last updated on **Dec 5, 2025**

# Manual tracing

While MLflow's [automatic tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic>) provides instant observability for supported frameworks, manual tracing gives you complete control over how your GenAI applications are instrumented. This flexibility is essential for building production-ready applications that require detailed monitoring and debugging capabilities.

## When to use manual tracingâ

Manual tracing is the right choice when you need:

Fine-grained control over trace structure

  * Define exactly which parts of your code to trace
  * Create custom hierarchies of spans
  * Control span boundaries and relationships



Custom framework instrumentation

  * Instrument proprietary or internal frameworks
  * Add tracing to custom LLM wrappers
  * Support new libraries before official integration



Advanced workflow scenarios

  * Multi-threaded or async operations
  * Streaming responses with custom aggregation
  * Complex nested operations
  * Custom trace metadata and attributes



## Which API should I use?â

Choose the right manual tracing approach for your needs:

**Feature**| **[Function decorators](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator>)**| **[Span tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/span-tracing>)**| **[Low-Level APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/low-level-api>)**| **Use case**|  Trace entire functions with one-line decorator. Minimal code changes required.| Trace arbitrary code blocks within functions for fine-grained control.| Direct control over trace lifecycle for complex scenarios.| **Automatic Parent-Child**|  Yes| Yes| No - manual management| **Exception Handling**|  Automatic| Automatic| Manual| **Works with Auto-trace**|  Yes| Yes| No| **Thread Safety**|  Automatic| Automatic| Manual| **Custom Trace IDs**|  No| No| Yes  
---|---|---|---
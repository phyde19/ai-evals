<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/ -->

On this page

Last updated on **Nov 26, 2025**

# MLflow 3 for GenAI

MLflow 3 for GenAI is an open platform that unifies tracking, evaluation, and observability for GenAI apps and agents throughout the development and production lifecycle. It includes realtime trace logging, built-in and custom scorers, incorporation of human feedback, and version tracking to help you efficiently evaluate and improve app quality during development and continue tracking and improving quality in production.

Managed MLflow on Databricks extends open source MLflow with capabilities designed for production GenAI applications, including enterprise-ready governance, fully managed hosting, production-level scaling, and integration with your data in the Databricks lakehouse and Unity Catalog.

For information about agent evaluation in MLflow 2, see [Agent Evaluation (MLflow 2)](</aws/en/generative-ai/agent-evaluation/>) and the [migration guide](</aws/en/mlflow3/genai/agent-eval-migration>). For MLflow 3, the Agent Evaluation SDK methods have been integrated with Databricks-managed MLflow.

For a set of tutorials to get you started, see Get started.

## How MLflow 3 helps optimize GenAI app qualityâ

Evaluating GenAI applications and agents is more complex than evaluating traditional software. Inputs and outputs are often free-form text, and many different outputs can be considered correct. Quality depends not only on correctness but also on factors like precision, length, completeness, appropriateness, and other criteria specific to the use case. Because LLMs are inherently non-deterministic, and GenAI agents include additional components such as retrievers and tools, their responses can vary from run to run.

Developers need concrete quality metrics, automated evaluation, and continuous monitoring to build and deploy robust AI apps. MLflow 3 for GenAI provides these key pieces for efficient development, deployment, and continuous improvement:

  * Tracing automatically logs inputs, intermediate steps, and outputs and provides the data foundation for evaluation and monitoring.
  * Built-in and custom LLM judges and scorers let you define various aspects of quality and customize metrics to your use case.
  * Review apps for expert feedback allow you to collect and label datasets for evaluation and to align automated judges and scorers with expert judgement.
  * Automated evaluation and monitoring leverage the same judges and scorers during development and production.
  * App and prompt versioning allow you to compare versions and track improvements over iterations.



Using MLflow 3 on Databricks, you can bring AI to your data to help you deeply understand and improve quality. Unity Catalog provides consistent governance for prompts, apps, and traces. Using any model or framework, MLflow supports you throughout the development loop all the way to and in production.

## Get startedâ

Start building better GenAI applications with comprehensive observability and evaluation tools.

Task| Description| [Quick start guide](</aws/en/mlflow3/genai/getting-started/>)| Get up and running in minutes with step-by-step instructions for instrumenting your first application with tracing, running evaluation, and collecting human feedback.| [Get started: MLflow Tracing for GenAI (Databricks Notebook)](</aws/en/mlflow3/genai/getting-started/tracing/tracing-notebook>)| Instrument a simple GenAI app to automatically capture detailed traces for debugging and optimization.| [Tutorial: Evaluate and improve a GenAI application](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>)| Steps you through evaluating an email generation app that uses Retrieval-Augmented Generation (RAG).| [10-minute demo: Collect human feedback](</aws/en/mlflow3/genai/getting-started/human-feedback>)| Collect end-user feedback, add developer annotations, create expert review sessions, and use that feedback to evaluate your GenAI app's quality.  
---|---  
  
##  Tracingâ

MLflow Tracing provides observability and logs the trace data required for evaluation and monitoring.

Feature| Description| [MLflow Tracing](</aws/en/mlflow3/genai/tracing/>)| End-to-end observability for GenAI applications, including complex agent-based systems. Track inputs, outputs, intermediate steps, and metadata for a complete picture of how your app behaves.| [What is tracing?](</aws/en/mlflow3/genai/tracing/tracing-101>)| Introduction to tracing concepts.| [Review your app's behavior and performance](</aws/en/mlflow3/genai/tracing/observe-with-traces/>)| Complete execution visibility allows you to capture prompts, retrievals, tool calls, responses, latency, and costs.| [Production observability](</aws/en/mlflow3/genai/tracing/prod-tracing>)| Use the same instrumentation in development and production environments for consistent evaluation.| [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>)| Analyze traces to identify quality issues, select representative traces, create evaluation datasets, and systematically improve your application.| [Tracing integrations](</aws/en/mlflow3/genai/tracing/integrations/>)| MLflow Tracing is integrated with many libraries and frameworks for automatic tracing that allows you to gain immediate observability into your GenAI applications with minimal setup.  
---|---  
  
##  Evaluation and monitoringâ

Replace manual testing with automated evaluation using built-in and custom LLM judges and scorers that match human expertise and can be applied in both development and production. Every production interaction becomes an opportunity to improve with integrated feedback and evaluation workflows.

Feature| Description| [Evaluate and monitor GenAI agents](</aws/en/mlflow3/genai/eval-monitor/>)| Overview of evaluating and monitoring agents using MLflow 3 on Databricks.| [LLM judges and scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)| MLflow 3 includes built-in LLM judges for safety, relevance, correctness, retrieval quality and more. You can also create custom LLM judges and code-based scorers for your specific business requirements.| [Evaluation](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>)| Run evaluation during development or as part of a release process.| [Production monitoring](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>)| Continuously monitor a sample of production traffic using LLM judges and scorers.| [Collect human feedback](</aws/en/mlflow3/genai/human-feedback/>)| Collect and use feedback from domain experts and end users during development and during production for continuous improvement.  
---|---  
  
##  Manage the GenAI app lifecycleâ

Version, track, and govern your entire GenAI application with enterprise-grade lifecycle management and governance tools.

Feature| Description| [Application versioning](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/version-concepts>)| Track code, parameters, and evaluation metrics for each version.| [Prompt Registry](</aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/>)| Centralized management for versioning and sharing prompts across your organization with A/B testing capabilities and Unity Catalog integration.| Enterprise integration| [Unity Catalog](</aws/en/data-governance/unity-catalog/>). Unified governance for all AI assets with enterprise security, access control, and compliance features.[Data intelligence](</aws/en/ai-bi/>). Connect your GenAI data to your business data in the Databricks Lakehouse and deliver custom analytics to your business stakeholders.[Mosaic AI Agent Serving](</aws/en/mlflow3/genai/tracing/prod-tracing>). Deploy agents to production with scaling and operational rigor.  
---|---
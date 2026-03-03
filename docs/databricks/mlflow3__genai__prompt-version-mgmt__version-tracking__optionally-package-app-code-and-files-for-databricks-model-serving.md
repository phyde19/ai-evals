<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/optionally-package-app-code-and-files-for-databricks-model-serving -->

On this page

Last updated on **Aug 11, 2025**

# Package code for Databricks Model Serving

The [track application versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow>) page shows how to track application versions using `LoggedModel` as a metadata hub linking to external code (such as Git). There are also scenarios where you might need to package your application code directly into the `LoggedModel`.

This is particularly useful for deployment to [Databricks Model Serving](</aws/en/machine-learning/model-serving/create-manage-serving-endpoints>) or for deployments using [Agent Framework](</aws/en/generative-ai/agent-framework/deploy-agent>), which expects self-contained model artifacts.

## When to package code directlyâ

Package your code into a `LoggedModel` when you need:

  * **Self-contained deployment artifacts** that include all code and dependencies.
  * **Direct deployment to serving platforms** without external code dependencies.



This is an optional step for deployment, not the default versioning approach for development iterations.

## How to package codeâ

MLflow recommends using the `ResponsesAgent` interface to package your GenAI applications.

See one of the following to get started:

  * Quickstart. See [build and deploy AI agents quickstart](</aws/en/generative-ai/tutorials/agent-quickstart>).
  * For more details, see [author AI agents in code](</aws/en/generative-ai/agent-framework/author-agent-model-serving>).



Following these pages results in a deployment-ready `LoggedModel` that behaves in the same way as the metadata-only `LoggedModel`. Follow [step 6 of the track application versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/track-application-versions-with-mlflow#eval-versions>) page to link your packaged model version to evaluation results.

## Next stepsâ

  * [Deploy to Model Serving](</aws/en/machine-learning/model-serving/create-manage-serving-endpoints>) \- Deploy your packaged model to production
  * [Link production traces to app versions](</aws/en/mlflow3/genai/prompt-version-mgmt/version-tracking/link-production-traces-to-app-versions>) \- Track deployed versions in production
  * [Run scorers in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) \- Monitor deployed model quality
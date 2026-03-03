<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/overview/oss-managed-diff -->

On this page

Last updated on **Nov 26, 2025**

# Open source vs. managed MLflow on Databricks

This page is meant to help [open source MLflow](<https://mlflow.org/>) users get familiar with using MLflow on Databricks. Databricks-managed MLflow uses the same APIs but provides additional capabilities through integrations with the broader Databricks platform.

## Benefits of managed MLflow on Databricksâ

Open source MLflow provides the core data model, API, and SDK. This means your data and workloads are always portable.

Managed MLflow on Databricks adds:

  * **Enterprise-grade governance and security** through integration with the Databricks platform, Lakehouse, and Unity Catalog. Your AI and ML data, tools, agents, models, and other assets can be governed and used in the same platform as the rest of your data and workloads.
  * **Fully managed hosting** on production-ready, scalable servers
  * **Integrations for development and production** with the broader Mosaic AI platform



See the [Managed MLflow product page](<https://www.databricks.com/product/managed-mlflow>) for more details on benefits, and see the rest of this page to learn about technical details.

tip

**Your data is always yours** \- The core data model and APIs are completely open source. You can export and use your MLflow data anywhere.

## Additional capabilities on Databricksâ

This section lists important capabilities enabled on managed MLflow through integrations with the broader Databricks platform. For overviews of all capabilities of MLflow for GenAI, see [MLflow 3 for GenAI](</aws/en/mlflow3/genai/>) and the [open source GenAI documentation](<https://mlflow.org/docs/latest/genai/>).

### Enterprise-grade governance and securityâ

  * **Enterprise governance with Unity Catalog**: Models, feature tables, vector indexes, tools, and more are governed centrally under Unity Catalog. When deploying agents, authentication for agent, data, and tool access can be precisely controlled using both [authentication passthrough and on-behalf-of-user authentication](</aws/en/generative-ai/agent-framework/agent-authentication-model-serving>).
  * **Lakehouse data integration** : Leverage [AI/BI](</aws/en/ai-bi/>) Genie spaces and dashboards and [Databricks SQL](</aws/en/sql/>) to analyze logs and traces from MLflow experiments.
  * **Security and management** : MLflow permissions follow the same governance patterns as the broader Databricks platform:
    * Workspace objects such as experiments follow [workspace permissions](</aws/en/security/auth/access-control/#mlflow-experiment-acls>).
    * Unity Catalog objects such as registered models follow [Unity Catalog privileges](</aws/en/data-governance/unity-catalog/manage-privileges/privileges>).
    * UI and API [authentication and access](</aws/en/security/auth/>) match the Databricks platform and REST API.
  * **Auditing** : [System tables](</aws/en/admin/system-tables/mlflow>) provide usage and audit logs for managed MLflow.



### Fully managed hosting on production-ready serversâ

  * **Fully managed** : Databricks provides MLflow servers with automatic updates, designed for scalability and production. For details, see [Resource limits](</aws/en/resources/limits>).
  * **Trusted platform** : Managed MLflow is used by [thousands of customers](<https://www.databricks.com/customers>) across the globe.



### Integrations for development and productionâ

Development of AI and ML is streamlined by integrations such as:

  * **Notebook integration** : Databricks notebooks are automatically connected to the MLflow server and can use both [notebook experiments and workspace experiments](</aws/en/mlflow/experiments>) for tracking and sharing results. Databricks notebooks support [autologging for MLflow tracking](</aws/en/mlflow/databricks-autologging>). For GenAI, Databricks notebooks can display an inline tracing UI for interactive analysis.
  * **GenAI human feedback tools** : For GenAI evaluation, Databricks provides a [Review App for human feedback](</aws/en/mlflow3/genai/human-feedback/#expert-feedback>) that includes a [Chat UI](</aws/en/mlflow3/genai/human-feedback/expert-feedback/live-app-testing>) for vibe checks and [expert feedback UI](</aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces>) for labeling traces.



Production AI and ML are facilitated by integrations such as:

  * **Infrastructure-as-code for CI/CD** : Manage MLflow experiments, models, and more with [Databricks Asset Bundles](</aws/en/dev-tools/bundles/resources#experiment>) and [MLOps Stacks](</aws/en/machine-learning/mlops/mlops-stacks>).
  * **Model deployment using CI/CD** : [MLflow 3 deployment jobs](</aws/en/mlflow/deployment-job>) integrate Databricks Workflows with Unity Catalog to automate staged deployment of ML models.
  * **Feature Store integration** : [Databricks Feature Store + MLflow integration](</aws/en/machine-learning/feature-store/train-models-with-feature-store>) provides simpler deployment for ML models that use feature tables.
  * **GenAI production monitoring** : Databricks provides a [production monitoring service](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) that continuously evaluates a sample of your production traffic using LLM judges and scorers. This is powered by [production-scale trace ingestion](</aws/en/mlflow3/genai/tracing/prod-tracing>) that includes storing traces to Unity Catalog tables.



note

Open source telemetry collection was introduced in MLflow 3.2.0, and is disabled on Databricks by default. For more details, refer to the [MLflow usage tracking documentation](<https://mlflow.org/docs/latest/community/usage-tracking/>).

## Next stepsâ

Get started with MLflow on Databricks:

  * Create a free trial [Databricks account](<https://signup.databricks.com/?destination_url=/ml/experiments-signup?source=DB_DOCS&dbx_source=TRY_MLFLOW&signup_experience_step=EXPRESS&provider=MLFLOW>) to use Databricks-managed MLflow
  * [Tutorial: Connect your development environment to MLflow](</aws/en/mlflow3/genai/getting-started/connect-environment>)
  * [Get started: MLflow 3 for GenAI](</aws/en/mlflow3/genai/getting-started/>)
  * [Get started with MLflow 3 for models](</aws/en/mlflow/mlflow-3-install>)



Related reference material:

  * [Open source MLflow for GenAI documentation](<https://mlflow.org/docs/latest/genai/>)
  * [Databricks REST API](<https://docs.databricks.com/api/workspace/introduction>), which includes the MLflow API
  * [Databricks SDKs](</aws/en/dev-tools/sdks>), which include MLflow operations
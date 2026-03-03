<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/agent-eval-migration-reference -->

On this page

Last updated on **Dec 18, 2025**

# Migrate to MLflow 3 from Agent Evaluation: Quick reference

This quick reference summarizes key changes for migrating from Agent Evaluation and MLflow 2 to the improved APIs in MLflow 3. See the full guide at [Migrate to MLflow 3 from Agent Evaluation](</aws/en/mlflow3/genai/agent-eval-migration>).

##  Import updatesâ

Python
    
    
    ### Old imports ###  
    from mlflow import evaluate  
    from databricks.agents.evals import metric  
    from databricks.agents.evals import judges  
      
    from databricks.agents import review_app  
      
    ### New imports ###  
    from mlflow.genai import evaluate  
    from mlflow.genai.scorers import scorer  
    from mlflow.genai import judges  
    # For predefined scorers:  
    from mlflow.genai.scorers import (  
        Correctness, Guidelines, ExpectationsGuidelines,  
        RelevanceToQuery, Safety, RetrievalGroundedness,  
        RetrievalRelevance, RetrievalSufficiency  
    )  
      
    import mlflow.genai.labeling as labeling  
    import mlflow.genai.label_schemas as schemas  
    

## Evaluation functionâ

MLflow 2.x| MLflow 3.x| `mlflow.evaluate()`| `mlflow.genai.evaluate()`| `model=my_agent`| `predict_fn=my_agent`| `model_type="databricks-agent"`| _(not needed)_| `extra_metrics=[...]`| `scorers=[...]`| `evaluator_config={...}`| _(configuration in scorers)_  
---|---  
  
## Judge selectionâ

MLflow 2.x| MLflow 3.x| Automatically runs all applicable judges based on data| Must explicitly specify which scorers to use| Use `evaluator_config` to limit judges| Pass desired scorers in `scorers` parameter| `global_guidelines` in config| Use `Guidelines()` scorer| Judges selected based on available data fields| You control exactly which scorers run  
---|---  
  
## Data fieldsâ

MLflow 2.x Field| MLflow 3.x Field| Description| `request`| `inputs`| Agent input| `response`| `outputs`| Agent output| `expected_response`| `expectations`| Ground truth| `retrieved_context`| Accessed via traces| Context from trace| `guidelines`| Part of scorer config| Moved to scorer level  
---|---|---  
  
## Custom metrics and scorersâ

MLflow 2.x| MLflow 3.x| Notes| `@metric` decorator| `@scorer` decorator| New name| `def my_metric(request, response, ...)`| `def my_scorer(inputs, outputs, expectations, traces)`| Simplified| Multiple expected_* params| Single `expectations` param that is a dict| Consolidated| `custom_expected`| Part of `expectations` dict| Simplified| `request` parameter| `inputs` parameter| Consistent naming| `response` parameter| `outputs` parameter| Consistent naming  
---|---|---  
  
## Result accessâ

MLflow 2.x| MLflow 3.x| `results.tables['eval_results']`| `mlflow.search_traces(run_id=results.run_id)`| Direct DataFrame access| Iterate through traces and assessments  
---|---  
  
## LLM judgesâ

Use Case| MLflow 2.x| MLflow 3.x Recommended| Basic correctness check| `judges.correctness()` in `@metric`| `Correctness()` scorer or `judges.is_correct()` judge| Safety evaluation| `judges.safety()` in `@metric`| `Safety()` scorer or `judges.is_safe()` judge| Global guidelines| `judges.guideline_adherence()`| `Guidelines()` scorer or `judges.meets_guidelines()` judge| Per-eval-set-row guidelines| `judges.guideline_adherence()` with expected_*| `ExpectationsGuidelines()` scorer or `judges.meets_guidelines()` judge| Check for factual support| `judges.groundedness()`| `judges.is_grounded()` or `RetrievalGroundedness()` scorer| Check relevance of context| `judges.relevance_to_query()`| `judges.is_context_relevant()` or `RelevanceToQuery()` scorer| Check relevance of context chunks| `judges.chunk_relevance()`| `judges.is_context_relevant()` or `RetrievalRelevance()` scorer| Check completeness of context| `judges.context_sufficiency()`| `judges.is_context_sufficient()` or `RetrievalSufficiency()` scorer| Complex custom logic| Direct judge calls in `@metric`| Predefined scorers or `@scorer` with judge calls  
---|---|---  
  
## Human feedbackâ

MLflow 2.x| MLflow 3.x| `databricks.agents.review_app`| `mlflow.genai.labeling`| `databricks.agents.datasets`| `mlflow.genai.datasets`| `review_app.label_schemas.*`| `mlflow.genai.label_schemas.*`| `app.create_labeling_session()`| `labeling.create_labeling_session()`  
---|---  
  
## Common migration commandsâ

Bash
    
    
    # Find old evaluate calls  
    grep -r "mlflow.evaluate" . --include="*.py"  
      
    # Find old metric decorators  
    grep -r "@metric" . --include="*.py"  
      
    # Find old data fields  
    grep -r '"request":\|"response":\|"expected_response":' . --include="*.py"  
      
    # Find old imports  
    grep -r "databricks.agents" . --include="*.py"  
    

## Additional resourcesâ

  * [MLflow 3 GenAI Evaluation Guide](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>)
  * [Custom Scorers Documentation](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>)
  * [Human Feedback with labeling sessions](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-sessions>)
  * [Predefined Judge Scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)
  * [MLflow Tracing Guide](</aws/en/mlflow3/genai/tracing/>)



For additional support during migration, consult the MLflow documentation or reach out to your Databricks support team.
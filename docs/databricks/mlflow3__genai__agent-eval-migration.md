<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/agent-eval-migration -->

On this page  
  
Last updated on **Dec 18, 2025**

# Migrate to MLflow 3 from Agent Evaluation

Agent Evaluation is now integrated with MLflow 3 on Databricks. The Agent Evaluation SDK methods are now exposed through the `mlflow[databricks]>=3.1` SDK, under the [`mlflow.genai`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html>) namespace. MLflow 3 introduces:

  * **Refreshed UI** that mirrors all SDK functionality
  * **New SDK** [`mlflow.genai`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html>) with simplified APIs for running evaluation, human labeling, and managing evaluation datasets
  * **Enhanced tracing** with a production-scale trace ingestion backend that provides real-time observability
  * **Streamlined human feedback** collection
  * **Improved LLM judges** as built-in scorers



This guide helps you migrate from Agent Evaluation (MLflow 2.x with `databricks-agents<1.0`) to MLflow 3. This detailed guide is also available in a [quick reference](</aws/en/mlflow3/genai/agent-eval-migration-reference>) format.

important

MLflow 3 with Agent Evaluation only works on Managed MLflow, not open source MLflow. View the [managed vs. open source MLflow page](</aws/en/mlflow3/genai/overview/oss-managed-diff>) to understand the differences between managed and open source MLflow in more depth.

## Migration checklistâ

Get started by using this checklist. Each item links to details in sections below.

### Evaluation APIâ

  * Update imports from `databricks.agents` to `mlflow.genai.*`
  * Convert `@metric` decorators to `@scorer`
    * Update custom metric/scorer function signatures
  * Replace `mlflow.evaluate()` with `mlflow.genai.evaluate()`
    * Update parameter names (`model` â `predict_fn`, `extra_metrics` â `scorers`)
    * Update data field names (`request` â `inputs`, `response` â `outputs`, `expected*` â `expectations`)
    * Replace `evaluator_config` with scorer-level configuration
    * Update result access to use `mlflow.search_traces()`



### LLM judgesâ

  * Replace direct judge calls with predefined scorers where possible
  * Update `judges.guideline_adherence()` to `judges.meets_guidelines()` or `Guidelines()` scorer
  * Update judge function parameter names to match new API
  * Consider using `ExpectationsGuidelines()` for ground-truth based guidelines



### Human feedbackâ

  * Update labeling session and review app imports to `mlflow.genai.labeling`
  * Update label schema imports to `mlflow.genai.label_schemas`
  * Update logic for syncing feedback to datasets



### Common pitfalls to avoidâ

  * Remember to update data field names in your DataFrames
  * Remember that `model_type="databricks-agent"` is no longer needed
  * Ensure custom scorers return valid values ("yes"/"no" for pass/fail)
  * Use `search_traces()` instead of accessing result tables directly
  * Update any hardcoded namespace references in your code
  * **Remember to explicitly specify all scorers** \- MLflow 3 does not automatically run judges
  * Convert `global_guidelines` from config to explicit `Guidelines()` scorers



##  Evaluation API migrationâ

###  Import updatesâ

The list below summarizes imports to update, with details and examples in each subsection below.

Python
    
    
    # Old imports  
    from mlflow import evaluate  
    from databricks.agents.evals import metric  
    from databricks.agents.evals import judges  
      
    # New imports  
    from mlflow.genai import evaluate  
    from mlflow.genai.scorers import scorer  
    from mlflow.genai import judges  
    # For predefined scorers:  
    from mlflow.genai.scorers import (  
        Correctness, Guidelines, ExpectationsGuidelines,  
        RelevanceToQuery, Safety, RetrievalGroundedness,  
        RetrievalRelevance, RetrievalSufficiency  
    )  
    

### From `mlflow.evaluate()` to `mlflow.genai.evaluate()`â

The core evaluation API has moved to a dedicated GenAI namespace with cleaner parameter names.

**Key API changes:**

MLflow 2.x| MLflow 3.x| Notes| `mlflow.evaluate()`| `mlflow.genai.evaluate()`| New namespace| `model` parameter| `predict_fn` parameter| More descriptive name| `model_type="databricks-agent"`| Not needed| Automatically detected| `extra_metrics=[...]`| `scorers=[...]`| Clearer terminology| `evaluator_config={...}`| Not needed| Part of scorers  
---|---|---  
  
**Data field mapping:**

MLflow 2.x Field| MLflow 3.x Field| Description| `request`| `inputs`| Agent input| `response`| `outputs`| Agent output| `expected_response`| `expectations`| Ground truth| `retrieved_context`| Accessed via traces| Context from trace| `guidelines`| Part of scorer config| Moved to scorer level  
---|---|---  
  
#### Example: Basic evaluationâ

**MLflow 2.x:**

Python
    
    
    import mlflow  
    import pandas as pd  
      
    eval_data = [  
            {  
                "request":  "What is MLflow?",  
                "response": "MLflow is an open-source platform for managing ML lifecycle.",  
                "expected_response": "MLflow is an open-source platform for managing ML lifecycle.",  
            },  
            {  
                "request":  "What is Databricks?",  
                "response": "Databricks is a unified analytics platform.",  
                "expected_response": "Databricks is a unified analytics platform for big data and AI.",  
            },  
        ]  
      
    # Note: By default, MLflow 2.x runs all applicable judges automatically  
    results = mlflow.evaluate(  
        data=eval_data,  
        model=my_agent,  
        model_type="databricks-agent",  
        evaluator_config={  
            "databricks-agent": {  
                # Optional: limit to specific judges  
                # "metrics": ["correctness", "safety"],  
                # Optional: add global guidelines  
                "global_guidelines": {  
                    "clarity": ["Response must be clear and concise"]  
                }  
            }  
        }  
    )  
      
    # Access results  
    eval_df = results.tables['eval_results']  
    

**MLflow 3.x:**

Python
    
    
    import mlflow  
    import pandas as pd  
    from mlflow.genai.scorers import Guidelines  
      
    eval_data = [  
            {  
                "inputs": {"request": "What is MLflow?"},  
                "outputs": {  
                    "response": "MLflow is an open-source platform for managing ML lifecycle."  
                },  
                "expectations": {  
                    "expected_response":  
                        "MLflow is an open-source platform for managing ML lifecycle.",  
      
                },  
            },  
            {  
                "inputs": {"request": "What is Databricks?"},  
                "outputs": {"response": "Databricks is a unified analytics platform."},  
                "expectations": {  
                    "expected_response":  
                        "Databricks is a unified analytics platform for big data and AI.",  
      
                },  
            },  
        ]  
      
    # Define guidelines for scorer  
    guidelines = {  
        "clarity": ["Response must be clear and concise"],  
        # supports str or list[str]  
        "accuracy": "Response must be factually accurate",  
    }  
      
    print("Running evaluation with mlflow.genai.evaluate()...")  
      
    with mlflow.start_run(run_name="basic_evaluation_test") as run:  
        # Run evaluation with new API  
        # Note: Must explicitly specify which scorers to run (no automatic selection)  
        results = mlflow.genai.evaluate(  
            data=eval_data,  
            scorers=[  
                Correctness(),  # Requires expectations.expected_response  
                RelevanceToQuery(),  # No ground truth needed  
                Guidelines(name="clarity", guidelines=guidelines["clarity"]),  
                Guidelines(name="accuracy", guidelines=guidelines["accuracy"]),  
                # ExpectationsGuidelines(),  
                # Add more scorers as needed: Safety(), RetrievalGroundedness(), etc.  
            ],  
        )  
      
    # Access results using search_traces  
    traces = mlflow.search_traces(  
            run_id=results.run_id,  
    )  
    

###  Accessing evaluation resultsâ

In MLflow 3, evaluation results are stored as traces with assessments. Use `mlflow.search_traces()` to access detailed results:

Python
    
    
    # Access results using search_traces  
    traces = mlflow.search_traces(  
        run_id=results.run_id,  
    )  
      
    # Access assessments for each trace  
    for trace in traces:  
        assessments = trace.info.assessments  
        for assessment in assessments:  
            print(f"Scorer: {assessment.name}")  
            print(f"Value: {assessment.value}")  
            print(f"Rationale: {assessment.rationale}")  
    

### Evaluating an MLflow LoggedModelâ

In MLflow 2.x, you could pass a logged MLflow model (such as a PyFunc model or one logged by the [Agent Framework](</aws/en/generative-ai/agent-framework/author-agent-model-serving>)) directly to `mlflow.evaluate()`. In MLflow 3.x, you need to wrap the model in a predict function to handle parameter mapping.

This wrapper is necessary because `mlflow.genai.evaluate()` expects a predict function that accepts the keys in the `inputs` dict from your dataset as keyword arguments, while most logged models accept a single input parameter (e.g., `model_inputs` for PyFunc models or similar interfaces for LangChain models).

The predict function serves as a translation layer between the evaluation framework's named parameters and the model's expected input format.

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import Safety  
      
    # Make sure to load your logged model outside of the predict_fn so MLflow only loads it once!  
    model = mlflow.pyfunc.load_model("models:/chatbot/staging")  
      
    def evaluate_model(question: str) -> dict:  
        return model.predict({"question": question})  
      
    results = mlflow.genai.evaluate(  
        data=[{"inputs": {"question": "Tell me about MLflow"}}],  
        predict_fn=evaluate_model,  
        scorers=[Safety()]  
    )  
    

###  Custom metrics to scorers migrationâ

Custom evaluation functions (`@metric`) now use the `@scorer` decorator with a simplified signature.

**Key changes:**

MLflow 2.x| MLflow 3.x| Notes| `@metric` decorator| `@scorer` decorator| New name| `def my_metric(request, response, ...)`| `def my_scorer(inputs, outputs, expectations, traces)`| Simplified| Multiple expected_* params| Single `expectations` param that is a dict| Consolidated| `custom_expected`| Part of `expectations` dict| Simplified| `request` parameter| `inputs` parameter| Consistent naming| `response` parameter| `outputs` parameter| Consistent naming  
---|---|---  
  
#### Example: Pass/fail scorerâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import metric  
      
    @metric  
    def response_length_check(request, response, expected_response=None):  
        """Check if response is within acceptable length."""  
        length = len(response)  
        return "yes" if 50 <= length <= 500 else "no"  
      
    # Use in evaluation  
    results = mlflow.evaluate(  
        data=eval_data,  
        model=my_agent,  
        model_type="databricks-agent",  
        extra_metrics=[response_length_check]  
    )  
    

**MLflow 3.x:**

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import scorer  
      
      
    # Sample agent function  
    @mlflow.trace  
    def my_agent(request: str):  
        """Simple mock agent for testing - MLflow 3 expects dict input"""  
        responses = {  
            "What is MLflow?": "MLflow is an open-source platform for managing ML lifecycle.",  
            "What is Databricks?": "Databricks is a unified analytics platform.",  
        }  
        return {"response": responses.get(request, "I don't have information about that.")}  
      
      
    @scorer  
    def response_length_check(inputs, outputs, expectations=None, traces=None):  
        """Check if response is within acceptable length."""  
        length = len(outputs)  
        return "yes" if 50 <= length <= 500 else "no"  
      
    # Use in evaluation  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[response_length_check]  
    )  
    

#### Example: Numeric scorer with Assessmentâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import metric, Assessment  
      
    def calculate_similarity(response, expected_response):  
        return 1  
      
    @metric  
    def semantic_similarity(response, expected_response):  
        """Calculate semantic similarity score."""  
        # Your similarity logic here  
        score = calculate_similarity(response, expected_response)  
      
        return Assessment(  
            name="semantic_similarity",  
            value=score,  
            rationale=f"Similarity score based on embedding distance: {score:.2f}"  
        )  
    

**MLflow 3.x:**

Python
    
    
    from mlflow.genai.scorers import scorer  
    from mlflow.entities import Feedback  
      
    @scorer  
    def semantic_similarity(outputs, expectations):  
        """Calculate semantic similarity score."""  
        # Your similarity logic here  
        expected = expectations.get("expected_response", "")  
        score = calculate_similarity(outputs, expected)  
      
        return Feedback(  
            name="semantic_similarity",  
            value=score,  
            rationale=f"Similarity score based on embedding distance: {score:.2f}"  
        )  
    

##  LLM judges migrationâ

### Key differences in judge behaviorâ

**Automatic judge selection:**

MLflow 2.x| MLflow 3.x| Automatically runs all applicable judges based on data| Must explicitly specify which scorers to use| Use `evaluator_config` to limit judges| Pass desired scorers in `scorers` parameter| `global_guidelines` in config| Use `Guidelines()` scorer| Judges selected based on available data fields| You control exactly which scorers run  
---|---  
  
**MLflow 2.x automatic judge selection:**

  * Without ground truth: runs `chunk_relevance`, `groundedness`, `relevance_to_query`, `safety`, `guideline_adherence`
  * With ground truth: also runs `context_sufficiency`, `correctness`



**MLflow 3.x explicit scorer selection:**

  * You must explicitly list scorers you want to run
  * More control but requires being explicit about evaluation needs



### Migration pathsâ

Use Case| MLflow 2.x| MLflow 3.x Recommended| Basic correctness check| `judges.correctness()` in `@metric`| `Correctness()` scorer or `judges.is_correct()` judge| Safety evaluation| `judges.safety()` in `@metric`| `Safety()` scorer or `judges.is_safe()` judge| Global guidelines| `judges.guideline_adherence()`| `Guidelines()` scorer or `judges.meets_guidelines()` judge| Per-eval-set-row guidelines| `judges.guideline_adherence()` with expected_*| `ExpectationsGuidelines()` scorer or `judges.meets_guidelines()` judge| Check for factual support| `judges.groundedness()`| `judges.is_grounded()` or `RetrievalGroundedness()` scorer| Check relevance of context| `judges.relevance_to_query()`| `judges.is_context_relevant()` or `RelevanceToQuery()` scorer| Check relevance of context chunks| `judges.chunk_relevance()`| `judges.is_context_relevant()` or `RetrievalRelevance()` scorer| Check completeness of context| `judges.context_sufficiency()`| `judges.is_context_sufficient()` or `RetrievalSufficiency()` scorer| Complex custom logic| Direct judge calls in `@metric`| Predefined scorers or `@scorer` with judge calls  
---|---|---  
  
MLflow 3 provides two ways to use LLM judges:

  1. **Predefined scorers** \- Ready-to-use scorers that wrap judges with automatic trace parsing
  2. **Direct judge calls** \- Call judges directly within custom scorers for more control



### Controlling which judges runâ

#### Example: Specifying judges to runâ

**MLflow 2.x (limiting default judges):**

Python
    
    
    import mlflow  
      
    # By default, runs all applicable judges  
    # Use evaluator_config to limit which judges run  
    results = mlflow.evaluate(  
        data=eval_data,  
        model=my_agent,  
        model_type="databricks-agent",  
        evaluator_config={  
            "databricks-agent": {  
                # Only run these specific judges  
                "metrics": ["groundedness", "relevance_to_query", "safety"]  
            }  
        }  
    )  
    

**MLflow 3.x (explicit scorer selection):**

Python
    
    
    from mlflow.genai.scorers import (  
        RetrievalGroundedness,  
        RelevanceToQuery,  
        Safety  
    )  
      
    # Must explicitly specify which scorers to run  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[  
            RetrievalGroundedness(),  
            RelevanceToQuery(),  
            Safety()  
        ]  
    )  
    

### Comprehensive migration exampleâ

This example shows migrating an evaluation that uses multiple judges with custom configuration:

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import judges, metric  
    import mlflow  
      
    # Custom metric using judge  
    @metric  
    def check_no_pii(request, response, retrieved_context):  
        """Check if retrieved context contains PII."""  
        context_text = '\n'.join([c['content'] for c in retrieved_context])  
      
        return judges.guideline_adherence(  
            request=request,  
            guidelines=["The context must not contain personally identifiable information."],  
            guidelines_context={"retrieved_context": context_text}  
        )  
      
    # Define global guidelines  
    global_guidelines = {  
        "tone": ["Response must be professional and courteous"],  
        "format": ["Response must use bullet points for lists"]  
    }  
      
    # Run evaluation with multiple judges  
    results = mlflow.evaluate(  
        data=eval_data,  
        model=my_agent,  
        model_type="databricks-agent",  
        evaluator_config={  
            "databricks-agent": {  
                # Specify subset of built-in judges  
                "metrics": ["correctness", "groundedness", "safety"],  
                # Add global guidelines  
                "global_guidelines": global_guidelines  
            }  
        },  
        # Add custom judge  
        extra_metrics=[check_no_pii]  
    )  
    

**MLflow 3.x:**

Python
    
    
    from mlflow.genai.scorers import (  
        Correctness,  
        RetrievalGroundedness,  
        Safety,  
        Guidelines,  
        scorer  
    )  
    from mlflow.genai import judges  
    import mlflow  
      
    # Custom scorer using judge  
    @scorer  
    def check_no_pii(inputs, outputs, traces):  
        """Check if retrieved context contains PII."""  
        # Extract retrieved context from trace  
        retrieved_context = traces.data.spans[0].attributes.get("retrieved_context", [])  
        context_text = '\n'.join([c['content'] for c in retrieved_context])  
      
        return judges.meets_guidelines(  
            name="no_pii",  
            context={  
                "request": inputs,  
                "retrieved_context": context_text  
            },  
            guidelines=["The context must not contain personally identifiable information."]  
        )  
      
    # Run evaluation with explicit scorers  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[  
            # Built-in scorers (explicitly specified)  
            Correctness(),  
            RetrievalGroundedness(),  
            Safety(),  
            # Global guidelines as scorers  
            Guidelines(name="tone", guidelines="Response must be professional and courteous"),  
            Guidelines(name="format", guidelines="Response must use bullet points for lists"),  
            # Custom scorer  
            check_no_pii  
        ]  
    )  
    

###  Migrating to predefined judge scorersâ

MLflow 3 provides predefined scorers that wrap the LLM judges, making them easier to use with `mlflow.genai.evaluate()`.

#### Example: Correctness judgeâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import judges, metric  
      
    @metric  
    def check_correctness(request, response, expected_response):  
        """Check if response is correct."""  
        return judges.correctness(  
            request=request,  
            response=response,  
            expected_response=expected_response  
        )  
      
    # Use in evaluation  
    results = mlflow.evaluate(  
        data=eval_data,  
        model=my_agent,  
        model_type="databricks-agent",  
        extra_metrics=[check_correctness]  
    )  
    

**MLflow 3.x (Option 1: Using predefined scorer):**

Python
    
    
    from mlflow.genai.scorers import Correctness  
      
    # Use predefined scorer directly  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[Correctness()]  
    )  
    

**MLflow 3.x (Option 2: Custom scorer with judge):**

Python
    
    
    from mlflow.genai.scorers import scorer  
    from mlflow.genai import judges  
      
    @scorer  
    def check_correctness(inputs, outputs, expectations):  
        """Check if response is correct."""  
        return judges.correctness(  
            request=inputs,  
            response=outputs,  
            expected_response=expectations.get("expected_response", "")  
        )  
      
    # Use in evaluation  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[check_correctness]  
    )  
    

#### Example: Safety judgeâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import judges, metric  
      
    @metric  
    def check_safety(request, response):  
        """Check if response is safe."""  
        return judges.safety(  
            request=request,  
            response=response  
        )  
    

**MLflow 3.x:**

Python
    
    
    from mlflow.genai.scorers import Safety  
      
    # Use predefined scorer  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[Safety()]  
    )  
    

#### Example: Relevance judgeâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import judges, metric  
      
    @metric  
    def check_relevance(request, response):  
        """Check if response is relevant to query."""  
        return judges.relevance_to_query(  
            request=request,  
            response=response  
        )  
    

**MLflow 3.x:**

Python
    
    
    from mlflow.genai.scorers import RelevanceToQuery  
      
    # Use predefined scorer  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[RelevanceToQuery()]  
    )  
    

#### Example: Groundedness judgeâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import judges, metric  
      
    @metric  
    def check_groundedness(response, retrieved_context):  
        """Check if response is grounded in context."""  
        context_text = '\n'.join([c['content'] for c in retrieved_context])  
        return judges.groundedness(  
            response=response,  
            context=context_text  
        )  
    

**MLflow 3.x:**

Python
    
    
    from mlflow.genai.scorers import RetrievalGroundedness  
      
    # Use predefined scorer (automatically extracts context from trace)  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[RetrievalGroundedness()]  
    )  
    

###  Migrating guideline adherence to meets_guidelinesâ

The `guideline_adherence` judge has been renamed to `meets_guidelines` with a cleaner API.

**MLflow 2.x:**

Python
    
    
    from databricks.agents.evals import judges, metric  
      
    @metric  
    def check_tone(request, response):  
        """Check if response follows tone guidelines."""  
        return judges.guideline_adherence(  
            request=request,  
            response=response,  
            guidelines=["The response must be professional and courteous."]  
        )  
      
    @metric  
    def check_policies(request, response, retrieved_context):  
        """Check if response follows company policies."""  
        context_text = '\n'.join([c['content'] for c in retrieved_context])  
      
        return judges.guideline_adherence(  
            request=request,  
            guidelines=["Response must comply with return policy in context."],  
            guidelines_context={  
                "response": response,  
                "retrieved_context": context_text  
            }  
        )  
    

**MLflow 3.x (Option 1: Using predefined Guidelines scorer):**

Python
    
    
    from mlflow.genai.scorers import Guidelines  
      
    # For simple guidelines that only need request/response  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[  
            Guidelines(  
                name="tone",  
                guidelines="The response must be professional and courteous."  
            )  
        ]  
    )  
    

**MLflow 3.x (Option 2: Custom scorer with meets_guidelines):**

Python
    
    
    from mlflow.genai.scorers import scorer  
    from mlflow.genai import judges  
      
    @scorer  
    def check_policies(inputs, outputs, traces):  
        """Check if response follows company policies."""  
        # Extract retrieved context from trace  
        retrieved_context = traces.data.spans[0].attributes.get("retrieved_context", [])  
        context_text = '\n'.join([c['content'] for c in retrieved_context])  
      
        return judges.meets_guidelines(  
            name="policy_compliance",  
            guidelines="Response must comply with return policy in context.",  
            context={  
                "request": inputs,  
                "response": outputs,  
                "retrieved_context": context_text  
            }  
        )  
    

####  Example: Migrating ExpectationsGuidelinesâ

When you want to set guidelines for each example in your evaluation set, such as requiring that certain topics are covered, or that the response follows a specific style, use the `ExpectationsGuidelines` scorer in MLflow 3.x.

**MLflow 2.x:**

In MLflow 2.x, you would implement guidelines as follows:

Python
    
    
    import pandas as pd  
      
    eval_data = {  
        "request": "What is MLflow?",  
        "response": "MLflow is an open-source platform for managing ML lifecycle.",  
        "guidelines": [  
            ["The response must mention these topics: platform, observability, testing"]  
        ],  
    }  
      
    eval_df = pd.DataFrame(eval_data)  
      
    mlflow.evaluate(  
        data=eval_df,  
        model_type="databricks-agent",  
        evaluator_config={  
            "databricks-agent": {"metrics": ["guideline_adherence"]}  
        }  
    )  
    

**MLflow 3.x:**

In MLflow 3.x, you organize evaluation data differently. Each entry in your evaluation data should have an `expectations` key, and inside that, you can include fields like `guidelines`.

Here's what your evaluation data might look like:

Python
    
    
    eval_data = [  
        {  
            "inputs": {"input": "What is MLflow?"},  
            "outputs": {"response": "MLflow is an open-source platform for managing ML lifecycle."},  
            "expectations": {  
                "guidelines": [  
                    "The response should mention the topics: platform, observability, and testing."  
                ]  
            }  
        }  
    ]  
    

Then, use the `ExpectationsGuidelines` scorer:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import ExpectationsGuidelines  
      
    expectations_guideline = ExpectationsGuidelines()  
      
    # Use predefined scorer  
    results = mlflow.genai.evaluate(  
        data=eval_data,  # Make sure each row has expectations.guidelines  
        predict_fn=my_app,  
        scorers=[  
            expectations_guideline  
        ]  
    )  
    

tip

If you need to check for specific factual content (e.g., "MLflow is open-source"), use the Correctness scorer with an `expected_facts` field instead of guidelines. See [Correctness judge](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_correct>).

### Replicating MLflow 2.x automatic judge behaviorâ

To replicate MLflow 2.x behavior of running all applicable judges, explicitly include all scorers:

**MLflow 2.x (automatic):**

Python
    
    
    # Automatically runs all applicable judges based on data  
    results = mlflow.evaluate(  
        data=eval_data,  # Contains expected_response and retrieved_context  
        model=my_agent,  
        model_type="databricks-agent"  
    )  
    

**MLflow 3.x (explicit):**

Python
    
    
    from mlflow.genai.scorers import (  
        Correctness, RetrievalSufficiency,  # Require ground truth  
        RelevanceToQuery, Safety, RetrievalGroundedness, RetrievalRelevance  # No ground truth  
    )  
      
    # Manually specify all judges you want to run  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_agent,  
        scorers=[  
            # With ground truth judges  
            Correctness(),  
            RetrievalSufficiency(),  
            # Without ground truth judges  
            RelevanceToQuery(),  
            Safety(),  
            RetrievalGroundedness(),  
            RetrievalRelevance(),  
        ]  
    )  
    

### Direct judge usageâ

You can still call judges directly for testing:

Python
    
    
    from mlflow.genai import judges  
      
    # Test a judge directly (same in both versions)  
    result = judges.correctness(  
        request="What is MLflow?",  
        response="MLflow is an open-source platform for ML lifecycle.",  
        expected_response="MLflow is an open-source platform for managing the ML lifecycle."  
    )  
    print(f"Judge result: {result.value}")  
    print(f"Rationale: {result.rationale}")  
    

##  Human feedback migrationâ

###  Labeling sessions and schemasâ

The Review App functionality has moved from `databricks.agents` to `mlflow.genai.labeling`.

**Namespace changes:**

MLflow 2.x| MLflow 3.x| `databricks.agents.review_app`| `mlflow.genai.labeling`| `databricks.agents.datasets`| `mlflow.genai.datasets`| `review_app.label_schemas.*`| `mlflow.genai.label_schemas.*`| `app.create_labeling_session()`| `labeling.create_labeling_session()`  
---|---  
  
#### Example: Creating a labeling sessionâ

**MLflow 2.x:**

Python
    
    
    from databricks.agents import review_app  
    import mlflow  
      
    # Get review app  
      
    my_app = review_app.get_review_app()  
      
    # Create custom label schema  
    quality_schema = my_app.create_label_schema(  
        name="response_quality",  
        type="feedback",  
        title="Rate the response quality",  
        input=review_app.label_schemas.InputCategorical(  
            options=["Poor", "Fair", "Good", "Excellent"]  
        )  
    )  
      
    # Create labeling session  
    session = my_app.create_labeling_session(  
        name="quality_review_jan_2024",  
        agent="my_agent",  
        assigned_users=["user1@company.com", "user2@company.com"],  
        label_schemas=[  
            review_app.label_schemas.EXPECTED_FACTS,  
            "response_quality"  
        ]  
    )  
      
    # Add traces for labeling  
    traces = mlflow.search_traces(run_id=run_id)  
    session.add_traces(traces)  
    

**MLflow 3.x:**

Python
    
    
    import mlflow  
    import mlflow.genai.labeling as labeling  
    import mlflow.genai.label_schemas as schemas  
      
    # Create custom label schema  
    quality_schema = schemas.create_label_schema(  
        name="response_quality",  
        type=schemas.LabelSchemaType.FEEDBACK,  
        title="Rate the response quality",  
        input=schemas.InputCategorical(  
            options=["Poor", "Fair", "Good", "Excellent"]  
        ),  
        overwrite=True  
    )  
      
    # Previously built in schemas must be created before use  
    # However, constant for their names are provided to ensure your schemas work with built-in scorers  
    expected_facts_schema = schemas.create_label_schema(  
        name=schemas.EXPECTED_FACTS,  
        type=schemas.LabelSchemaType.EXPECTATION,  
        title="Expected facts",  
        input=schemas.InputTextList(max_length_each=1000),  
        instruction="Please provide a list of facts that you expect to see in a correct response.",  
        overwrite=True  
    )  
      
    # Create labeling session  
    session = labeling.create_labeling_session(  
        name="quality_review_jan_2024",  
        assigned_users=["user1@company.com", "user2@company.com"],  
        label_schemas=[  
            schemas.EXPECTED_FACTS,  
            "response_quality"  
        ]  
    )  
      
    # Add traces for labeling  
    traces = mlflow.search_traces(  
        run_id=session.mlflow_run_id  
    )  
    session.add_traces(traces)  
      
    # Get review app URL  
    app = labeling.get_review_app()  
    print(f"Review app URL: {app.url}")  
    

###  Syncing feedback to datasetsâ

**MLflow 2.x:**

Python
    
    
    # Sync expectations back to dataset  
    session.sync(to_dataset="catalog.schema.eval_dataset")  
      
    # Use dataset for evaluation  
    dataset = spark.read.table("catalog.schema.eval_dataset")  
    results = mlflow.evaluate(  
        data=dataset,  
        model=my_agent,  
        model_type="databricks-agent"  
    )  
    

**MLflow 3.x:**

Python
    
    
    from mlflow.genai import datasets  
    import mlflow  
      
    # Sample agent function  
    @mlflow.trace  
    def my_agent(request: str):  
        """Simple mock agent for testing - MLflow 3 expects dict input"""  
        responses = {  
            "What is MLflow?": "MLflow is an open-source platform for managing ML lifecycle.",  
            "What is Databricks?": "Databricks is a unified analytics platform.",  
        }  
        return {"response": responses.get(request, "I don't have information about that.")}  
      
      
    # Sync expectations back to dataset  
    session.sync(to_dataset="catalog.schema.eval_dataset")  
      
    # Use dataset for evaluation  
    dataset = datasets.get_dataset("catalog.schema.eval_dataset")  
    results = mlflow.genai.evaluate(  
        data=dataset,  
        predict_fn=my_agent  
    )  
    

## Additional resourcesâ

  * [MLflow 3 GenAI Evaluation Guide](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>)
  * [Custom Scorers Documentation](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>)
  * [Human Feedback with labeling sessions](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-sessions>)
  * [Predefined Judge Scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>)
  * [MLflow Tracing Guide](</aws/en/mlflow3/genai/tracing/>)



For additional support during migration, consult the MLflow documentation or reach out to your Databricks support team.
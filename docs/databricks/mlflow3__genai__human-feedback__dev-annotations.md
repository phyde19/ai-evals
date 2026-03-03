<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/human-feedback/dev-annotations -->

On this page

Last updated on **Dec 16, 2025**

# Label during development

As a developer building GenAI applications, you need a way to track your observations about the quality of your application's outputs. [MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) allows you to add feedback or expectations directly to traces during development, giving you a quick way to record quality issues, mark successful examples, or add notes for future reference.

## Prerequisitesâ

  * Your application is instrumented with [MLflow Tracing](</aws/en/mlflow3/genai/tracing/>)
  * You have generated traces by running your application



## Add assessment labelsâ

Assessments attach structured feedback, scores, or ground truth to traces and spans for quality evaluation and improvement in MLflow.

  * Databricks UI
  * MLflow SDK
  * Databricks REST API



MLflow makes it easy to add annotations (labels) directly to traces through the MLflow UI.

note

If you are using a Databricks notebook, you can also perform these steps from the Trace UI that renders inline in the notebook.

  1. Navigate to the Traces tab in the MLflow Experiment UI
  2. Open an individual trace
  3. Within the trace UI, click on the specific span you want to label
     * Selecting the root span attaches feedback to the entire trace
  4. Expand the Assessments tab at the far right
  5. Fill in the form to add your feedback
     * **Assessment Type**
       * _Feedback_ : Subjective assessment of quality (ratings, comments)
       * _Expectation_ : The expected output or value (what should have been produced)
     * **Assessment Name**
       * A unique name for what the feedback is about
     * **Data Type**
       * Number
       * Boolean
       * String
     * **Value**
       * Your assessment
     * **Rationale**
       * Optional notes about the value
  6. Click **Create** to save your label
  7. When you return to the Traces tab, your label will appear as a new column



You can programmatically add labels to traces using MLflow's SDK. This is useful for automated labeling based on your application logic or for batch processing of traces.

MLflow provides two APIs:

  * [`mlflow.log_feedback()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=log_feedback#mlflow.log_feedback>) \- Logs feedback that evaluates your app's actual outputs or intermediate steps (for example, "Was the response good?", ratings, comments).
  * [`mlflow.log_expectation()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html?highlight=log_expectation#mlflow.log_expectation>) \- Logs expectations that define the desired or correct outcome (ground truth) your app should have produced.



Python
    
    
    import mlflow  
    from mlflow.entities.assessment import (  
        AssessmentSource,  
        AssessmentSourceType,  
        AssessmentError,  
    )  
      
      
    @mlflow.trace  
    def my_app(input: str) -> str:  
        return input + "_output"  
      
      
    # Create a sample trace to demonstrate assessment logging  
    my_app(input="hello")  
      
    trace_id = mlflow.get_last_active_trace_id()  
      
    # Handle case where trace_id might be None  
    if trace_id is None:  
        raise ValueError("No active trace found. Make sure to run a traced function first.")  
      
    print(f"Using trace_id: {trace_id}")  
      
      
    # =============================================================================  
    # LOG_FEEDBACK - Evaluating actual outputs and performance  
    # =============================================================================  
      
    # Example 1: Human rating (integer scale)  
    # Use case: Domain experts rating response quality on a 1-5 scale  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="human_rating",  
        value=4,  # int - rating scale feedback  
        rationale="Human evaluator rating",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.HUMAN,  
            source_id="evaluator@company.com",  
        ),  
    )  
      
    # Example 2: LLM judge score (float for precise scoring)  
    # Use case: Automated quality assessment using LLM-as-a-judge  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="llm_judge_score",  
        value=0.85,  # float - precise scoring from 0.0 to 1.0  
        rationale="LLM judge evaluation",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.LLM_JUDGE,  
            source_id="gpt-4o-mini",  
        ),  
        metadata={"temperature": "0.1", "model_version": "2024-01"},  
    )  
      
    # Example 3: Binary feedback (boolean for yes/no assessments)  
    # Use case: Simple thumbs up/down or correct/incorrect evaluations  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="is_helpful",  
        value=True,  # bool - binary assessment  
        rationale="Boolean assessment of helpfulness",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.HUMAN,  
            source_id="reviewer@company.com",  
        ),  
    )  
      
    # Example 4: Multi-category feedback (list for multiple classifications)  
    # Use case: Automated categorization or multi-label classification  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="automated_categories",  
        value=["helpful", "accurate", "concise"],  # list - multiple categories  
        rationale="Automated categorization",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.CODE,  
            source_id="classifier_v1.2",  
        ),  
    )  
      
    # Example 5: Complex analysis with metadata (when you need structured context)  
    # Use case: Detailed automated analysis with multiple dimensions stored in metadata  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="response_analysis_score",  
        value=4.2,  # single score instead of dict - keeps value simple  
        rationale="Analysis: 150 words, positive sentiment, includes examples, confidence 0.92",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.CODE,  
            source_id="analyzer_v2.1",  
        ),  
        metadata={  # Use metadata for structured details  
            "word_count": "150",  
            "sentiment": "positive",  
            "has_examples": "true",  
            "confidence": "0.92",  
        },  
    )  
      
    # Example 6: Error handling when evaluation fails  
    # Use case: Logging when automated evaluators fail due to API limits, timeouts, etc.  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="failed_evaluation",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.LLM_JUDGE,  
            source_id="gpt-4o",  
        ),  
        error=AssessmentError(  # Use error field when evaluation fails  
            error_code="RATE_LIMIT_EXCEEDED",  
            error_message="API rate limit exceeded during evaluation",  
        ),  
        metadata={"retry_count": "3", "error_timestamp": "2024-01-15T10:30:00Z"},  
    )  
      
    # =============================================================================  
    # LOG_EXPECTATION - Defining ground truth and desired outcomes  
    # =============================================================================  
      
    # Example 1: Simple text expectation (most common pattern)  
    # Use case: Defining the ideal response for factual questions  
    mlflow.log_expectation(  
        trace_id=trace_id,  
        name="expected_response",  
        value="The capital of France is Paris.",  # Simple string - the "correct" answer  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.HUMAN,  
            source_id="content_curator@example.com",  
        ),  
    )  
      
    # Example 2: Complex structured expectation (advanced pattern)  
    # Use case: Defining detailed requirements for response structure and content  
    mlflow.log_expectation(  
        trace_id=trace_id,  
        name="expected_response_structure",  
        value={  # Complex dict - detailed specification of ideal response  
            "entities": {  
                "people": ["Marie Curie", "Pierre Curie"],  
                "locations": ["Paris", "France"],  
                "dates": ["1867", "1934"],  
            },  
            "key_facts": [  
                "First woman to win Nobel Prize",  
                "Won Nobel Prizes in Physics and Chemistry",  
                "Discovered radium and polonium",  
            ],  
            "response_requirements": {  
                "tone": "informative",  
                "length_range": {"min": 100, "max": 300},  
                "include_examples": True,  
                "citations_required": False,  
            },  
        },  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.HUMAN,  
            source_id="content_strategist@example.com",  
        ),  
        metadata={  
            "content_type": "biographical_summary",  
            "target_audience": "general_public",  
            "fact_check_date": "2024-01-15",  
        },  
    )  
      
    # Example 3: Multiple acceptable answers (list pattern)  
    # Use case: When there are several valid ways to express the same fact  
    mlflow.log_expectation(  
        trace_id=trace_id,  
        name="expected_facts",  
        value=[  # List of acceptable variations of the correct answer  
            "Paris is the capital of France",  
            "The capital city of France is Paris",  
            "France's capital is Paris",  
        ],  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.HUMAN,  
            source_id="qa_team@example.com",  
        ),  
    )  
    

Create assessments using the Databricks REST API to programmatically log feedback and assessments on traces from any environment.

See [Databricks REST API documentation](<https://docs.databricks.com/api/workspace/mlflowexperimenttrace/createassessmentv3>).

**REST API endpoint**
    
    
     POST https://<workspace-host>.databricks.com/api/3.0/mlflow/traces/{trace_id}/assessments  
    

**Example request:**

Bash
    
    
    curl -X POST \  
      "https://<workspace-host>.databricks.com/api/3.0/mlflow/traces/<trace-id>/assessments" \  
      -H "Authorization: Bearer <databricks-token>" \  
      -H "Content-Type: application/json" \  
      -d '{  
        "assessment": {  
          "assessment_name": "string",  
          "create_time": "2019-08-24T14:15:22Z",  
          "expectation": {  
            "serialized_value": {  
              "serialization_format": "string",  
              "value": "string"  
            },  
            "value": {}  
          },  
          "feedback": {  
            "error": {  
              "error_code": "string",  
              "error_message": "string",  
              "stack_trace": "string"  
            },  
            "value": {}  
          },  
          "last_update_time": "2019-08-24T14:15:22Z",  
          "metadata": {  
            "property1": "string",  
            "property2": "string"  
          },  
          "overrides": "string",  
          "rationale": "string",  
          "source": {  
            "source_id": "string",  
            "source_type": "HUMAN"  
          },  
          "span_id": "string",  
          "valid": true  
        }  
      }'  
    

**Example response:**

JSON
    
    
    {  
      "assessment": {  
        "assessment_id": "string",  
        "assessment_name": "string",  
        "create_time": "2019-08-24T14:15:22Z",  
        "expectation": {  
          "serialized_value": {  
            "serialization_format": "string",  
            "value": "string"  
          },  
          "value": {}  
        },  
        "feedback": {  
          "error": {  
            "error_code": "string",  
            "error_message": "string",  
            "stack_trace": "string"  
          },  
          "value": {}  
        },  
        "last_update_time": "2019-08-24T14:15:22Z",  
        "metadata": {  
          "property1": "string",  
          "property2": "string"  
        },  
        "overrides": "string",  
        "rationale": "string",  
        "source": {  
          "source_id": "string",  
          "source_type": "HUMAN"  
        },  
        "span_id": "string",  
        "trace_id": "string",  
        "valid": true  
      }  
    }  
    

## Next stepsâ

Continue your journey with these recommended actions and tutorials.

  * [Collect domain expert feedback](</aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces>) \- Set up structured labeling sessions
  * [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) \- Use your labeled traces to create test datasets
  * [Collect end-user feedback](</aws/en/mlflow3/genai/tracing/collect-user-feedback/>) \- Capture feedback from deployed applications



## Reference guidesâ

Explore detailed documentation for concepts and features mentioned in this guide.

  * [Labeling schemas](</aws/en/mlflow3/genai/human-feedback/concepts/labeling-schemas>) \- Learn about structured feedback collection
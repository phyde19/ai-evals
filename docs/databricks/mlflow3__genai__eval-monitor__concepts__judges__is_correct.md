<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_correct -->

On this page

Last updated on **Feb 17, 2026**

# Correctness judge

The `Correctness` judge assesses whether your GenAI application's response is factually correct by comparing it against provided ground truth information (`expected_facts` or `expected_response`). This built-in LLM judge is designed for evaluating application responses against known correct answers.

For API details, see the [MLflow documentation](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Correctness>).

For detailed documentation and additional examples, see the [MLflow Correctness judge documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/response-quality/correctness/>).

## Prerequisites for running the examplesâ

  1. Install MLflow and required packages.

Python
         
         %pip install --upgrade "mlflow[databricks]>=3.4.0"  
         dbutils.library.restartPython()  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




## Usage examplesâ

  * Invoke directly
  * Invoke with evaluate()



Python
    
    
    from mlflow.genai.scorers import Correctness  
      
    correctness_judge = Correctness()  
      
    # Example 1: Response contains expected facts  
    feedback = correctness_judge(  
        inputs={"request": "What is MLflow?"},  
        outputs={"response": "MLflow is an open-source platform for managing the ML lifecycle."},  
        expectations={  
            "expected_facts": [  
                "MLflow is open-source",  
                "MLflow is a platform for ML lifecycle"  
            ]  
        }  
    )  
      
    print(feedback.value)  # "yes"  
    print(feedback.rationale)  # Explanation of which facts are supported  
      
    # Example 2: Response missing or contradicting facts  
    feedback = correctness_judge(  
        inputs={"request": "When was MLflow released?"},  
        outputs={"response": "MLflow was released in 2017."},  
        expectations={"expected_facts": ["MLflow was released in June 2018"]}  
    )  
      
    # Example 3: Using expected_response instead of expected_facts  
    feedback = correctness_judge(  
        inputs={"request": "What is the capital of France?"},  
        outputs={"response": "The capital of France is Paris."},  
        expectations={"expected_response": "Paris is the capital of France."}  
    )  
    

The `Correctness` judge can be used directly with MLflow's evaluation framework.

**Requirements:**

  * **Trace requirements** : `inputs` and `outputs` must be on the Trace's root span
  * **Ground-truth labels** : Required - must provide either `expected_facts` or `expected_response` in the `expectations` dictionary



Python
    
    
    from mlflow.genai.scorers import Correctness  
      
    # Create evaluation dataset with ground truth  
    eval_dataset = [  
        {  
            "inputs": {"query": "What is the capital of France?"},  
            "outputs": {  
                "response": "Paris is the magnificent capital city of France, known for the Eiffel Tower and rich culture."  
            },  
            "expectations": {  
                "expected_facts": ["Paris is the capital of France."]  
            },  
        },  
        {  
            "inputs": {"query": "What are the main components of MLflow?"},  
            "outputs": {  
                "response": "MLflow has four main components: Tracking, Projects, Models, and Registry."  
            },  
            "expectations": {  
                "expected_facts": [  
                    "MLflow has four main components",  
                    "Components include Tracking",  
                    "Components include Projects",  
                    "Components include Models",  
                    "Components include Registry"  
                ]  
            },  
        },  
        {  
            "inputs": {"query": "When was MLflow released?"},  
            "outputs": {  
                "response": "MLflow was released in 2017 by Databricks."  
            },  
            "expectations": {  
                "expected_facts": ["MLflow was released in June 2018"]  
            },  
        }  
    ]  
      
    # Run evaluation with Correctness scorer  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        scorers=[  
            Correctness(  
                model="databricks:/databricks-gpt-oss-120b",  # Optional. Defaults to custom Databricks model.  
            )  
        ]  
    )  
    

### Alternative: Using expected_responseâ

You can also use `expected_response` instead of `expected_facts`:

Python
    
    
    eval_dataset_with_response = [  
        {  
            "inputs": {"query": "What is MLflow?"},  
            "outputs": {  
                "response": "MLflow is an open-source platform for managing the ML lifecycle."  
            },  
            "expectations": {  
                "expected_response": "MLflow is an open-source platform for managing the machine learning lifecycle, including experimentation, reproducibility, and deployment."  
            },  
        }  
    ]  
      
    # Run evaluation with expected_response  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset_with_response,  
        scorers=[Correctness()]  
    )  
    

tip

Use `expected_facts` rather than `expected_response` for more flexible evaluation - the response doesn't need to match word-for-word, just contain the key facts.

## Select the LLM that powers the judgeâ

By default, these judges use a Databricks-hosted LLM designed to perform GenAI quality assessments. You can change the judge model by using the `model` argument in the judge definition. The model must be specified in the format `<provider>:/<model-name>`, where `<provider>` is a LiteLLM-compatible model provider. If you use `databricks` as the model provider, the model name is the same as the serving endpoint name.

You can customize the judge by providing a different judge model:

Python
    
    
    from mlflow.genai.scorers import Correctness  
      
    # Use a different judge model  
    correctness_judge = Correctness(  
        model="databricks:/databricks-gpt-5-mini"  # Or any LiteLLM-compatible model  
    )  
      
    # Use in evaluation  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        scorers=[correctness_judge]  
    )  
    

## Interpret resultsâ

The judge returns a `Feedback` object with:

  * **`value`** : "yes" if response is correct, "no" if incorrect
  * **`rationale`** : Detailed explanation of which facts are supported or missing



## Next stepsâ

  * [Explore other built-in judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) \- Learn about other built-in quality evaluation judges
  * [Create custom judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>) \- Build domain-specific evaluation judges
  * [Run evaluations](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) \- Use judges in comprehensive application evaluation
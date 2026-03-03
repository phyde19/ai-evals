<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_safe -->

On this page

Last updated on **Feb 17, 2026**

# Safety judge

The `Safety` judge evaluates text content to identify potentially harmful, offensive, or inappropriate material. It returns a pass/fail assessment along with a detailed rationale explaining any safety concerns.

For API details, see the [MLflow documentation](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Safety>).

For detailed documentation and additional examples, see the [MLflow Safety judge documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/response-quality/safety/>).

## Prerequisites for running the examplesâ

  1. Install MLflow and required packages.

Python
         
         %pip install --upgrade "mlflow[databricks]>=3.4.0"  
         dbutils.library.restartPython()  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




## Usage examplesâ

The `Safety` judge can be invoked directly for single assessment or used with MLflow's evaluation framework for batch evaluation.

  * Invoke directly
  * Invoke with evaluate()



Python
    
    
    from mlflow.genai.scorers import Safety  
      
    # Assess the safety of a single output  
    assessment = Safety(  
        outputs="MLflow is an open-source platform for managing the ML lifecycle, including experimentation, reproducibility, and deployment."  
    )  
    print(assessment)  
    

Python
    
    
    from mlflow.genai.scorers import Safety  
      
    # Create evaluation dataset with various safety scenarios  
    eval_dataset = [  
        {  
            "inputs": {"query": "Tell me about MLflow"},  
            "outputs": {  
                "response": "MLflow is an open-source platform for managing the ML lifecycle, including experimentation, reproducibility, and deployment."  
            },  
        },  
        {  
            "inputs": {"query": "How can I stay productive?"},  
            "outputs": {  
                "response": "To stay productive, try these tips: Take regular breaks, prioritize tasks, stay hydrated, get enough sleep, and maintain a healthy work-life balance."  
            },  
        },  
        {  
            "inputs": {"query": "What's your opinion on sensitive topics?"},  
            "outputs": {  
                "response": "I aim to provide helpful, factual information while avoiding potentially harmful or biased content."  
            },  
        }  
    ]  
      
    # Run evaluation with Safety scorer  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        scorers=[  
            Safety(  
                model="databricks:/databricks-gpt-oss-120b",  # Optional. Defaults to custom Databricks model.  
            ),  
        ]  
    )  
    

## Select the LLM that powers the judgeâ

By default, this judge uses a Databricks-hosted LLM designed to perform GenAI quality assessments. You can change the judge model by using the `model` argument in the judge definition. The model must be specified in the format `<provider>:/<model-name>`, where `<provider>` is a LiteLLM-compatible model provider. If you use `databricks` as the model provider, the model name is the same as the serving endpoint name.

You can customize the Safety judge by specifying a different model:

Python
    
    
    from mlflow.genai.scorers import Safety  
      
    # Use a different model for safety evaluation  
    safety_judge = Safety(  
        model="databricks:/databricks-claude-opus-4-1"  # Use a different model  
    )  
      
    # Run evaluation with Safety judge  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        scorers=[safety_judge]  
    )  
    

## Next stepsâ

  * [Explore other built-in judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) \- Learn about relevance, groundedness, and correctness judges
  * [Monitor safety in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) \- Set up continuous safety monitoring for deployed applications
  * [Create custom safety guidelines with Guidelines judge](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/guidelines>) \- Define specific safety criteria for your use case
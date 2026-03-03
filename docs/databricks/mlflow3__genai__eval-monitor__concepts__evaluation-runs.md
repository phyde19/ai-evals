<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/evaluation-runs -->

On this page

Last updated on **Sep 24, 2025**

# Evaluation runs

Evaluation runs are MLflow runs that organize and store the results of evaluating your GenAI app. An evaluation run includes the following:

  * **Traces** : One trace for each input in your evaluation dataset.
  * **Feedback** : Quality assessments from scorers attached to each trace.
  * **Metrics** : Aggregate statistics across all evaluated examples.
  * **Metadata** : Information about the evaluation configuration.



## How to create evaluation runsâ

An evaluation run is automatically created when you call `mlflow.genai.evaluate()`. For more information about `mlflow.genai.evaluate()`, see [the MLflow source code](<https://mlflow.org/docs/latest/api_reference/_modules/mlflow/genai/evaluation/base.html#evaluate>) and [documentation](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>).

Python
    
    
    import mlflow  
      
    # This creates an evaluation run  
    results = mlflow.genai.evaluate(  
        data=test_dataset,  
        predict_fn=my_app,  
        scorers=[correctness_scorer, safety_scorer],  
        experiment_name="my_app_evaluations"  
    )  
      
    # Access the run ID  
    print(f"Evaluation run ID: {results.run_id}")  
    

## Evaluation run structureâ
    
    
    Evaluation Run  
    âââ Run Info  
    â   âââ run_id: unique identifier  
    â   âââ experiment_id: which experiment it belongs to  
    â   âââ start_time: when evaluation began  
    â   âââ status: success/failed  
    âââ Traces (one per dataset row)  
    â   âââ Trace 1  
    â   â   âââ inputs: {"question": "What is MLflow?"}  
    â   â   âââ outputs: {"response": "MLflow is..."}  
    â   â   âââ feedbacks: [correctness: 0.8, relevance: 1.0]  
    â   âââ Trace 2  
    â   âââ ...  
    âââ Aggregate Metrics  
    â   âââ correctness_mean: 0.85  
    â   âââ relevance_mean: 0.92  
    â   âââ safety_pass_rate: 1.0  
    âââ Parameters  
        âââ model_version: "v2.1"  
        âââ dataset_name: "qa_test_v1"  
        âââ scorers: ["correctness", "relevance", "safety"]
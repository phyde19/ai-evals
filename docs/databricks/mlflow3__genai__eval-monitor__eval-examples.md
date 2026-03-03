<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/eval-examples -->

On this page

Last updated on **Oct 28, 2025**

# MLflow evaluation examples for GenAI

This page presents some common usage patterns for the evaluation harness, including data patterns and `predict_fn` patterns.

## Common data input patternsâ

### Evaluate using an MLflow Evaluation Dataset (recommended)â

MLflow Evaluation Datasets provide versioning, lineage tracking, and integration with Unity Catalog for production-ready evaluation. They are useful when you need version control and lineage tracking for your evaluation data, and when you need to convert traces to evaluation records.

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import Correctness, Safety  
    from my_app import agent  # Your GenAI app with tracing  
      
    # Load versioned evaluation dataset  
    dataset = mlflow.genai.datasets.get_dataset("catalog.schema.eval_dataset_name")  
      
    # Run evaluation  
    results = mlflow.genai.evaluate(  
        data=dataset,  
        predict_fn=agent,  
        scorers=[Correctness(), Safety()],  
    )  
    

To create datasets from traces or scratch, see [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>).

### Evaluate using a list of dictionariesâ

Use a simple list of dictionaries for quick prototyping without creating a formal evaluation dataset. This is useful for quick prototyping, small datasets (fewer than 100 examples), and informal development testing.

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import Correctness, RelevanceToQuery  
    from my_app import agent  # Your GenAI app with tracing  
      
    # Define test data as a list of dictionaries  
    eval_data = [  
        {  
            "inputs": {"question": "What is MLflow?"},  
            "expectations": {"expected_facts": ["open-source platform", "ML lifecycle management"]}  
        },  
        {  
            "inputs": {"question": "How do I track experiments?"},  
            "expectations": {"expected_facts": ["mlflow.start_run()", "log metrics", "log parameters"]}  
        },  
        {  
            "inputs": {"question": "What are MLflow's main components?"},  
            "expectations": {"expected_facts": ["Tracking", "Projects", "Models", "Registry"]}  
        }  
    ]  
      
    # Run evaluation  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=agent,  
        scorers=[Correctness(), RelevanceToQuery()],  
    )  
    

For production, convert to an [MLflow Evaluation Dataset](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>).

### Evaluate using a Pandas DataFrameâ

Use Pandas DataFrames for evaluation when working with CSV files or existing data science workflows. This is useful for quick prototyping, small datasets (fewer than 100 examples), and informal development testing.

Python
    
    
    import mlflow  
    import pandas as pd  
    from mlflow.genai.scorers import Correctness, Safety  
    from my_app import agent  # Your GenAI app with tracing  
      
    # Create evaluation data as a Pandas DataFrame  
    eval_df = pd.DataFrame([  
        {  
            "inputs": {"question": "What is MLflow?"},  
            "expectations": {"expected_response": "MLflow is an open-source platform for ML lifecycle management"}  
        },  
        {  
            "inputs": {"question": "How do I log metrics?"},  
            "expectations": {"expected_response": "Use mlflow.log_metric() to log metrics"}  
        }  
    ])  
      
    # Run evaluation  
    results = mlflow.genai.evaluate(  
        data=eval_df,  
        predict_fn=agent,  
        scorers=[Correctness(), Safety()],  
    )  
    

### Evaluate using a Spark DataFrameâ

Use Spark DataFrames for large-scale evaluations or when data is already in Delta Lake or Unity Catalog. This is useful when the data already exists in Delta Lake or Unity Catalog, or if you need to filter the records in an MLflow Evaluation Dataset before running the evaluation.

The DataFrame must comply with the [evaluation dataset schema](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-datasets>).

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import Safety, RelevanceToQuery  
    from my_app import agent  # Your GenAI app with tracing  
      
    # Load evaluation data from a Delta table in Unity Catalog  
    eval_df = spark.table("catalog.schema.evaluation_data")  
      
    # Or load from any Spark-compatible source  
    # eval_df = spark.read.parquet("path/to/evaluation/data")  
      
    # Run evaluation  
    results = mlflow.genai.evaluate(  
        data=eval_df,  
        predict_fn=agent,  
        scorers=[Safety(), RelevanceToQuery()],  
    )  
    

## Common `predict_fn` patternsâ

### Call your app directlyâ

Pass your app directly as `predict_fn` when parameter names match your evaluation dataset keys. This is useful for apps that have parameter names that match the `inputs` in your evaluation dataset.

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery, Safety  
      
    # Your GenAI app that accepts 'question' as a parameter  
    @mlflow.trace  
    def my_chatbot_app(question: str) -> dict:  
        # Your app logic here  
        response = f"I can help you with: {question}"  
        return {"response": response}  
      
    # Evaluation data with 'question' key matching the function parameter  
    eval_data = [  
        {"inputs": {"question": "What is MLflow?"}},  
        {"inputs": {"question": "How do I track experiments?"}}  
    ]  
      
    # Pass your app directly since parameter names match  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=my_chatbot_app,  # Direct reference, no wrapper needed  
        scorers=[RelevanceToQuery(), Safety()]  
    )  
    

### Wrap your app in a callableâ

If your app expects different parameter names or data structures than your evaluation dataset's `inputs`, wrap it in a callable function. This is useful when there are parameter name mismatches between your app's parameters and evaluation dataset `input` keys (for example, `user_input` vs `question`), or when data format conversions are required (for example, string to list or JSON parsing).

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery, Safety  
      
    # Your existing GenAI app with different parameter names  
    @mlflow.trace  
    def customer_support_bot(user_message: str, chat_history: list = None) -> dict:  
        # Your app logic here  
        context = f"History: {chat_history}" if chat_history else "New conversation"  
        return {  
            "bot_response": f"Helping with: {user_message}. {context}",  
            "confidence": 0.95  
        }  
      
    # Wrapper function to translate evaluation data to your app's interface  
    def evaluate_support_bot(question: str, history: str = None) -> dict:  
        # Convert evaluation dataset format to your app's expected format  
        chat_history = history.split("|") if history else []  
      
        # Call your app with the translated parameters  
        result = customer_support_bot(  
            user_message=question,  
            chat_history=chat_history  
        )  
      
        # Translate output to standard format if needed  
        return {  
            "response": result["bot_response"],  
            "confidence_score": result["confidence"]  
        }  
      
    # Evaluation data with different key names  
    eval_data = [  
        {"inputs": {"question": "Reset password", "history": "logged in|forgot email"}},  
        {"inputs": {"question": "Track my order"}}  
    ]  
      
    # Use the wrapper function for evaluation  
    results = mlflow.genai.evaluate(  
        data=eval_data,  
        predict_fn=evaluate_support_bot,  # Wrapper handles translation  
        scorers=[RelevanceToQuery(), Safety()]  
    )  
    

### Evaluate a deployed endpointâ

Use the `to_predict_fn` function to evaluate Agent Framework, Model Serving chat endpoints, and custom endpoints.

This function creates a predict function that's compatible with those endpoints and automatically extracts traces from tracing-enabled endpoints for full observability.

note

The `to_predict_fn` function performs a `kwargs` pass-through directly to your endpoint. Your evaluation data must match the input format that your endpoint expects. If the formats don't match, the evaluation fails with an error message about unrecognized input keys.

  * Model Serving chat
  * Agent Framework
  * Custom endpoint



Model Serving chat endpoints require data that is formatted with the `messages` key.

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery  
      
    # Create predict function for a chat endpoint  
    predict_fn = mlflow.genai.to_predict_fn("endpoints:/my-chatbot-endpoint")  
      
    # Evaluate the chat endpoint  
    results = mlflow.genai.evaluate(  
        data=[{"inputs": {"messages": [{"role": "user", "content": "How does MLflow work?"}]}}],  
        predict_fn=predict_fn,  
        scorers=[RelevanceToQuery()]  
    )  
    

Agent Framework endpoints can have different input interfaces. The following example shows an `input` key:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery  
      
    # Create a predict function for a Knowledge Assistant agent endpoint  
    predict_fn = mlflow.genai.to_predict_fn("endpoints:/ka-56a301ab-endpoint")  
      
    # Evaluate the agent endpoint  
    results = mlflow.genai.evaluate(  
        data=[{"inputs": {"input": [{"role": "user", "content": "How do I use the Models from Code feature in MLflow?"}]}}],  
        predict_fn=predict_fn,  
        scorers=[RelevanceToQuery()]  
    )  
    

Custom endpoints might have entirely different access patterns for submitting data to them. Ensure that the `data` input format is compatible with the endpoint being used for evaluation.

If your evaluation data format is incompatible with your endpoint, wrap the model's interface. A translation layer can ensure that the correct payload is submitted to the evaluation endpoint.

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery  
      
    def custom_predict_fn(inputs):  
        # Transform inputs to match your endpoint's expected format  
        # For example, if your endpoint expects a 'query' key instead of 'messages'  
        transformed_inputs = {  
            "query": inputs["messages"][0]["content"],  
            "context": inputs.get("context", "")  
        }  
      
        # Call your endpoint with the transformed data  
        original_predict_fn = mlflow.genai.to_predict_fn("endpoints:/my-custom-endpoint")  
        return original_predict_fn(transformed_inputs)  
      
    # Use your wrapper function for evaluation  
    results = mlflow.genai.evaluate(  
        data=[{"inputs": {"messages": [{"role": "user", "content": "What is machine learning?"}], "context": "technical documentation"}}],  
        predict_fn=custom_predict_fn,  
        scorers=[RelevanceToQuery()]  
    )  
    

### Evaluate a logged modelâ

Wrap logged MLflow models to translate between evaluation's named parameters and the model's single-parameter interface.

Most logged models (such as those using PyFunc or logging flavors like LangChain) accept a single input parameter (for example, `model_inputs` for PyFunc), while `predict_fn` expects named parameters that correspond to the keys in your evaluation dataset.

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
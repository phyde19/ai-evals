<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_context_relevant -->

On this page

Last updated on **Feb 17, 2026**

# Answer and context relevance judges

MLflow provides two built-in LLM judges to assess relevance in your GenAI applications. These judges help diagnose quality issues - if context isn't relevant, the generation step cannot produce a helpful response.

  * **`RelevanceToQuery`** : Evaluates if your app's response directly addresses the user's input.
  * **`RetrievalRelevance`** : Evaluates if each document returned by your app's retriever(s) is relevant.



For API details, see the MLflow documentation:

  * [`RelevanceToQuery`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RelevanceToQuery>)
  * [`RetrievalRelevance`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RetrievalRelevance>)



For detailed documentation and additional examples, see the [MLflow Relevance judges documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/rag/relevance/>).

## Prerequisites for running the examplesâ

  1. Install MLflow and required packages.

Python
         
         %pip install --upgrade "mlflow[databricks]>=3.4.0" openai "databricks-connect>=16.1"  
         dbutils.library.restartPython()  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




##  `RelevanceToQuery` judgeâ

This scorer evaluates if your app's response directly addresses the user's input without deviating into unrelated topics.

You can invoke the scorer directly with a single input for testing, or pass it to `mlflow.genai.evaluate` for running full evaluation on a dataset.

**Requirements:**

  * **Trace requirements** : `inputs` and `outputs` must be on the Trace's root span



  * Invoke directly
  * Invoke with evaluate()



Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery  
      
    assessment = RelevanceToQuery(name="my_relevance_to_query")(  
        inputs={"question": "What is the capital of France?"},  
        outputs="The capital of France is Paris.",  
    )  
    print(assessment)  
    

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RelevanceToQuery  
      
    data = [  
        {  
            "inputs": {"question": "What is the capital of France?"},  
            "outputs": "The capital of France is Paris.",  
        }  
    ]  
    result = mlflow.genai.evaluate(data=data, scorers=[RelevanceToQuery()])  
    

## `RetrievalRelevance` judgeâ

This scorer evaluates if each document returned by your app's retriever(s) is relevant to the input request.

**Requirements:**

  * **Trace requirements** : The MLflow Trace must contain at least one span with `span_type` set to `RETRIEVER`



  * Invoke directly
  * Invoke with evaluate()



Python
    
    
    from mlflow.genai.scorers import retrieval_relevance  
    import mlflow  
      
    # Get a trace from a previous run  
    trace = mlflow.get_trace("<your-trace-id>")  
      
    # Assess if each retrieved document is relevant  
    feedbacks = retrieval_relevance(trace=trace)  
    print(feedbacks)  
    

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RetrievalRelevance  
      
    # Evaluate traces from previous runs  
    results = mlflow.genai.evaluate(  
        data=traces,  # DataFrame or list containing trace data  
        scorers=[RetrievalRelevance()]  
    )  
    

### RAG exampleâ

Here's a complete example showing how to create a RAG application with a retriever and evaluate it:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RetrievalRelevance  
    from mlflow.entities import Document  
    from typing import List  
      
    # Define a retriever function with proper span type  
    @mlflow.trace(span_type="RETRIEVER")  
    def retrieve_docs(query: str) -> List[Document]:  
        # Simulated retrieval - in practice, this would query a vector database  
        if "capital" in query.lower() and "france" in query.lower():  
            return [  
                Document(  
                    id="doc_1",  
                    page_content="Paris is the capital of France.",  
                    metadata={"source": "geography.txt"}  
                ),  
                Document(  
                    id="doc_2",  
                    page_content="The Eiffel Tower is located in Paris.",  
                    metadata={"source": "landmarks.txt"}  
                )  
            ]  
        else:  
            return [  
                Document(  
                    id="doc_3",  
                    page_content="Python is a programming language.",  
                    metadata={"source": "tech.txt"}  
                )  
            ]  
      
    # Define your app that uses the retriever  
    @mlflow.trace  
    def rag_app(query: str):  
        docs = retrieve_docs(query)  
        # In practice, you would pass these docs to an LLM  
        return {"response": f"Found {len(docs)} relevant documents."}  
      
    # Create evaluation dataset  
    eval_dataset = [  
        {  
            "inputs": {"query": "What is the capital of France?"}  
        },  
        {  
            "inputs": {"query": "How do I use Python?"}  
        }  
    ]  
      
    # Run evaluation with RetrievalRelevance scorer  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        predict_fn=rag_app,  
        scorers=[  
            RetrievalRelevance(  
                model="databricks:/databricks-gpt-oss-120b",  # Optional. Defaults to custom Databricks model.  
            )  
        ]  
    )  
    

## Select the LLM that powers the judgeâ

By default, these judges use a Databricks-hosted LLM designed to perform GenAI quality assessments. You can change the judge model by using the `model` argument in the judge definition. The model must be specified in the format `<provider>:/<model-name>`, where `<provider>` is a LiteLLM-compatible model provider. If you use `databricks` as the model provider, the model name is the same as the serving endpoint name.

You can customize these judges by providing different judge models:

Python
    
    
    from mlflow.genai.scorers import RelevanceToQuery, RetrievalRelevance  
      
    # Use different judge models  
    relevance_judge = RelevanceToQuery(  
        model="databricks:/databricks-gpt-5-mini"  # Or any LiteLLM-compatible model  
    )  
      
    retrieval_judge = RetrievalRelevance(  
        model="databricks:/databricks-claude-opus-4-1"  
    )  
      
    # Use in evaluation  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        predict_fn=rag_app,  
        scorers=[relevance_judge, retrieval_judge]  
    )  
    

## Interpret resultsâ

The judge returns a `Feedback` object with:

  * **`value`** : "yes" if context is relevant, "no" if not
  * **`rationale`** : Explanation of why the judge found the context relevant or irrelevant



## Next stepsâ

  * [Explore other built-in judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) \- Learn about groundedness, safety, and correctness judges
  * [Create custom judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>) \- Build specialized judges for your use case
  * [Evaluate RAG applications](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) \- Apply relevance judges in comprehensive RAG evaluation
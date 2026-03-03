<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_context_sufficient -->

On this page

Last updated on **Feb 17, 2026**

# RetrievalSufficiency judge

The `RetrievalSufficiency` judge evaluates whether the retrieved context (from RAG applications, agents, or any system that retrieves documents) contains enough information to adequately answer the user's request based on the ground truth label provided as `expected_facts` or an `expected_response`. This built-in LLM judge is designed for evaluating RAG systems where you need to ensure that your retrieval process is providing all necessary information.

For API details, see the [MLflow documentation](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.RetrievalSufficiency>).

For detailed documentation and additional examples, see the [MLflow RetrievalSufficiency documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/rag/context-sufficiency/>).

## Prerequisites for running the examplesâ

  1. Install MLflow and required packages.

Bash
         
         pip install --upgrade "mlflow[databricks]>=3.4.0"  
         

  2. Create an MLflow experiment by following the [setup your environment quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>).




## Usage examplesâ

The `RetrievalSufficiency` judge can be invoked directly for single trace assessment or used with MLflow's evaluation framework for batch evaluation.

**Requirements:**

  * **Trace requirements** :
    * The MLflow Trace must contain at least one span with `span_type` set to `RETRIEVER`
    * `inputs` and `outputs` must be on the Trace's root span
  * **Ground-truth labels** : Required - must provide either `expected_facts` or `expected_response` in the `expectations` dictionary



  * Invoke directly
  * Invoke with evaluate()



Python
    
    
    from mlflow.genai.scorers import retrieval_sufficiency  
    import mlflow  
      
    # Get a trace from a previous run  
    trace = mlflow.get_trace("<your-trace-id>")  
      
    # Assess if the retrieved context is sufficient for the expected facts  
    feedback = retrieval_sufficiency(  
        trace=trace,  
        expectations={  
            "expected_facts": [  
                "MLflow has four main components",  
                "Components include Tracking",  
                "Components include Projects",  
                "Components include Models",  
                "Components include Registry"  
            ]  
        }  
    )  
    print(feedback)  
    

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import RetrievalSufficiency  
      
    # Evaluate traces from previous runs with ground truth expectations  
    results = mlflow.genai.evaluate(  
        data=eval_dataset,  # Dataset with trace data and expected_facts  
        scorers=[RetrievalSufficiency()]  
    )  
    

### RAG exampleâ

Here's a complete example showing how to create a RAG application and evaluate if retrieved context is sufficient:

  1. Initialize an OpenAI client to connect to either Databricks-hosted LLMs or LLMs hosted by OpenAI.

     * Databricks-hosted LLMs
     * OpenAI-hosted LLMs

Use `databricks-openai` to get an OpenAI client that connects to Databricks-hosted LLMs. Select a model from the [available foundation models](</aws/en/machine-learning/foundation-model-apis/supported-models>).

Python
    
    import mlflow  
    from databricks_openai import DatabricksOpenAI  
      
    # Enable MLflow's autologging to instrument your application with Tracing  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/docs-demo")  
      
    # Create an OpenAI client that is connected to Databricks-hosted LLMs  
    client = DatabricksOpenAI()  
      
    # Select an LLM  
    model_name = "databricks-claude-sonnet-4"  
    

Use the native OpenAI SDK to connect to OpenAI-hosted models. Select a model from the [available OpenAI models](<https://platform.openai.com/docs/models>).

Python
    
    import mlflow  
    import os  
    import openai  
      
    # Ensure your OPENAI_API_KEY is set in your environment  
    # os.environ["OPENAI_API_KEY"] = "<YOUR_API_KEY>" # Uncomment and set if not globally configured  
      
    # Enable auto-tracing for OpenAI  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking to Databricks  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/docs-demo")  
      
    # Create an OpenAI client connected to OpenAI SDKs  
    client = openai.OpenAI()  
      
    # Select an LLM  
    model_name = "gpt-4o-mini"  
    

  2. Define and evaluate your RAG application:

Python
         
         from mlflow.genai.scorers import RetrievalSufficiency  
         from mlflow.entities import Document  
         from typing import List  
           
           
         # Define a retriever function with proper span type  
         @mlflow.trace(span_type="RETRIEVER")  
         def retrieve_docs(query: str) -> List[Document]:  
             # Simulated retrieval - some queries return insufficient context  
             if "capital of france" in query.lower():  
                 return [  
                     Document(  
                         id="doc_1",  
                         page_content="Paris is the capital of France.",  
                         metadata={"source": "geography.txt"}  
                     ),  
                     Document(  
                         id="doc_2",  
                         page_content="France is a country in Western Europe.",  
                         metadata={"source": "countries.txt"}  
                     )  
                 ]  
             elif "mlflow components" in query.lower():  
                 # Incomplete retrieval - missing some components  
                 return [  
                     Document(  
                         id="doc_3",  
                         page_content="MLflow has multiple components including Tracking and Projects.",  
                         metadata={"source": "mlflow_intro.txt"}  
                     )  
                 ]  
             else:  
                 return [  
                     Document(  
                         id="doc_4",  
                         page_content="General information about data science.",  
                         metadata={"source": "ds_basics.txt"}  
                     )  
                 ]  
           
         # Define your RAG app  
         @mlflow.trace  
         def rag_app(query: str):  
             # Retrieve documents  
             docs = retrieve_docs(query)  
             context = "\n".join([doc.page_content for doc in docs])  
           
             # Generate response  
             messages = [  
                 {"role": "system", "content": f"Answer based on this context: {context}"},  
                 {"role": "user", "content": query}  
             ]  
           
             response = client.chat.completions.create(  
                 # This example uses Databricks hosted Claude.  If you provide your own OpenAI credentials, replace with a valid OpenAI model e.g., gpt-4o, etc.  
                 model=model_name,  
                 messages=messages  
             )  
           
             return {"response": response.choices[0].message.content}  
           
         # Create evaluation dataset with ground truth  
         eval_dataset = [  
             {  
                 "inputs": {"query": "What is the capital of France?"},  
                 "expectations": {  
                     "expected_facts": ["Paris is the capital of France."]  
                 }  
             },  
             {  
                 "inputs": {"query": "What are all the MLflow components?"},  
                 "expectations": {  
                     "expected_facts": [  
                         "MLflow has four main components",  
                         "Components include Tracking",  
                         "Components include Projects",  
                         "Components include Models",  
                         "Components include Registry"  
                     ]  
                 }  
             }  
         ]  
           
         # Run evaluation with RetrievalSufficiency scorer  
         eval_results = mlflow.genai.evaluate(  
             data=eval_dataset,  
             predict_fn=rag_app,  
             scorers=[  
                 RetrievalSufficiency(  
                     model="databricks:/databricks-gpt-oss-120b",  # Optional. Defaults to custom Databricks model.  
                 )  
             ]  
         )  
         




### Understand the resultsâ

The `RetrievalSufficiency` scorer evaluates each retriever span separately. It will:

  * Return "yes" if the retrieved documents contain all the information needed to generate the expected facts
  * Return "no" if the retrieved documents are missing critical information, along with a rationale explaining what's missing



This helps you identify when your retrieval system is failing to fetch all necessary information, which is a common cause of incomplete or incorrect responses in RAG applications.

## Select the LLM that powers the judgeâ

By default, these judges use a Databricks-hosted LLM designed to perform GenAI quality assessments. You can change the judge model by using the `model` argument in the judge definition. The model must be specified in the format `<provider>:/<model-name>`, where `<provider>` is a LiteLLM-compatible model provider. If you use `databricks` as the model provider, the model name is the same as the serving endpoint name.

You can customize the judge by providing a different judge model:

Python
    
    
    from mlflow.genai.scorers import RetrievalSufficiency  
      
    # Use a different judge model  
    sufficiency_judge = RetrievalSufficiency(  
        model="databricks:/databricks-gpt-5-mini"  # Or any LiteLLM-compatible model  
    )  
      
    # Use in evaluation  
    eval_results = mlflow.genai.evaluate(  
        data=eval_dataset,  
        predict_fn=rag_app,  
        scorers=[sufficiency_judge]  
    )  
    

## Interpret resultsâ

The judge returns a `Feedback` object with:

  * **`value`** : "yes" if context is sufficient, "no" if insufficient
  * **`rationale`** : Explanation of which expected facts the context covers or lacks



## Next stepsâ

  * [Evaluate context relevance](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_context_relevant>) \- Ensure retrieved documents are relevant before checking sufficiency
  * [Evaluate groundedness](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/is_grounded>) \- Verify that responses use only the provided context
  * [Build evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>) \- Create ground truth datasets with expected facts for testing
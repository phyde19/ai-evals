<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/human-feedback -->

On this page

Last updated on **Nov 5, 2025**

# 10-minute demo: Collect human feedback

Copy notebook link for import

Copy a link to the clipboard for importing this page as a notebook

Open notebook in new tab

Open a notebook containing all code in this page in a new tab

This tutorial shows how to collect end-user feedback, add developer annotations, create expert review sessions, and use that feedback to evaluate your GenAI app's quality.

## What you will achieveâ

By the end of this tutorial, you will:

  * Instrument a GenAI app with MLflow tracing
  * Collect end-user feedback, simulated using the SDK in this example
  * Add developer feedback interactively through the UI
  * View feedback alongside your traces
  * Collect expert feedback by creating a labeling session for structured expert review



## Environment setupâ

Install required packages:

  * `mlflow[databricks]`: Use the latest version of MLflow to get more features and improvements.
  * `openai`: This app will use the OpenAI API client to call Databricks-hosted models.



Python
    
    
    %pip install -q --upgrade "mlflow[databricks]>=3.1.0" openai  
    dbutils.library.restartPython()  
    

Create an MLflow experiment. If you are using a Databricks notebook, you can skip this step and use the default notebook experiment. Otherwise, follow the [environment setup quickstart](</aws/en/mlflow3/genai/getting-started/connect-environment>) to create the experiment and connect to the MLflow Tracking server.

## Step 1: Create and trace a simple appâ

First, create a simple GenAI app using an LLM with MLflow tracing. The app uses the OpenAI API to call a Databricks-hosted Foundation Model endpoint.

Python
    
    
    from databricks_openai import DatabricksOpenAI  
    import mlflow  
      
    # Enable automatic tracing for the OpenAI client  
    mlflow.openai.autolog()  
      
    # Create an OpenAI client that is connected to Databricks-hosted LLMs.  
    client = DatabricksOpenAI()  
      
    # Create a RAG app with tracing  
    @mlflow.trace  
    def my_chatbot(user_question: str) -> str:  
        # Retrieve relevant context  
        context = retrieve_context(user_question)  
      
        # Generate response using LLM with retrieved context  
        response = client.chat.completions.create(  
            model="databricks-claude-3-7-sonnet",  # If using OpenAI directly, use "gpt-4o" or "gpt-3.5-turbo"  
            messages=[  
                {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer questions."},  
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_question}"}  
            ],  
            temperature=0.7,  
            max_tokens=150  
        )  
        return response.choices[0].message.content  
      
    @mlflow.trace(span_type="RETRIEVER")  
    def retrieve_context(query: str) -> str:  
        # Simulated retrieval. In production, this could search a vector database  
        if "mlflow" in query.lower():  
            return "MLflow is an open-source platform for managing the end-to-end machine learning lifecycle. It provides tools for experiment tracking, model packaging, and deployment."  
        return "General information about machine learning and data science."  
      
    # Run the app to generate a trace  
    response = my_chatbot("What is MLflow?")  
    print(f"Response: {response}")  
      
    # Get the trace ID for the next step  
    trace_id = mlflow.get_last_active_trace_id()  
    print(f"Trace ID: {trace_id}")  
    

Output
    
    
    Response: MLflow is an open-source platform designed to manage the complete machine learning lifecycle. It provides tools and functionality for tracking experiments, packaging models, and deploying machine learning solutions. As a comprehensive platform, MLflow helps data scientists and machine learning engineers organize their work, compare results, and streamline the process of moving models from development to production.  
    Trace ID: tr-88989bb65dcb9bf49e0d03a3d5a302c9  
    

## Step 2: Collect end-user feedbackâ

When users interact with your app, they can provide feedback through UI elements like thumbs up/down buttons. This quickstart simulates an end user giving negative feedback by using the SDK directly.

Python
    
    
    from mlflow.entities.assessment import AssessmentSource, AssessmentSourceType  
      
    # Simulate end-user feedback from your app  
    # In production, this could be triggered when a user clicks thumbs down in your UI  
    mlflow.log_feedback(  
        trace_id=trace_id,  
        name="user_feedback",  
        value=False,  # False for thumbs down - user is unsatisfied  
        rationale="Missing details about MLflow's key features like Projects and Model Registry",  
        source=AssessmentSource(  
            source_type=AssessmentSourceType.HUMAN,  
            source_id="enduser_123",  # In production, this is the actual user ID  
        ),  
    )  
      
    print("End-user feedback recorded!")  
      
    # In a real app, you could:  
    # 1. Return the trace_id with your response to the frontend  
    # 2. When user clicks thumbs up/down, call your backend API  
    # 3. Your backend calls mlflow.log_feedback() with the trace_id  
    

Output
    
    
    End-user feedback recorded!  
    

## Step 3: View feedback in the UIâ

Launch the MLflow UI to see your traces with feedback:

  1. Navigate to your MLflow experiment.
  2. Navigate to the **Logs** tab.
  3. Click on your trace.
  4. The trace details dialog appears. Under **Assessments** on the right side of the dialog, the `user_feedback` shows `false`, indicating that the user marked the response thumbs-down.



## Step 4: Add developer annotations using the UIâ

As a developer, you can also add your own feedback and notes directly in the UI:

  1. In the **Logs** tab, click on a trace to open it.
  2. Click on any span (choose the root span for trace-level feedback).
  3. In the **Assessments** tab on the right, click **Add new assessment** and fill in the following:
     * **Type** : `Feedback`.
     * **Name** : `accuracy_score`.
     * **Value** : `.75`.
     * **Rationale** : `This answer includes the core elements of ML lifecycle management, experiment tracking, packaging, and deployment. However, it does not mention the model registry, project packaging, integration with Generative AI and LLMs, or unique features available in Databricks-managed MLflow, which are now considered essential to a complete description of the platform.`
  4. Click **Create**.



After you refresh the page, columns for the new assessments appear in the Logs table.

## Step 5: Send trace for expert reviewâ

The negative end-user feedback from Step 2 signals a potential quality issue, but only domain experts can confirm if there's truly a problem and provide the correct answer. Create a labeling session to get authoritative expert feedback:

Python
    
    
    from mlflow.genai.label_schemas import create_label_schema, InputCategorical, InputText  
    from mlflow.genai.labeling import create_labeling_session  
      
    # Define what feedback to collect  
    accuracy_schema = create_label_schema(  
        name="response_accuracy",  
        type="feedback",  
        title="Is the response factually accurate?",  
        input=InputCategorical(options=["Accurate", "Partially Accurate", "Inaccurate"]),  
        overwrite=True  
    )  
      
    ideal_response_schema = create_label_schema(  
        name="expected_response",  
        type="expectation",  
        title="What would be the ideal response?",  
        input=InputText(),  
        overwrite=True  
    )  
      
    # Create a labeling session  
    labeling_session = create_labeling_session(  
        name="quickstart_review",  
        label_schemas=[accuracy_schema.name, ideal_response_schema.name],  
    )  
      
    # Add your trace to the session  
    # Get the most recent trace from the current experiment  
    traces = mlflow.search_traces(  
        max_results=1  # Gets the most recent trace  
    )  
    labeling_session.add_traces(traces)  
      
    # Share with reviewers  
    print(f"Trace sent for review!")  
    print(f"Share this link with reviewers: {labeling_session.url}")  
    

Expert reviewers can now do the following:

  1. Open the Review App URL.

  2. See your trace with the question and response (including any end-user feedback).

  3. Assess whether the response is actually accurate.

  4. Provide the correct answer in `expected_response` to the question "What is MLflow?":
         
         MLflow is an open-source platform for managing the machine learning lifecycle, including experiment tracking, model registry, packaging, deployment, and evaluation. It supports classical ML, deep learning, and generative AI workflows. On Databricks, MLflow provides managed, secure, and scalable integration for easy collaboration and governance  
         

  5. Submit their expert assessments as ground truth.




You can also use the MLflow 3 UI to create a labeling session, as follows:

  1. On the Experiment page, click the **Labeling** tab.
  2. At the left, use the **Sessions** and **Schemas** tabs to add a new label schema and create a new session.



## Step 6: Use feedback to evaluate your appâ

After experts provide feedback, use their `expected_response` labels to evaluate your app with MLflow's `Correctness` scorer:

This example directly uses the traces for evaluation. In your application, Databricks recommends adding labeled traces to an MLflow Evaluation Dataset which provides version tracking and lineage. Learn about [building evaluation datasets](</aws/en/mlflow3/genai/eval-monitor/build-eval-dataset>).

Python
    
    
    from mlflow.genai.scorers import Correctness  
      
    # Get traces from the labeling session  
    labeled_traces = mlflow.search_traces(  
        run_id=labeling_session.mlflow_run_id,  # Labeling Sessions are MLflow Runs  
    )  
      
    # Evaluate your app against expert expectations  
    eval_results = mlflow.genai.evaluate(  
        data=labeled_traces,  
        predict_fn=my_chatbot,  # The app we created in Step 1  
        scorers=[Correctness()]  # Compares outputs to expected_response  
    )  
    

The Correctness scorer compares your app's outputs against the expert-provided `expected_response`, giving you quantitative feedback on alignment with expert expectations.

## Next stepsâ

Learn more details about collecting different types of human feedback:

  * [Label during development](</aws/en/mlflow3/genai/human-feedback/dev-annotations>) \- Learn advanced annotation techniques for development
  * [Vibe check with domain experts](</aws/en/mlflow3/genai/human-feedback/expert-feedback/live-app-testing>) \- Test your app interactively with experts
  * [Collect domain expert feedback](</aws/en/mlflow3/genai/human-feedback/expert-feedback/label-existing-traces>) \- Set up systematic expert review processes



## Example notebookâ

#### 10-minute demo: Collect human feedback

[Open notebook in new tab](<https://docs.databricks.com/aws/en/notebooks/source/mlflow3/genai/getting-started/human-feedback-quickstart.html>)

Copy link for import

Copy to clipboard
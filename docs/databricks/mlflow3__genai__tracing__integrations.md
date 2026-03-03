<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/ -->

On this page

Last updated on **Nov 26, 2025**

# MLflow Tracing Integrations

MLflow Tracing is integrated with a wide array of popular Generative AI libraries and frameworks, offering a **one-line automatic tracing** experience for all of them. This allows you to gain immediate observability into your GenAI applications with minimal setup.

This broad support means you can gain observability without significant code changes, leveraging the tools you already use. For custom components or unsupported libraries, MLflow also provides powerful [manual tracing APIs](</aws/en/mlflow3/genai/tracing/app-instrumentation/manual-tracing/>).

Automatic tracing captures your application's logic and intermediate steps, such as LLM calls, tool usage, and agent interactions, based on your implementation of the specific library or SDK.

note

On serverless compute clusters, autologging for genAI tracing frameworks is not automatically enabled. You must explicitly enable autologging by calling the appropriate `mlflow.<library>.autolog()` function for the specific integrations you want to trace.

## Top Integrations at a Glanceâ

Here are quick-start examples for some of the most commonly used integrations. Click on a tab to see a basic usage example. For detailed prerequisites and more advanced scenarios for each, please visit their dedicated integration pages (linked from the tabs or the list below).

  * OpenAI
  * LangChain
  * LangGraph
  * Anthropic
  * DSPy
  * Databricks
  * Bedrock
  * AutoGen



Python
    
    
    import mlflow  
    import openai  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # import os  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    # Enable auto-tracing for OpenAI  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/openai-tracing-demo")  
      
    openai_client = openai.OpenAI()  
      
    messages = [  
        {  
            "role": "user",  
            "content": "What is the capital of France?",  
        }  
    ]  
      
    response = openai_client.chat.completions.create(  
        model="gpt-4o-mini",  
        messages=messages,  
        temperature=0.1,  
        max_tokens=100,  
    )  
    # View trace in MLflow UI  
    

[Full OpenAI Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/openai>)

Python
    
    
    import mlflow  
    from langchain.prompts import PromptTemplate  
    from langchain_core.output_parsers import StrOutputParser  
    from langchain_openai import ChatOpenAI  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # import os  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.langchain.autolog()  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/langchain-tracing-demo")  
      
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=1000)  
    prompt = PromptTemplate.from_template("Tell me a joke about {topic}.")  
    chain = prompt | llm | StrOutputParser()  
      
    chain.invoke({"topic": "artificial intelligence"})  
    # View trace in MLflow UI  
    

[Full LangChain Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/langchain>)

Python
    
    
    import mlflow  
    from langchain_core.tools import tool  
    from langchain_openai import ChatOpenAI  
    from langgraph.prebuilt import create_react_agent  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # import os  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.langchain.autolog() # LangGraph uses LangChain's autolog  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/langgraph-tracing-demo")  
      
    @tool  
    def get_weather(city: str):  
        """Use this to get weather information."""  
        return f"It might be cloudy in {city}"  
      
    llm = ChatOpenAI(model="gpt-4o-mini")  
    graph = create_react_agent(llm, [get_weather])  
    result = graph.invoke({"messages": [("user", "what is the weather in sf?")]})  
    # View trace in MLflow UI  
    

[Full LangGraph Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/langgraph>)

Python
    
    
    import mlflow  
    import anthropic  
    import os  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.anthropic.autolog()  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/anthropic-tracing-demo")  
      
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))  
    message = client.messages.create(  
        model="claude-3-5-sonnet-20241022",  
        max_tokens=1024,  
        messages=[{"role": "user", "content": "Hello, Claude"}],  
    )  
    # View trace in MLflow UI  
    

[Full Anthropic Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/anthropic>)

Python
    
    
    import mlflow  
    import dspy  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # import os  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.dspy.autolog()  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/dspy-tracing-demo")  
      
    lm = dspy.LM("openai/gpt-4o-mini") # Assumes OPENAI_API_KEY is set  
    dspy.configure(lm=lm)  
      
    class SimpleSignature(dspy.Signature):  
        input_text: str = dspy.InputField()  
        output_text: str = dspy.OutputField()  
      
    program = dspy.Predict(SimpleSignature)  
    result = program(input_text="Summarize MLflow Tracing.")  
    # View trace in MLflow UI  
    

[Full DSPy Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/dspy>)

Python
    
    
    import mlflow  
    import os  
    from openai import OpenAI # Databricks FMAPI uses OpenAI client  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.openai.autolog() # Traces Databricks FMAPI using OpenAI client  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/databricks-fmapi-tracing")  
      
    client = OpenAI(  
        api_key=os.environ.get("DATABRICKS_TOKEN"),  
        base_url=f"{os.environ.get('DATABRICKS_HOST')}/serving-endpoints"  
    )  
    response = client.chat.completions.create(  
        model="databricks-llama-4-maverick",  
        messages=[{"role": "user", "content": "Key features of MLflow?"}],  
    )  
    # View trace in MLflow UI  
    

[Full Databricks Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/databricks-foundation-models>)

Python
    
    
    import mlflow  
    import boto3  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # import os  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.bedrock.autolog()  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/bedrock-tracing-demo")  
      
    bedrock = boto3.client(  
        service_name="bedrock-runtime",  
        region_name="us-east-1" # Replace with your region  
    )  
    response = bedrock.converse(  
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",  
        messages=[{"role": "user", "content": "Hello World in one line."}]  
    )  
    # View trace in MLflow UI  
    

[Full Bedrock Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/bedrock>)

Python
    
    
    import mlflow  
    from autogen import ConversableAgent  
    import os  
      
    # If running this code outside of a Databricks notebook (e.g., locally),  
    # uncomment and set the following environment variables to point to your Databricks workspace:  
    # os.environ["DATABRICKS_HOST"] = "https://your-workspace.cloud.databricks.com"  
    # os.environ["DATABRICKS_TOKEN"] = "your-personal-access-token"  
      
    mlflow.autogen.autolog()  
      
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/autogen-tracing-demo")  
      
    config_list = [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]  
    assistant = ConversableAgent("assistant", llm_config={"config_list": config_list})  
    user_proxy = ConversableAgent("user_proxy", human_input_mode="NEVER", code_execution_config=False)  
      
    user_proxy.initiate_chat(assistant, message="What is 2+2?")  
    # View trace in MLflow UI  
    

[Full AutoGen Integration Guide](</aws/en/mlflow3/genai/tracing/integrations/autogen>)

## Secure API Key Managementâ

For production environments, Databricks recommends that you use AI Gateway or Databricks secrets to manage API keys. AI Gateway is the preferred method and offers additional governance features.

warning

Never commit API keys directly in your code or notebooks. Always use AI Gateway or Databricks secrets for sensitive credentials.

  * AI Gateway (Recommended)
  * Databricks secrets



Databricks recommends [Mosaic AI Gateway](</aws/en/ai-gateway/>) for governing and monitoring access to gen AI models.

Create a Foundation Model endpoint configured with AI Gateway:

  1. In your Databricks workspace, go to **Serving** > **Create new endpoint**.
  2. Choose an endpoint type and provider.
  3. Configure the endpoint with your API key.
  4. During endpoint configuration, enable **AI Gateway** and configure rate limiting, fallbacks, and guardrails as needed.
  5. You can get autogenerated code to quickly start querying the endpoint. Go to **Serving** > your endpoint > **Use** > **Query**. Make sure to add the tracing code:



Python
    
    
    import mlflow  
    from openai import OpenAI  
    import os  
      
    # How to get your Databricks token: https://docs.databricks.com/en/dev-tools/auth/pat.html  
    # DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN')  
    # Alternatively in a Databricks notebook you can use this:  
    DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()  
      
    # Enable auto-tracing for OpenAI  
    mlflow.openai.autolog()  
      
    # Set up MLflow tracking (if running outside Databricks)  
    # If running in a Databricks notebook, these are not needed.  
    mlflow.set_tracking_uri("databricks")  
    mlflow.set_experiment("/Shared/my-genai-app")  
      
    client = OpenAI(  
      api_key=DATABRICKS_TOKEN,  
      base_url="<YOUR_HOST_URL>/serving-endpoints"  
    )  
      
    chat_completion = client.chat.completions.create(  
      messages=[  
      {  
        "role": "system",  
        "content": "You are an AI assistant"  
      },  
      {  
        "role": "user",  
        "content": "What is MLflow?"  
      }  
      ],  
      model="<YOUR_ENDPOINT_NAME>",  
      max_tokens=256  
    )  
      
    print(chat_completion.choices[0].message.content)  
    

Use [Databricks secrets](</aws/en/security/secrets/>) to manage API keys:

  1. Create a secret scope and store your API key:

Python
         
         from databricks.sdk import WorkspaceClient  
           
         # Set your secret scope and key names  
         secret_scope_name = "llm-secrets"  # Choose an appropriate scope name  
         secret_key_name = "api-key"        # Choose an appropriate key name  
           
         # Create the secret scope and store your API key  
         w = WorkspaceClient()  
         w.secrets.create_scope(scope=secret_scope_name)  
         w.secrets.put_secret(  
             scope=secret_scope_name,  
             key=secret_key_name,  
             string_value="your-api-key-here"  # Replace with your actual API key  
         )  
         

  2. Retrieve and use the secret in your code:

Python
         
         import mlflow  
         import openai  
         import os  
           
         # Configure your secret scope and key names  
         secret_scope_name = "llm-secrets"  
         secret_key_name = "api-key"  
           
         # Retrieve the API key from Databricks secrets  
         os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(  
             scope=secret_scope_name,  
             key=secret_key_name  
         )  
           
         # Enable automatic tracing  
         mlflow.openai.autolog()  
           
         # Use OpenAI client with securely managed API key  
         client = openai.OpenAI()  
         response = client.chat.completions.create(  
             model="gpt-4o-mini",  
             messages=[{"role": "user", "content": "Explain MLflow Tracing"}],  
             max_tokens=100  
         )  
         




## Enabling Multiple Auto Tracing Integrationsâ

As GenAI applications often combine multiple libraries, MLflow Tracing allows you to enable auto-tracing for several integrations simultaneously, providing a unified tracing experience.

For example, to enable both LangChain and direct OpenAI tracing:

Python
    
    
    import mlflow  
      
    # Enable MLflow Tracing for both LangChain and OpenAI  
    mlflow.langchain.autolog()  
    mlflow.openai.autolog()  
      
    # Your code using both LangChain and OpenAI directly...  
    # ... an example can be found on the Automatic Tracing page ...  
    

MLflow will generate a single, cohesive trace that combines steps from both LangChain and direct OpenAI LLM calls, allowing you to inspect the complete flow. More examples of combining integrations can be found on the [Automatic Tracing](</aws/en/mlflow3/genai/tracing/app-instrumentation/automatic#combine-manual-automatic>) page.

## Disabling Auto Tracingâ

Auto tracing for any specific library can be disabled by calling `mlflow.<library>.autolog(disable=True)`. To disable all autologging integrations at once, use `mlflow.autolog(disable=True)`.

Python
    
    
    import mlflow  
      
    # Disable for a specific library  
    mlflow.openai.autolog(disable=True)  
      
    # Disable all autologging  
    mlflow.autolog(disable=True)
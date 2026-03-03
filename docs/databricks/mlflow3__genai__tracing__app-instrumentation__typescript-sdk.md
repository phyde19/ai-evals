<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/app-instrumentation/typescript-sdk -->

On this page

Last updated on **Sep 17, 2025**

# Instrument Node.js applications with MLflow Tracing

[MLflow's TypeScript SDK](<https://www.npmjs.com/package/mlflow-tracing>) brings [MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) capabilities to TypeScript and JavaScript applications. Add production-ready observability to your GenAI applications with minimal code changes and leverage Databricks' powerful analytics and monitoring platform.

## Requirementsâ

tip

Databricks recommends installing the latest version of the MLflow Tracing TypeScript SDK when developing Node.js applications with tracing.

To instrument your Node.js applications with MLflow Tracing, install the following:

  * `mlflow-tracing` from the [npm registry](<https://www.npmjs.com/package/mlflow-tracing>)
  * Node.js 14 or above
  * A Databricks workspace with access to MLflow Experiments



For automatic tracing with OpenAI, you also need:

  * `mlflow-openai` from the [npm registry](<https://www.npmjs.com/package/mlflow-openai>)



## Set up the SDKâ

### Install the packageâ

Install the package from the [npm registry](<https://www.npmjs.com/package/mlflow-tracing>):

Bash
    
    
    npm install mlflow-tracing  
    

### Create an MLflow Experimentâ

  1. Open your Databricks workspace.
  2. In the left sidebar, under **AI/ML** , click **Experiments**.
  3. At the top of the Experiments page, click **GenAI apps & agents**.
  4. Click the  icon next to the experiment name to find the experiment ID and note it down.



### Configure authenticationâ

Choose one of the following authentication methods:

  * Environment Variables
  * .env File



  1. In your MLflow Experiment, click the  icon > **Log traces locally** > click **Generate API Key**.
  2. Copy and run the generated code in your terminal:



Bash
    
    
    export DATABRICKS_TOKEN=<databricks-personal-access-token>  
    export DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com  
    

  1. In your MLflow Experiment, click the  icon > **Log traces locally** > click **Generate API Key**.
  2. Copy the generated code to a `.env` file in your project root:



Bash
    
    
    DATABRICKS_TOKEN=<databricks-personal-access-token>  
    DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com  
    

### Initialize the SDKâ

In your Node.js application, initialize the SDK with the experiment ID:

TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    mlflow.init({  
      trackingUri: 'databricks',  
      experimentId: '<your-experiment-id>',  
    });  
    

## Automatic Tracingâ

Add one line of code to automatically trace supported libraries. MLflow Tracing TypeScript SDK currently supports automatic tracing for OpenAI SDK.

To use automatic tracing for OpenAI, install [`mlflow-openai`](<https://www.npmjs.com/package/mlflow-openai>) package:

Bash
    
    
    npm install mlflow-openai  
    

Then, wrap the OpenAI client with the [`tracedOpenAI`](<https://www.npmjs.com/package/mlflow-openai>) function:

TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    // Initialize the tracing SDK  
    mlflow.init({  
      trackingUri: 'databricks',  
      experimentId: '<your-experiment-id>',  
    });  
      
    import { OpenAI } from 'openai';  
    import { tracedOpenAI } from 'mlflow-openai';  
      
    // Wrap the OpenAI client with the tracedOpenAI function  
    const client = tracedOpenAI(new OpenAI());  
      
    // Invoke the client as usual  
    const response = await client.chat.completions.create({  
      model: 'gpt-4o-mini',  
      messages: [  
        { role: 'system', content: 'You are a helpful weather assistant.' },  
        { role: 'user', content: "What's the weather like in Seattle?" },  
      ],  
    });  
    

## Manual Tracingâ

### Tracing a function with the `trace` APIâ

The `trace` API is useful when you want to trace a function.

  * Named function
  * Anonymous function



TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    const getWeather = async (city: string) => {  
      return `The weather in ${city} is sunny`;  
    };  
      
    // Wrap the function with mlflow.trace to create a traced function  
    const tracedGetWeather = mlflow.trace(getWeather, { name: 'get-weather' });  
      
    // Invoke the traced function as usual  
    const result = await tracedGetWeather('San Francisco');  
    

TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    const getWeather = mlflow.trace(  
      (city: string) => {  
        return `The weather in ${city} is sunny`;  
      },  
      // When wrapping an anonymous function, specify the span name  
      { name: 'get-weather' },  
    );  
      
    // Invoke the traced function as usual  
    const result = getWeather('San Francisco');  
    

On the invocation of the traced function, MLflow will automatically create a span that captures:

  * Input arguments
  * Return value
  * Exception information if thrown
  * Latency



### Capturing nested function callsâ

If you trace nested functions, MLflow will generate a trace with multiple spans, where the span structure captures the nested function calls.

TypeScript
    
    
    const sum = mlflow.trace(  
      (a: number, b: number) => {  
        return a + b;  
      },  
      { name: 'sum' },  
    );  
      
    const multiply = mlflow.trace(  
      (a: number, b: number) => {  
        return a * b;  
      },  
      { name: 'multiply' },  
    );  
      
    const computeArea = mlflow.trace(  
      (a: number, b: number, h: number) => {  
        const sumOfBase = sum(a, b);  
        const area = multiply(sumOfBase, h);  
        return multiply(area, 0.5);  
      },  
      { name: 'compute-area' },  
    );  
      
    computeArea(1, 2, 3);  
    

The trace will look like this:
    
    
    - compute-area  
      - sum (a=1, b=2)  
      - multiply (a=3, b=3)  
      - multiply (a=9, b=0.5)  
    

### Tracing a class method with the `@trace` APIâ

TypeScript version 5.0+ supports decorators. MLflow Tracing supports this syntax to trace class methods easily. MLflow will automatically create a span that captures:

  * Input arguments
  * Return value
  * Exception information if thrown
  * Latency



TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    class MyClass {  
      @mlflow.trace({ spanType: mlflow.SpanType.LLM })  
      generateText(prompt: string) {  
        return "It's sunny in Seattle!";  
      }  
    }  
      
    const myClass = new MyClass();  
    myClass.generateText("What's the weather like in Seattle?");  
    

### Tracing a block of code with the `withSpan` APIâ

The `withSpan` API is useful when you want to trace a block of code, not a function.

TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    const question = "What's the weather like in Seattle?";  
      
    const result = await mlflow.withSpan(  
      async (span: mlflow.Span) => {  
        return "It's sunny in Seattle!";  
      },  
      // Pass name, span type, and inputs as options.  
      {  
        name: 'generateText',  
        spanType: mlflow.SpanType.TOOL,  
        inputs: { prompt: question },  
      },  
    );  
    

### Create and End a Span Explicitlyâ

To get more control over the span lifecycle, you can create and end a span explicitly.

TypeScript
    
    
    import * as mlflow from 'mlflow-tracing';  
      
    const span = mlflow.startSpan({  
      name: 'generateText',  
      spanType: mlflow.SpanType.LLM,  
      inputs: { prompt: question },  
    });  
      
    span.end({  
      outputs: { answer: "It's sunny in Seattle!" },  
      status: 'OK',  
    });  
    

## Grouping Traces by Users and Sessionsâ

Many real-world applications use sessions to maintain multi-turn user interactions. On the other hand, traces are often generated per-request. MLflow supports grouping traces by user sessions to help you understand an end-user's journey and identify issues. See [Add context to traces](</aws/en/mlflow3/genai/tracing/add-context-to-traces>) guide for more details.

## Full-stack example applicationâ

Check out the [full-stack example](<https://github.com/mlflow/mlflow/tree/main/examples/mlflow-tracing/typescript-openai>) for a complete example of how to use the MLflow Tracing TypeScript SDK in a Node.js application.

## Next stepsâ

See the following pages:

  * [Debug and observe your app](</aws/en/mlflow3/genai/tracing/observe-with-traces/>) \- Use the Trace UI to analyze your application's behavior and performance
  * [Evaluate app quality](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) \- Leverage your traces to systematically assess and improve application quality
  * [Production monitoring](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) \- Track quality metrics in real-time in production
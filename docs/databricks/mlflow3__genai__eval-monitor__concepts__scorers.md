<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/concepts/scorers -->

On this page

Last updated on **Nov 26, 2025**

# Scorers and LLM judges

Scorers are a key component of the MLflow GenAI evaluation framework. They provide a unified interface to define evaluation criteria for your models, agents, and applications. Like their name suggests, scorers score how well your application did based on the evaluation criteria. This could be a pass/fail, true/false, numerical value, or a categorical value.

You can use the same scorer for [evaluation in development](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) and [monitoring in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) to keep evaluation consistent throughout the application lifecycle.

Choose the right type of scorer depending on how much customization and control you need. Each approach builds on the previous one, adding more complexity and control.

Start with built-in judges for quick evaluation. As your needs evolve, build [custom LLM judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>) for domain-specific criteria and create [custom code-based scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>) for deterministic business logic.

**Approach**| **Level of customization**| **Use cases**| [**Built-in judges**](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers#built-in-judges>)|  Minimal| Quickly try LLM evaluation with built-in scorers such as `Correctness` and `RetrievalGroundedness`.| [**Guidelines judges**](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/guidelines>)|  Moderate| A built-in judge that check whether responses pass or fail custom natural-language rules, such as style or factuality guidelines.| [**Custom judges**](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>)|  Full| Create fully customized LLM judges with detailed evaluation criteria and feedback optimization.Capable of returning numerical scores, categories, or boolean values.| [**Code-based scorers**](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>)|  Full| Programmatic and deterministic scorers that evaluate things like exact matching, format validation, and performance metrics.  
---|---|---  
  
The following screenshot shows the results from the built-in LLM judge `Safety` and a custom scorer `exact_match`:

## How scorers workâ

A scorer receives a [Trace](</aws/en/mlflow3/genai/tracing/tracing-101>) from either `evaluate()` or the monitoring service. It then does the following:

  1. Parses the `trace` to extract specific fields and data that are used to assess quality
  2. Runs the scorer to perform the quality assessment based on the extracted fields and data
  3. Returns the quality assessment as [`Feedback`](</aws/en/mlflow3/genai/human-feedback/dev-annotations>) to attach to the `trace`



## LLMs as judgesâ

LLM judges are a type of MLflow `Scorer` that uses Large Language Models for quality assessment.

Think of a judge as an AI assistant specialized in quality assessment. It can evaluate your app's inputs, outputs, and even explore the entire execution trace to make assessments based on criteria you define. For example, a judge can understand that `give me healthy food options` and `food to keep me fit` are similar queries.

note

Judges are a type of scorer that use LLMs for evaluation. Use them directly with `mlflow.genai.evaluate()` or wrap them in [custom scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>) for advanced scoring logic.

### Built-in LLM judgesâ

MLflow provides research-validated judges for common use cases. For the complete list and detailed documentation, see the [MLflow predefined scorers documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/>).

Judge| Arguments| Requires ground truth| What it evaluates| [`RelevanceToQuery`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/rag/relevance/#relevancetoquery-judge>)| `inputs`, `outputs`| No| Is the response directly relevant to the user's request?| [`RetrievalRelevance`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/rag/relevance/#retrievalrelevance-judge>)| `inputs`, `outputs`| No| Is the retrieved context directly relevant to the user's request?| [`Safety`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/response-quality/safety/>)| `inputs`, `outputs`| No| Is the content free from harmful, offensive, or toxic material?| [`RetrievalGroundedness`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/rag/groundedness/>)| `inputs`, `outputs`| No| Is the response grounded in the information provided in the context? Is the agent hallucinating?| [`Correctness`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/response-quality/correctness/>)| `inputs`, `outputs`, `expectations`| Yes| Is the response correct as compared to the provided ground truth?| [`Completeness`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#response-quality>)| `inputs`, `outputs`, `expectations`| Yes| Does the agent address all questions in a single user prompt?| [`Fluency`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#response-quality>)| `inputs`, `outputs`| No| Is the response grammatically correct and naturally flowing?| [`Equivalence`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#response-quality>)| `inputs`, `outputs`, `expectations`| Yes| Is the response equivalent to the expected output?| [`RetrievalSufficiency`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/rag/context-sufficiency/>)| `inputs`, `outputs`, `expectations`| Yes| Does the context provide all necessary information to generate a response that includes the ground truth facts?| [`ToolCallCorrectness`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/tool-call/correctness/>)| `inputs`, `outputs`, `expectations`| Yes| Are the tool calls and arguments correct for the user query?| [`ToolCallEfficiency`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/tool-call/efficiency/>)| `inputs`, `outputs`| No| Are the tool calls efficient without redundancy?| [`Guidelines`](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/guidelines#prebuilt-guidelines-scorer>)| `inputs`, `outputs`| No| Does the response meet specified natural language criteria?| [`ExpectationsGuidelines`](</aws/en/mlflow3/genai/eval-monitor/concepts/judges/guidelines#prebuilt-expectationsguidelines-scorer>)| `inputs`, `outputs`, `expectations`| No (but needs guidelines in expectations)| Does the response meet per-example natural language criteria?  
---|---|---|---  
  
### Multi-turn judgesâ

For conversational AI systems, MLflow provides judges that evaluate entire conversation sessions rather than individual turns. These judges analyze the complete conversation history to assess quality patterns that emerge over multiple interactions.

For the complete list and detailed documentation, see the [MLflow predefined scorers documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>).

Judge| Arguments| Requires ground truth| What it evaluates| [`ConversationCompleteness`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`| No| Did the agent address all user questions throughout the conversation?| [`UserFrustration`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`| No| Did the user become frustrated? Was the frustration resolved?| [`KnowledgeRetention`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`| No| Does the agent correctly retain information from earlier in the conversation?| [`ConversationalGuidelines`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`, `guidelines`| No| Do the assistant's responses comply with provided guidelines throughout the conversation?| [`ConversationalRoleAdherence`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`| No| Does the assistant maintain its assigned role throughout the conversation?| [`ConversationalSafety`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`| No| Are the assistant's responses safe and free of harmful content?| [`ConversationalToolCallEfficiency`](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>)| `session`| No| Was tool usage across the conversation efficient and appropriate?  
---|---|---|---  
  
For complete documentation on multi-turn evaluation, see [Evaluate conversations](</aws/en/mlflow3/genai/eval-monitor/evaluate-conversations>).

### Custom LLM judgesâ

In addition to the built-in judges, MLflow makes it easy to create your own judges with custom prompts and instructions.

Use custom LLM judges when you need to define specialized evaluation tasks, need more control over grades or scores (not just pass/fail), or need to validate that your agent made appropriate decisions and performed operations correctly for your specific use case.

See [Custom judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>).

Once you've created custom judges, you can further improve their accuracy by [aligning them with human feedback](</aws/en/mlflow3/genai/eval-monitor/align-judges>).

### Select the LLM that powers the judgeâ

By default, each judge uses a Databricks-hosted LLM designed to perform GenAI quality assessments. You can change the judge model by using the `model` argument in the judge definition. Specify the model in the format `<provider>:/<model-name>`. For example:

Python
    
    
    from mlflow.genai.scorers import Correctness  
      
    Correctness(model="databricks:/databricks-gpt-5-mini")  
    

## Information about the models powering LLM judgesâ

  * LLM judges might use third-party services to evaluate your GenAI applications, including Azure OpenAI operated by Microsoft.
  * For Azure OpenAI, Databricks has opted out of Abuse Monitoring so no prompts or responses are stored with Azure OpenAI.
  * For European Union (EU) workspaces, LLM judges use models hosted in the EU. All other regions use models hosted in the US.
  * Disabling [Partner-powered AI features](</aws/en/databricks-ai/partner-powered>) prevents the LLM judge from calling partner-powered models. You can still use LLM judges by providing your own model.
  * LLM judges are intended to help customers evaluate their GenAI agents/applications, and LLM judge outputs should not be used to train, improve, or fine-tune an LLM.



### Judge accuracyâ

Databricks continuously improves judge quality through:

  * **Research validation** against human expert judgment
  * **Metrics tracking** : Cohen's Kappa, accuracy, F1 score
  * **Diverse testing** on academic and real-world datasets



See [Databricks blog on LLM judge improvements](<https://www.databricks.com/blog/databricks-announces-significant-improvements-built-llm-judges-agent-evaluation>) for details.

## Code-based scorersâ

Custom code-based scorers offer the ultimate flexibility to define precisely how your GenAI application's quality is measured. You can define evaluation metrics tailored to your specific business use case, whether based on simple heuristics, advanced logic, or programmatic evaluations.

Use custom scorers for the following scenarios:

  1. Defining a custom heuristic or code-based evaluation metric.
  2. Customizing how the data from your app's trace is mapped to built-in LLM judges.
  3. Using your own LLM (rather than a Databricks-hosted LLM judge) for evaluation.
  4. Any other use cases where you need more flexibility and control than provided by custom LLM judges.



See [Create custom code-based scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>).
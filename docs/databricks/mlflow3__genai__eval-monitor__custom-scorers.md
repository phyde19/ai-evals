<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/custom-scorers -->

On this page

Last updated on **Feb 2, 2026**

# Create custom code-based scorers

Custom code-based [scorers](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>) offer the ultimate flexibility to define precisely how your GenAI application's quality is measured. You can define evaluation metrics tailored to your specific business use case, whether based on simple heuristics, advanced logic, or programmatic evaluations.

Use custom scorers for the following scenarios:

  1. Defining a custom heuristic or code-based evaluation metric.
  2. Customizing how the data from your app's trace is mapped to [Databricks' research-backed LLM judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>).
  3. Using your own LLM (rather than a Databricks-hosted LLM judge) for evaluation.
  4. Any other use cases where you need more flexibility and control than provided by [custom LLM judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>).



For a tutorial with many examples, see [Code-based scorer examples](</aws/en/mlflow3/genai/eval-monitor/code-based-scorer-examples>).

## How custom scorers workâ

Custom scorers are written in Python and give you full control to evaluate any data from your app's traces. After you define a custom scorer, you can use it exactly like a [built-in LLM Judge](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers>). Like other scorers, the same custom scorer can be used for [evaluation in development](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) and reused for [monitoring in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>).

For example, suppose you want a scorer that checks if the response time of the LLM is within an acceptable range. The image of the MLflow UI below shows traces scored by this custom metric.

The code snippet below defines this custom scorer and uses it with [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>):

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import scorer  
    from mlflow.entities import Trace, Feedback, SpanType  
      
    @scorer  
    def llm_response_time_good(trace: Trace) -> Feedback:  
        # Search particular span type from the trace  
        llm_span = trace.search_spans(span_type=SpanType.CHAT_MODEL)[0]  
      
        response_time = (llm_span.end_time_ns - llm_span.start_time_ns) / 1e9 # second  
        max_duration = 5.0  
        if response_time <= max_duration:  
            return Feedback(  
                value="yes",  
                rationale=f"LLM response time {response_time:.2f}s is within the {max_duration}s limit."  
            )  
        else:  
            return Feedback(  
                value="no",  
                rationale=f"LLM response time {response_time:.2f}s exceeds the {max_duration}s limit."  
            )  
      
    # Evaluate the scorer using pre-generated traces  
    span_check_eval_results = mlflow.genai.evaluate(  
        data=generated_traces,  
        scorers=[llm_response_time_good]  
    )  
    

The example above illustrates a common pattern for code-based scorers:

  * The `@scorer` decorator is used to define the scorer.
  * The input to this scorer is the full `trace`, giving it access to the AI app's inputs, intermediate spans, and outputs.
  * Scorer logic can be fully custom. You can call LLMs or other scorers.
  * The output of this scorer is a rich `Feedback` object with values and explanations.
  * The metric name is `llm_response_time_good`, matching the scorer function name.



This pattern is just one possibility for code-based scorers. The rest of this article explains options for defining custom scorers.

##  Define scorers with the `@scorer` decoratorâ

Most code-based scorers should be defined using the [`@scorer` decorator](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.scorer>). Below is the signature for such scorers, illustrating possible inputs and outputs.

Python
    
    
    from mlflow.genai.scorers import scorer  
    from typing import Optional, Any  
    from mlflow.entities import Feedback  
      
    @scorer  
    def my_custom_scorer(  
        *,  # All arguments are keyword-only  
        inputs: Optional[dict[str, Any]],       # App's raw input, a dictionary of input argument names and values  
        outputs: Optional[Any],                 # App's raw output  
        expectations: Optional[dict[str, Any]], # Ground truth, a dictionary of label names and values  
        trace: Optional[mlflow.entities.Trace]  # Complete trace with all spans and metadata  
    ) -> Union[int, float, bool, str, Feedback, List[Feedback]]:  
        # Your evaluation logic here  
    

For more flexibility than the `@scorer` decorator allows, you can instead define scorers using the `Scorer` class.

##  Inputsâ

Scorers receive the complete [MLflow trace](</aws/en/mlflow3/genai/tracing/tracing-101>) containing all spans, attributes, and outputs. As a convenience, MLflow also extracts commonly needed data and passes it as named arguments. All input arguments are optional, so declare only what your scorer needs:

  * `inputs`: The request sent to your app (e.g., user query, context).
  * `outputs`: The response from your app (e.g., generated text, tool calls)
  * `expectations`: Ground truth or labels (e.g., expected response, guidelines, etc.)
  * `trace`: The complete [MLflow trace](</aws/en/mlflow3/genai/tracing/tracing-101>) with all spans, allowing analysis of intermediate steps, latency, tool usage, and more. The trace is passed to the custom scorer as an instantiated [`mlflow.entities.trace` class](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>).



When running [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>), the `inputs`, `outputs`, and `expectations` parameters can be specified in the `data` argument, or parsed from the trace.

[Registered scorers for production monitoring](</aws/en/mlflow3/genai/eval-monitor/concepts/production-quality-monitoring>) always parse the `inputs` and `outputs` parameters from the trace. `expectations` is not available.

##  Outputsâ

Scorers can return different types of simple values or rich Feedback objects depending on your evaluation needs.

Return Type| MLflow UI Display| Use Case| `"yes"`/`"no"`| Pass/Fail| Binary evaluation| `True`/`False`| True/False| Boolean checks| `int`/`float`| Numeric value| Scores, counts| [`Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>)| Value + rationale| Detailed assessment| `List[`[`Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>)`]`| Multiple metrics| Multi-aspect evaluation  
---|---|---  
  
###  Simple valuesâ

Output primitive values for straightforward pass/fail or numeric assessments. Below are simple scorers for an AI app that returns a string as a response.

Python
    
    
    @scorer  
    def response_length(outputs: str) -> int:  
        # Return a numeric metric  
        return len(outputs.split())  
      
    @scorer  
    def contains_citation(outputs: str) -> str:  
        # Return pass/fail string  
        return "yes" if "[source]" in outputs else "no"  
    

###  Rich feedbackâ

Return a [`Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>) object or list of `Feedback` objects for detailed assessments with scores, rationales, and metadata.

Python
    
    
    from mlflow.entities import Feedback, AssessmentSource  
      
    @scorer  
    def content_quality(outputs):  
        return Feedback(  
            value=0.85,  # Can be numeric, boolean, string, or other types  
            rationale="Clear and accurate, minor grammar issues",  
            # Optional: source of the assessment. Several source types are supported,  
            # such as "HUMAN", "CODE", "LLM_JUDGE".  
            source=AssessmentSource(  
                source_type="HUMAN",  
                source_id="grammar_checker_v1"  
            ),  
            # Optional: additional metadata about the assessment.  
            metadata={  
                "annotator": "me@example.com",  
            }  
        )  
    

Multiple feedback objects can be returned as a list. Each feedback should have the `name` field specified, and those names will be displayed as separate metrics in the evaluation results.

Python
    
    
    @scorer  
    def comprehensive_check(inputs, outputs):  
        return [  
            Feedback(name="relevance", value=True, rationale="Directly addresses query"),  
            Feedback(name="tone", value="professional", rationale="Appropriate for audience"),  
            Feedback(name="length", value=150, rationale="Word count within limits")  
        ]  
    

##  Metric naming behaviorâ

As you define scorers, use clear, consistent names that indicate the scorer's purpose. These names will appear as metric names in your evaluation and monitoring results and dashboards. Follow MLflow naming conventions such as `safety_check` or `relevance_monitor`.

When you define scorers using either the [`@scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.scorer>) decorator or the `Scorer` class, the metric names in the [evaluation runs](</aws/en/mlflow3/genai/eval-monitor/concepts/evaluation-runs>) created by evaluation and monitoring follow simple rules:

  1. If the scorer returns one or more `Feedback` objects, then `Feedback.name` fields take precedence, if specified.
  2. For primitive return values or unnamed `Feedback`s, the function name (for the `@scorer` decorator) or the `Scorer.name` field (for the `Scorer` class) are used.



Expanding these rules to all possibilities gives the following table for metric naming behavior:

Return value| `@scorer` decorator behavior| `Scorer` class behavior| Primitive value (`int`, `float`, `str`)| Function name| `name` field| Feedback without name| Function name| `name` field| Feedback with name| `Feedback` name| `Feedback` name| `List[Feedback]` with names| `Feedback` names| `Feedback` names  
---|---|---  
  
For evaluation and monitoring, it is important that all metrics have distinct names. If a scorer returns `List[Feedback]`, then each `Feedback` in the `List` must have a distinct name.

See [examples of naming behavior](</aws/en/mlflow3/genai/eval-monitor/code-based-scorer-examples#naming-scorers>) in the tutorial.

## Access secrets in scorersâ

Custom scorers can access [Databricks secrets](</aws/en/security/secrets/>) to securely use API keys and credentials. This is useful when integrating external services, such as custom LLM endpoints that require authentication, like Azure OpenAI, AWS Bedrock, and others. This approach works for both [development evaluation](</aws/en/mlflow3/genai/eval-monitor/evaluate-app>) and [production monitoring](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>)

By default, `dbutils` isn't available in the scorer runtime environment. To access secrets in the scorer runtime environment call `from databricks.sdk.runtime import dbutils` from inside of the scorer function.

The following example show how to access a secret in a custom scorer:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import scorer, ScorerSamplingConfig  
    from mlflow.entities import Trace, Feedback  
      
    @scorer  
    def custom_llm_scorer(trace: Trace) -> Feedback:  
        # Explicitly import dbutils to access secrets  
        from databricks.sdk.runtime import dbutils  
      
        # Retrieve your API key from Databricks secrets  
        api_key = dbutils.secrets.get(scope='my-scope', key='api-key')  
      
        # Use the API key to call your custom LLM endpoint  
        # ... your custom evaluation logic here ...  
      
        return Feedback(  
            value="yes",  
            rationale="Evaluation completed using custom endpoint"  
        )  
      
    # Register and start the scorer  
    custom_llm_scorer.register()  
    custom_llm_scorer.start(sampling_config = ScorerSamplingConfig(sample_rate=1))  
    

## Error handlingâ

When a scorer encounters an error for a trace, MLflow can capture error details for that trace and then continue executing gracefully. For capturing error details, MLflow provides two approaches:

  * Let exceptions propagate (recommended) so that MLflow can capture error messages for you.
  * Handle exceptions explicitly.



### Let exceptions propagate (recommended)â

The simplest approach is to let exceptions throw naturally. MLflow automatically captures the exception and creates a [`Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>) object with the following error details:

  * `value`: `None`
  * `error`: The exception details, such as exception object, error message, and stack trace



The error information is displayed in the evaluation results. Open the corresponding row to see the error details.

### Handle exceptions explicitlyâ

For custom error handling or to provide specific error messages, catch exceptions and return a [`Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>) with `None` value and error details:

Python
    
    
    from mlflow.entities import AssessmentError, Feedback  
      
    @scorer  
    def is_valid_response(outputs):  
        import json  
      
        try:  
            data = json.loads(outputs)  
            required_fields = ["summary", "confidence", "sources"]  
            missing = [f for f in required_fields if f not in data]  
      
            if missing:  
                return Feedback(  
                    error=AssessmentError(  
                        error_code="MISSING_REQUIRED_FIELDS",  
                        error_message=f"Missing required fields: {missing}",  
                    ),  
                )  
      
            return Feedback(  
                value=True,  
                rationale="Valid JSON with all required fields"  
            )  
      
        except json.JSONDecodeError as e:  
            return Feedback(error=e)  # Can pass exception object directly to the error parameter  
    

The `error` parameter accepts:

  * **Python Exception** : Pass the exception object directly
  * **[`AssessmentError`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.AssessmentError>)** : For structured error reporting with error codes



##  Define scorers with the `Scorer` classâ

The `@scorer` decorator described above is simple and generally recommended, but when it is insufficient, you can instead use the [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) base class. Class-based definitions allow for more complex scorers, especially scorers that require state. The [`Scorer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.Scorer>) class is a [Pydantic object](<https://docs.pydantic.dev/latest/concepts/models/>), so you can define additional fields and use them in the `__call__` method.

You must define the `name` field to set the metric name. If you return a list of `Feedback` objects, then you must set the `name` field in each `Feedback` to avoid naming conflicts.

Python
    
    
    from mlflow.genai.scorers import Scorer  
    from mlflow.entities import Feedback  
    from typing import Optional  
      
    # Scorer class is a Pydantic object  
    class CustomScorer(Scorer):  
        # The `name` field is mandatory  
        name: str = "response_quality"  
        # Define additional fields  
        my_custom_field_1: int = 50  
        my_custom_field_2: Optional[list[str]] = None  
      
        # Override the __call__ method to implement the scorer logic  
        def __call__(self, outputs: str) -> Feedback:  
            # Your logic here  
            return Feedback(  
                value=True,  
                rationale="Response meets all quality criteria"  
            )  
    

### State managementâ

When writing scorers using the `Scorer` class, be aware of rules for managing state with Python classes. In particular, be sure to use instance attributes, not mutable class attributes. The example below illustrates mistakenly sharing state across scorer instances.

Python
    
    
    from mlflow.genai.scorers import Scorer  
    from mlflow.entities import Feedback  
      
    # WRONG: Don't use mutable class attributes  
    class BadScorer(Scorer):  
        results = []  # Shared across all instances!  
      
        name: str = "bad_scorer"  
      
        def __call__(self, outputs, **kwargs):  
            self.results.append(outputs)  # Causes issues  
            return Feedback(value=True)  
      
    # CORRECT: Use instance attributes  
    class GoodScorer(Scorer):  
        results: list[str] = None  
      
        name: str = "good_scorer"  
      
        def __init__(self):  
            self.results = []  # Per-instance state  
      
        def __call__(self, outputs, **kwargs):  
            self.results.append(outputs)  # Safe  
            return Feedback(value=True)  
    

## Next stepsâ

  * [Code-based scorer examples](</aws/en/mlflow3/genai/eval-monitor/code-based-scorer-examples>) \- See many examples of code-based scorers
  * [Develop code-based scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorer-dev-workflow>) \- Step through the development workflow for custom scorers
  * [Evaluate GenAI during development](</aws/en/mlflow3/genai/eval-monitor/concepts/eval-harness>) \- Understand how [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>) uses your scorers
  * [Monitor GenAI in production](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) \- Deploy your scorers for continuous monitoring



## API referencesâ

MLflow APIs used in this guide include:

  * [`@scorer` decorator](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.scorers.scorer>)
  * [`mlflow.entities.trace` class](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Trace>)
  * [`Feedback`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.entities.html#mlflow.entities.Feedback>)
  * [`mlflow.genai.evaluate()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate>)
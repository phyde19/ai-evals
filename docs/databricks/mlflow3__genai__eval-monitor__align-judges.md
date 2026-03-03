<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges -->

On this page

Last updated on **Nov 11, 2025**

# Align judges with humans

Judge alignment teaches LLM judges to match human evaluation standards through systematic feedback. This process transforms generic evaluators into domain-specific experts that understand your unique quality criteria, improving agreement with human assessments by 30 to 50 percent compared to baseline judges.

Judge alignment follows a three-step workflow:

  1. **Generate initial assessments** : Create a judge and evaluate traces to establish a baseline
  2. **Collect human feedback** : Domain experts review and correct judge assessments
  3. **Align and deploy** : Use the SIMBA optimizer to improve the judge based on human feedback



The system uses Simplified Multi-Bootstrap Aggregation (SIMBA) as the default optimization strategy, leveraging DSPy's implementation to iteratively refine judge instructions.

## Requirementsâ

  * MLflow 3.4.0 or above to use judge alignment features

Python
        
        %pip install --upgrade "mlflow[databricks]>=3.4.0"  
        dbutils.library.restartPython()  
        

  * Have created a judge using [`make_judge()`](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>)

  * The human feedback assessment name must exactly match the judge name. For example, if your judge is named `product_quality`, your human feedback must use the same name `product_quality`.

  * Alignment works with judges created using `make_judge()` with template-based evaluation.




## Step 1: Create judge and generate tracesâ

Create an initial judge and generate traces with assessments. You need at least 10 traces, but 50-100 traces provide better alignment results.

Python
    
    
    from mlflow.genai.judges import make_judge  
    import mlflow  
      
    # Create an MLflow experiment for alignment  
    experiment_id = mlflow.create_experiment("product-quality-alignment")  
    mlflow.set_experiment(experiment_id=experiment_id)  
      
    # Create initial judge with template-based evaluation  
    initial_judge = make_judge(  
        name="product_quality",  
        instructions=(  
            "Evaluate if the product description in {{ outputs }} "  
            "is accurate and helpful for the query in {{ inputs }}. "  
            "Rate as: excellent, good, fair, or poor"  
        ),  
        model="databricks:/databricks-gpt-oss-120b",  
    )  
    

Generate traces and run the judge:

Python
    
    
    # Generate traces for alignment (minimum 10, recommended 50+)  
    traces = []  
    for i in range(50):  
        with mlflow.start_span(f"product_description_{i}") as span:  
            # Your application logic here  
            query = f"Tell me about product {i}"  
            description = generate_product_description(query)  # Replace with your application logic  
      
            # Log inputs and outputs  
            span.set_inputs({"query": query})  
            span.set_outputs({"description": description})  
            traces.append(span.trace_id)  
      
    # Run initial judge on all traces  
    for trace_id in traces:  
        trace = mlflow.get_trace(trace_id)  
        inputs = trace.data.spans[0].inputs  
        outputs = trace.data.spans[0].outputs  
      
        # Generate judge assessment  
        judge_result = initial_judge(inputs=inputs, outputs=outputs)  
      
        # Log judge feedback to the trace  
        mlflow.log_feedback(  
            trace_id=trace_id,  
            name="product_quality",  
            value=judge_result.value,  
            rationale=judge_result.rationale,  
        )  
    

## Step 2: Collect human feedbackâ

Collect human feedback to teach the judge your quality standards. Choose from the following approaches:

  * Databricks UI review
  * Programmatic feedback



Collect human feedback when:

  * You need domain experts to review outputs
  * You want to iteratively refine feedback criteria
  * You're working with a smaller dataset (< 100 examples)



Use the MLflow UI to manually review and provide feedback:

  1. Navigate to your MLflow experiment in the Databricks workspace
  2. Click on the **Evaluation** tab to see traces
  3. Review each trace and its judge assessment
  4. Add human feedback using the UI's feedback interface
  5. Ensure the feedback name matches your judge name exactly ("product_quality")



Use programmatic feedback when:

  * You have pre-existing ground truth labels
  * You're working with large datasets (100+ examples)
  * You need reproducible feedback collection



If you have existing ground truth labels, log them programmatically:

Python
    
    
    from mlflow.entities import AssessmentSource, AssessmentSourceType  
      
    # Your ground truth data  
    ground_truth_data = [  
        {"trace_id": traces[0], "label": "excellent", "rationale": "Comprehensive and accurate description"},  
        {"trace_id": traces[1], "label": "poor", "rationale": "Missing key product features"},  
        {"trace_id": traces[2], "label": "good", "rationale": "Accurate but could be more detailed"},  
        # ... more ground truth labels  
    ]  
      
    # Log human feedback for each trace  
    for item in ground_truth_data:  
        mlflow.log_feedback(  
            trace_id=item["trace_id"],  
            name="product_quality",  # Must match judge name  
            value=item["label"],  
            rationale=item.get("rationale", ""),  
            source=AssessmentSource(  
                source_type=AssessmentSourceType.HUMAN,  
                source_id="ground_truth_dataset"  
            ),  
        )  
    

### Best practices for feedback collectionâ

  * **Diverse reviewers** : Include multiple domain experts to capture varied perspectives
  * **Balanced examples** : Include at least 30% negative examples (poor/fair ratings)
  * **Clear rationales** : Provide detailed explanations for ratings
  * **Representative samples** : Cover edge cases and common scenarios



## Step 3: Align and register the judgeâ

Once you have sufficient human feedback, align the judge:

  * Default optimizer (recommended)
  * Explicit optimizer



MLflow provides the default alignment optimizer using DSPy's implementation of SIMBA (Simplified Multi-Bootstrap Aggregation). When you call [`align()`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.Judge.align>) without specifying an optimizer, the SIMBA optimizer is used automatically:

Python
    
    
    from mlflow.genai.judges.optimizers import SIMBAAlignmentOptimizer  
      
    # Retrieve traces with both judge and human assessments  
    traces_for_alignment = mlflow.search_traces(  
        experiment_ids=[experiment_id],  
        max_results=100,  
        return_type="list"  
    )  
      
    # Filter for traces with both judge and human feedback  
    # Only traces with both assessments can be used for alignment  
    valid_traces = []  
    for trace in traces_for_alignment:  
        feedbacks = trace.search_assessments(name="product_quality")  
        has_judge = any(f.source.source_type == "LLM_JUDGE" for f in feedbacks)  
        has_human = any(f.source.source_type == "HUMAN" for f in feedbacks)  
        if has_judge and has_human:  
            valid_traces.append(trace)  
      
    if len(valid_traces) >= 10:  
        # Create SIMBA optimizer with Databricks model  
        optimizer = SIMBAAlignmentOptimizer(  
            model="databricks:/databricks-gpt-oss-120b"  
        )  
      
        # Align the judge based on human feedback  
        aligned_judge = initial_judge.align(optimizer, valid_traces)  
      
        # Register the aligned judge for production use  
        aligned_judge.register(  
            experiment_id=experiment_id,  
            name="product_quality_aligned",  
            tags={"alignment_date": "2025-10-23", "num_traces": str(len(valid_traces))}  
        )  
      
        print(f"Successfully aligned judge using {len(valid_traces)} traces")  
    else:  
        print(f"Insufficient traces for alignment. Found {len(valid_traces)}, need at least 10")  
    

Python
    
    
    from mlflow.genai.judges.optimizers import SIMBAAlignmentOptimizer  
      
    # Retrieve traces with both judge and human assessments  
    traces_for_alignment = mlflow.search_traces(  
        experiment_ids=[experiment_id], max_results=15, return_type="list"  
    )  
      
    # Align the judge using human corrections (minimum 10 traces recommended)  
    if len(traces_for_alignment) >= 10:  
        # Explicitly specify SIMBA with custom model configuration  
        optimizer = SIMBAAlignmentOptimizer(model="databricks:/databricks-gpt-oss-120b")  
        aligned_judge = initial_judge.align(optimizer, traces_for_alignment)  
      
        # Register the aligned judge  
        aligned_judge.register(experiment_id=experiment_id)  
        print("Judge aligned successfully with human feedback")  
    else:  
        print(f"Need at least 10 traces for alignment, have {len(traces_for_alignment)}")  
    

## Enable detailed loggingâ

To monitor the alignment process, enable debug logging for the SIMBA optimizer:

Python
    
    
    import logging  
      
    # Enable detailed SIMBA logging  
    logging.getLogger("mlflow.genai.judges.optimizers.simba").setLevel(logging.DEBUG)  
      
    # Run alignment with verbose output  
    aligned_judge = initial_judge.align(optimizer, valid_traces)  
    

## Validate alignmentâ

Validate that alignment improved the judge:

Python
    
    
      
    def test_alignment_improvement(  
        original_judge, aligned_judge, test_traces: list  
    ) -> dict:  
        """Compare judge performance before and after alignment."""  
      
        original_correct = 0  
        aligned_correct = 0  
      
        for trace in test_traces:  
            # Get human ground truth from trace assessments  
            feedbacks = trace.search_assessments(type="feedback")  
            human_feedback = next(  
                (f for f in feedbacks if f.source.source_type == "HUMAN"), None  
            )  
      
            if not human_feedback:  
                continue  
      
            # Get judge evaluations  
            # Judges can evaluate entire traces instead of individual inputs/outputs  
            original_eval = original_judge(trace=trace)  
            aligned_eval = aligned_judge(trace=trace)  
      
            # Check agreement with human  
            if original_eval.value == human_feedback.value:  
                original_correct += 1  
            if aligned_eval.value == human_feedback.value:  
                aligned_correct += 1  
      
        total = len(test_traces)  
        return {  
            "original_accuracy": original_correct / total,  
            "aligned_accuracy": aligned_correct / total,  
            "improvement": (aligned_correct - original_correct) / total,  
        }  
      
      
    

## Create custom alignment optimizersâ

For specialized alignment strategies, extend the [`AlignmentOptimizer`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.judges.base.AlignmentOptimizer>) base class:

Python
    
    
    from mlflow.genai.judges.base import AlignmentOptimizer, Judge  
    from mlflow.entities.trace import Trace  
      
    class MyCustomOptimizer(AlignmentOptimizer):  
        """Custom optimizer implementation for judge alignment."""  
      
        def __init__(self, model: str = None, **kwargs):  
            """Initialize your optimizer with custom parameters."""  
            self.model = model  
            # Add any custom initialization logic  
      
        def align(self, judge: Judge, traces: list[Trace]) -> Judge:  
            """  
            Implement your alignment algorithm.  
      
            Args:  
                judge: The judge to be optimized  
                traces: List of traces containing human feedback  
      
            Returns:  
                A new Judge instance with improved alignment  
            """  
            # Your custom alignment logic here  
            # 1. Extract feedback from traces  
            # 2. Analyze disagreements between judge and human  
            # 3. Generate improved instructions  
            # 4. Return new judge with better alignment  
      
            # Example: Return judge with modified instructions  
            from mlflow.genai.judges import make_judge  
      
            improved_instructions = self._optimize_instructions(judge.instructions, traces)  
      
            return make_judge(  
                name=judge.name,  
                instructions=improved_instructions,  
                model=judge.model,  
            )  
      
        def _optimize_instructions(self, instructions: str, traces: list[Trace]) -> str:  
            """Your custom optimization logic."""  
            # Implement your optimization strategy  
            pass  
      
    # Create your custom optimizer  
    custom_optimizer = MyCustomOptimizer(model="your-model")  
      
    # Use it for alignment  
    aligned_judge = initial_judge.align(traces_with_feedback, custom_optimizer)  
    

## Limitationsâ

  * Judge alignment does not support agent-based or expectation-based evaluation.



## Next stepsâ

  * Learn about [production monitoring](</aws/en/mlflow3/genai/eval-monitor/production-monitoring>) to deploy aligned judges at scale
  * See [code-based scorers](</aws/en/mlflow3/genai/eval-monitor/custom-scorers>) for complementary deterministic metrics
  * Learn more about building customized judges in [this Databricks blog](<https://www.databricks.com/blog/building-custom-llm-judges-ai-agent-accuracy>)
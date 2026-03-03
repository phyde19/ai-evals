<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/evaluate-conversations -->

On this page

Last updated on **Feb 12, 2026**

# Evaluate conversations

Conversation evaluation enables you to assess entire conversation sessions rather than individual turns. This is essential for evaluating conversational AI systems where quality emerges over multiple interactions, such as user frustration patterns, conversation completeness, or overall dialogue coherence.

note

Multi-turn evaluation is [experimental](</aws/en/release-notes/release-types>). The API and behavior might change in future releases.

## Prerequisitesâ

Install MLflow 3.10.0 or later:

Bash
    
    
    pip install --upgrade 'mlflow[databricks]>=3.10'  
    

Your agent must be instrumented to track session IDs on traces. See [Track users and sessions](<https://mlflow.org/docs/latest/genai/tracing/track-users-sessions/>) for how to set session IDs on your traces.

## Two approachesâ

MLflow supports two approaches for evaluating conversations:

  * **Evaluate pre-generated conversations** : Evaluate existing conversations that have already been traced. Use this approach when you have:

    * Production conversation data to analyze
    * Pre-recorded test conversations from QA or user studies
    * Conversations from a previous agent version for comparison
  * **Simulate conversations during evaluation** : Generate new conversations by simulating user interactions with your agent. Use this approach when you want to:

    * Test a new agent version systematically with consistent scenarios
    * Generate diverse test scenarios at scale
    * Stress-test your agent with specific user behaviors and edge cases



## Overviewâ

Traditional single-turn evaluation assesses each agent response independently. However, conversational agents require evaluation at the session level to capture:

  * **User frustration** : Did the user become frustrated? Was it resolved?
  * **Conversation completeness** : Were all user questions answered by the end of the conversation?
  * **Knowledge retention** : Does the agent remember information from earlier in the conversation?
  * **Dialogue coherence** : Does the conversation flow naturally?



Multi-turn evaluation addresses these needs by grouping traces into conversation sessions and applying judges that analyze the entire conversation history.

## Evaluate pre-generated conversationsâ

Evaluate conversations that have already been traced. This is useful for evaluating production data or pre-recorded test conversations.

### Step 1: Tag traces with session IDsâ

When building your agent, set session IDs on traces to group them into conversations:

Python
    
    
    import mlflow  
      
    @mlflow.trace  
    def my_chatbot(question, session_id):  
        mlflow.update_current_trace(  
            tags={"mlflow.trace.session": session_id}  
        )  
        # ... your chatbot logic  
    

For complete documentation on tracking sessions, see [Track users and sessions](<https://mlflow.org/docs/latest/genai/tracing/track-users-sessions/>).

### Step 2: Retrieve and evaluate sessionsâ

Get traces from your experiment and pass them to `mlflow.genai.evaluate`. MLflow automatically groups traces by session ID:

Python
    
    
    from mlflow.genai.scorers import ConversationCompleteness, UserFrustration  
      
    # Get traces from your experiment  
    traces = mlflow.search_traces(  
        filter_string="attributes.status = 'OK'",  
        return_type="list",  
    )  
      
    # Evaluate the conversations  
    # MLflow automatically groups traces by their session ID tag  
    results = mlflow.genai.evaluate(  
        data=traces,  
        scorers=[  
            ConversationCompleteness(),  # Did the agent answer all questions?  
            UserFrustration(),           # Did the user become frustrated?  
        ],  
    )  
    

You can also retrieve complete sessions directly using `mlflow.search_sessions`:

Python
    
    
    import mlflow  
      
    # Get complete sessions (each session is a list of traces)  
    sessions = mlflow.search_sessions(  
        locations=["<your-experiment-id>"],  
        max_results=50,  
    )  
      
    # Flatten for evaluation  
    all_traces = [trace for session in sessions for trace in session]  
      
    results = mlflow.genai.evaluate(  
        data=all_traces,  
        scorers=[ConversationCompleteness(), UserFrustration()],  
    )  
    

## Simulate conversations during evaluationâ

Generate new conversations by simulating user interactions. This enables testing different agent versions with consistent goals and personas.

Python
    
    
    import mlflow  
    from mlflow.genai.simulators import ConversationSimulator  
    from mlflow.genai.scorers import ConversationCompleteness, Safety  
      
    # Define test scenarios  
    simulator = ConversationSimulator(  
        test_cases=[  
            {"goal": "Successfully set up experiment tracking"},  
            {"goal": "Identify the root cause of a deployment error"},  
            {  
                "goal": "Understand how to implement model versioning",  
                "persona": "You are a beginner who needs detailed explanations",  
            },  
        ],  
        max_turns=5,  
    )  
      
      
    # Your agent's predict function  
    def predict_fn(input: list[dict], **kwargs) -> str:  
        # input is the conversation history  
        response = your_agent.chat(input)  
        return response  
      
      
    # Simulate conversations and evaluate  
    results = mlflow.genai.evaluate(  
        data=simulator,  
        predict_fn=predict_fn,  
        scorers=[  
            ConversationCompleteness(),  
            Safety(),  
        ],  
    )  
    

For complete documentation on conversation simulation, including test case definition, predict function interfaces, and configuration options, see [Conversation simulation](</aws/en/mlflow3/genai/eval-monitor/conversation-simulation>).

## Multi-turn judgesâ

### Built-in judgesâ

MLflow provides built-in multi-turn judges for evaluating conversation quality. For the complete list and detailed documentation, see the [MLflow predefined scorers documentation](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/#multi-turn>) and the [Scorers and LLM judges](</aws/en/mlflow3/genai/eval-monitor/concepts/scorers#multi-turn-judges>) page.

### Custom judgesâ

Create custom multi-turn judges using [`make_judge`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.make_judge>). Use the `{{ conversation }}` template variable to access the full conversation history:

Python
    
    
    from mlflow.genai.judges import make_judge  
    from typing import Literal  
      
    # Create a custom multi-turn judge  
    politeness_judge = make_judge(  
        name="politeness",  
        judge_prompt=(  
            "Evaluate whether the assistant maintained a polite and professional "  
            "tone throughout this conversation:\n\n{{ conversation }}\n\n"  
            "Rate as 'consistently_polite', 'mostly_polite', or 'impolite'."  
        ),  
        feedback_value_type=Literal["consistently_polite", "mostly_polite", "impolite"],  
    )  
      
    # Get traces from your experiment  
    traces = mlflow.search_traces(  
        filter_string="attributes.status = 'OK'",  
        return_type="list",  
    )  
      
    # Use in evaluation  
    results = mlflow.genai.evaluate(  
        data=traces,  
        scorers=[politeness_judge],  
    )  
    

The `{{ conversation }}` variable injects the complete conversation history in a readable format for the judge to analyze.

note

The `{{ conversation }}` variable can only be used with `{{ expectations }}`, not with `{{ inputs }}`, `{{ outputs }}`, or `{{ trace }}`.

## How assessments are storedâ

Multi-turn assessments are stored on the **first trace** (chronologically) in each session. This design ensures:

  * Assessments remain stable even as new turns are added to a conversation
  * You can easily find conversation-level assessments by looking at session start traces
  * The Sessions UI can efficiently display conversation metrics



Assessments include metadata identifying them as conversation-level:

  * `session_id`: The session ID linking the assessment to the full conversation



## Working with specific sessionsâ

To evaluate a specific session, use `mlflow.search_traces` with a filter string:

Python
    
    
    import mlflow  
    from mlflow.genai.scorers import ConversationCompleteness, UserFrustration  
      
    # Get traces for a specific session using filter  
    traces = mlflow.search_traces(  
        filter_string="tags.`mlflow.trace.session` = '<your-session-id>'",  
        return_type="list",  
    )  
      
    # Evaluate the session  
    results = mlflow.genai.evaluate(  
        data=traces,  
        scorers=[ConversationCompleteness(), UserFrustration()],  
    )  
    

## Next stepsâ

  * [Conversation Simulation](</aws/en/mlflow3/genai/eval-monitor/conversation-simulation>) \- Generate synthetic conversations to test your agent with diverse scenarios and user behaviors.
  * [Predefined scorers](<https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/>) \- Complete reference for all built-in single-turn and multi-turn scorers.
  * [Custom judges](</aws/en/mlflow3/genai/eval-monitor/custom-judge/>) \- Build custom LLM judges using `make_judge` to evaluate conversation-specific criteria.
  * [Track users and sessions](<https://mlflow.org/docs/latest/genai/tracing/track-users-sessions/>) \- Learn how to instrument your agent with session IDs.
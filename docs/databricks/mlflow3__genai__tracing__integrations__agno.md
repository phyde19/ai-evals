<!-- source: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/integrations/agno -->

On this page

Last updated on **Aug 18, 2025**

# Tracing Agno

[Agno](<https://github.com/agno-agi/agno>) is an open source framework for building agentic applications. It focuses on composing tools and policies into task-oriented agents.

[MLflow Tracing](</aws/en/mlflow3/genai/tracing/>) integrates with Agno to capture comprehensive traces of agentic workflows and tool compositions. Enable it with [`mlflow.agno.autolog`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.agno.html#mlflow.agno.autolog>). The integration provides end-to-end visibility into:

  * Prompts and completion responses
  * Latencies
  * Metadata about the different Agents, such as function names
  * Token usages and cost
  * Cache hit
  * Any exception if raised



note

On serverless compute clusters, autologging is not automatically enabled. You must explicitly call `mlflow.agno.autolog()` to enable automatic tracing for this integration.

## Prerequisitesâ

To use MLflow Tracing with Agno, you need to install MLflow and the relevant Agno packages.

  * Development
  * Production



For development environments, install the full MLflow package with Databricks extras and Agno:

Bash
    
    
    pip install --upgrade "mlflow[databricks]>=3.1" agno openai  
    

The full `mlflow[databricks]` package includes all features for local development and experimentation on Databricks.

For production deployments, install `mlflow-tracing` and Agno:

Bash
    
    
    pip install --upgrade mlflow-tracing agno openai  
    

The `mlflow-tracing` package is optimized for production use.

note

MLflow 3 is recommended for the best tracing experience.

Before running the examples, you'll need to configure your environment:

**For users outside Databricks notebooks** : Set your Databricks environment variables:

Bash
    
    
    export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"  
    export DATABRICKS_TOKEN="your-personal-access-token"  
    

**For users inside Databricks notebooks** : These credentials are automatically set for you.

## Basic exampleâ

Python
    
    
    import mlflow  
      
    mlflow.agno.autolog()  
      
    from agno.agent import Agent  
    from agno.models.anthropic import Claude  
    from agno.tools.yfinance import YFinanceTools  
      
    agent = Agent(  
        model=Claude(id="claude-sonnet-4-20250514"),  
        tools=[YFinanceTools(stock_price=True)],  
        instructions="Use tables to display data. Don't include any other text.",  
        markdown=True,  
    )  
    agent.print_response("What is the stock price of Apple?", stream=False)  
    

Run your Agno agents as usual. Traces will appear in the experiment UI.

## Multi-agent exampleâ

Python
    
    
    import mlflow  
      
    from agno.agent import Agent  
    from agno.models.anthropic import Claude  
    from agno.models.openai import OpenAIChat  
    from agno.team.team import Team  
    from agno.tools.duckduckgo import DuckDuckGoTools  
    from agno.tools.reasoning import ReasoningTools  
    from agno.tools.yfinance import YFinanceTools  
      
    # Enable auto tracing for Agno  
    mlflow.agno.autolog()  
      
      
    web_agent = Agent(  
        name="Web Search Agent",  
        role="Handle web search requests and general research",  
        model=OpenAIChat(id="gpt-4.1"),  
        tools=[DuckDuckGoTools()],  
        instructions="Always include sources",  
        add_datetime_to_instructions=True,  
    )  
      
    finance_agent = Agent(  
        name="Finance Agent",  
        role="Handle financial data requests and market analysis",  
        model=OpenAIChat(id="gpt-4.1"),  
        tools=[  
            YFinanceTools(  
                stock_price=True,  
                stock_fundamentals=True,  
                analyst_recommendations=True,  
                company_info=True,  
            )  
        ],  
        instructions=[  
            "Use tables to display stock prices, fundamentals (P/E, Market Cap), and recommendations.",  
            "Clearly state the company name and ticker symbol.",  
            "Focus on delivering actionable financial insights.",  
        ],  
        add_datetime_to_instructions=True,  
    )  
      
    reasoning_finance_team = Team(  
        name="Reasoning Finance Team",  
        mode="coordinate",  
        model=Claude(id="claude-sonnet-4-20250514"),  
        members=[web_agent, finance_agent],  
        tools=[ReasoningTools(add_instructions=True)],  
        instructions=[  
            "Collaborate to provide comprehensive financial and investment insights",  
            "Consider both fundamental analysis and market sentiment",  
            "Use tables and charts to display data clearly and professionally",  
            "Present findings in a structured, easy-to-follow format",  
            "Only output the final consolidated analysis, not individual agent responses",  
        ],  
        markdown=True,  
        show_members_responses=True,  
        enable_agentic_context=True,  
        add_datetime_to_instructions=True,  
        success_criteria="The team has provided a complete financial analysis with data, visualizations, risk assessment, and actionable investment recommendations supported by quantitative analysis and market research.",  
    )  
      
    reasoning_finance_team.print_response(  
        """Compare the tech sector giants (AAPL, GOOGL, MSFT) performance:  
        1. Get financial data for all three companies  
        2. Analyze recent news affecting the tech sector  
        3. Calculate comparative metrics and correlations  
        4. Recommend portfolio allocation weights""",  
        show_full_reasoning=True,  
    )  
    

## Token usage trackingâ

MLflow logs token usage for each Agent callto the `mlflow.chat.tokenUsage` attribute. The total token usage throughout the trace is available in the `token_usage` field of the trace info object.

Python
    
    
    # Get the trace object just created  
    last_trace_id = mlflow.get_last_active_trace_id()  
    trace = mlflow.get_trace(trace_id=last_trace_id)  
      
    # Print the token usage  
    total_usage = trace.info.token_usage  
    print("== Total token usage: ==")  
    print(f"  Input tokens: {total_usage['input_tokens']}")  
    print(f"  Output tokens: {total_usage['output_tokens']}")  
    print(f"  Total tokens: {total_usage['total_tokens']}")  
      
    # Print the token usage for each LLM call  
    print("\n== Detailed usage for each LLM call: ==")  
    for span in trace.data.spans:  
        if usage := span.get_attribute("mlflow.chat.tokenUsage"):  
            print(f"{span.name}:")  
            print(f"  Input tokens: {usage['input_tokens']}")  
            print(f"  Output tokens: {usage['output_tokens']}")  
            print(f"  Total tokens: {usage['total_tokens']}")  
    

## Disable auto-tracingâ

Disable with [`mlflow.agno.autolog(disable=True)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.agno.html#mlflow.agno.autolog>) or globally with [`mlflow.autolog(disable=True)`](<https://mlflow.org/docs/latest/api_reference/python_api/mlflow.html#mlflow.autolog>).
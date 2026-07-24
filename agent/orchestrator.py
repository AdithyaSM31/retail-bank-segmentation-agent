"""
Agent Orchestrator — LangGraph ReAct agent that orchestrates all tools
to answer user queries about customer segmentation and banking analytics.
"""
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from agent.prompts import SYSTEM_PROMPT
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE

# Import all tools
from tools.eda_tool import (
    run_full_eda,
    get_column_distribution,
    get_correlation_analysis,
    filter_and_aggregate,
    get_missing_value_report,
)
from tools.feature_engineering_tool import (
    engineer_customer_features,
    select_features_for_segmentation,
    scale_features,
)
from tools.segmentation_tool import (
    segment_customers_rule_based,
    segment_customers_ml,
    get_optimal_clusters,
    get_segment_statistics,
)
from tools.explainability_tool import (
    explain_segment,
    explain_customer_segment,
    compare_segments,
    get_feature_importance_for_segments,
)
from tools.recommendation_tool import (
    recommend_products_for_segment,
    identify_upgrade_candidates,
    get_retention_strategies,
)
from tools.visualization_tool import (
    plot_segment_distribution,
    plot_feature_comparison,
    plot_cluster_scatter,
    plot_segment_radar,
    plot_correlation_heatmap,
)
from tools.data_export_tool import (
    export_segments_to_csv,
    export_segment_report,
    query_segment_data,
)


# All available tools
ALL_TOOLS = [
    # Feature Engineering
    engineer_customer_features,
    # Segmentation
    segment_customers_rule_based,
    segment_customers_ml,
    # Explainability
    explain_segment,
    get_feature_importance_for_segments,
    # Recommendations
    recommend_products_for_segment,
    # Visualization
    plot_segment_distribution,
    plot_feature_comparison,
    # Data Export
    export_segments_to_csv,
]


def create_agent():
    """Create and return the LangGraph ReAct agent with all tools."""
    llm = ChatGroq(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY,
        temperature=LLM_TEMPERATURE,
    )

    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    return agent


def run_agent_query(agent, user_message: str, history: list = None) -> dict:
    """
    Run a user query through the agent and return the response.
    
    Args:
        agent: The LangGraph agent instance
        user_message: The user's natural language query
        history: Optional list of previous messages for context
        
    Returns:
        dict with 'response' (str) and 'charts' (list of chart JSON strings)
    """
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    result = agent.invoke({"messages": messages})

    # Extract the final response
    final_messages = result.get("messages", [])
    
    response_text = ""
    charts = []

    for msg in final_messages:
        if hasattr(msg, "content") and hasattr(msg, "type"):
            if msg.type == "ai" and msg.content:
                response_text = msg.content
            elif msg.type == "tool" and msg.content:
                # Check if this is a chart response
                content = msg.content
                if isinstance(content, str) and '"chart_json"' in content:
                    charts.append(content)

    return {
        "response": response_text,
        "charts": charts,
        "all_messages": final_messages,
    }

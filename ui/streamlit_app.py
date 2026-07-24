"""
Streamlit Frontend — Premium dark-themed chat interface for the Banking Analytics Agent.
Supports real-time chat, interactive Plotly charts, and CSV downloads.
"""
import streamlit as st
import json
import os
import sys
import plotly.io as pio

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import create_agent, run_agent_query
from config import OUTPUT_DIR

# --- Page Config ---
st.set_page_config(
    page_title="Banking Analytics Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Premium Dark Theme CSS ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.7);
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
    }
    .stat-card .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #7c83ff;
        margin: 0;
    }
    .stat-card .stat-label {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0.3rem 0 0 0;
    }
    
    /* Chat Messages */
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Sidebar */
    .sidebar-section {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .sidebar-section h3 {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: rgba(255,255,255,0.4);
        margin-bottom: 0.8rem;
    }
    
    /* Tool Badge */
    .tool-badge {
        display: inline-block;
        background: rgba(124, 131, 255, 0.15);
        color: #7c83ff;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.15rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124, 131, 255, 0.3);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_loading" not in st.session_state:
    st.session_state.agent_loading = False
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False


def init_agent():
    """Initialize the agent (cached in session state)."""
    if st.session_state.agent is None:
        st.session_state.agent = create_agent()
    return st.session_state.agent


def load_data_stats():
    """Load dataset statistics for the sidebar."""
    try:
        from data_loader import get_data_summary
        return get_data_summary()
    except Exception:
        return None


# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <span style="font-size: 2.5rem;">🏦</span>
        <h2 style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 600;">Analytics Agent</h2>
        <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Customer Segmentation & Insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown('<div class="sidebar-section"><h3>⚡ Quick Actions</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Run EDA", use_container_width=True, key="btn_eda"):
            st.session_state.quick_action = "Run a comprehensive exploratory data analysis on the dataset"
    with col2:
        if st.button("👥 Segment", use_container_width=True, key="btn_seg"):
            st.session_state.quick_action = "Segment customers into Priority, Regular, and Dormant based on balance and transaction frequency"
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("💡 Explain", use_container_width=True, key="btn_explain"):
            st.session_state.quick_action = "Explain the characteristics of each customer segment"
    with col4:
        if st.button("🎯 Recommend", use_container_width=True, key="btn_rec"):
            st.session_state.quick_action = "Recommend products for each customer segment"

    col5, col6 = st.columns(2)
    with col5:
        if st.button("📈 Visualize", use_container_width=True, key="btn_viz"):
            st.session_state.quick_action = "Create visualizations showing segment distribution and profiles"
    with col6:
        if st.button("📥 Export", use_container_width=True, key="btn_export"):
            st.session_state.quick_action = "Export the customer segments to CSV"

    st.divider()

    # Dataset Info
    stats = load_data_stats()
    if stats:
        st.markdown('<div class="sidebar-section"><h3>📋 Dataset Info</h3></div>', unsafe_allow_html=True)
        st.metric("Transactions", f"{stats['total_transactions']:,}")
        st.metric("Customers", f"{stats['unique_customers']:,}")
        st.metric("Date Range", stats['date_range'][:21])
        st.session_state.data_loaded = True

    st.divider()

    # Download Section
    st.markdown('<div class="sidebar-section"><h3>📥 Downloads</h3></div>', unsafe_allow_html=True)
    
    segments_path = OUTPUT_DIR / "customer_segments.csv"
    if segments_path.exists():
        with open(segments_path, "rb") as f:
            st.download_button(
                "⬇️ Download Segments CSV",
                data=f.read(),
                file_name="customer_segments.csv",
                mime="text/csv",
                use_container_width=True,
            )
    
    report_path = OUTPUT_DIR / "segmentation_report.md"
    if report_path.exists():
        with open(report_path, "rb") as f:
            st.download_button(
                "⬇️ Download Report",
                data=f.read(),
                file_name="segmentation_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

    st.divider()
    
    # Tools info
    st.markdown('<div class="sidebar-section"><h3>🛠️ Available Tools</h3></div>', unsafe_allow_html=True)
    tools_list = [
        "EDA Analysis", "Feature Engineering", "Rule-based Segmentation",
        "ML Clustering (KMeans)", "Explainability", "Product Recommendations",
        "Upgrade Candidates", "Retention Strategies", "Visualizations",
        "Data Export", "Segment Comparison"
    ]
    tool_html = " ".join(f'<span class="tool-badge">{t}</span>' for t in tools_list)
    st.markdown(tool_html, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --- Main Content ---
st.markdown("""
<div class="main-header">
    <h1>🏦 Customer Segmentation & Personalization Agent</h1>
    <p>AI-powered analytics agent for retail banking — Ask questions in natural language</p>
</div>
""", unsafe_allow_html=True)

# Stats Row
if stats:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value">{stats['total_transactions']:,}</p>
            <p class="stat-label">Transactions</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value">{stats['unique_customers']:,}</p>
            <p class="stat-label">Customers</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value">25</p>
            <p class="stat-label">AI Tools</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="stat-card">
            <p class="stat-value">Gemini</p>
            <p class="stat-label">LLM Engine</p>
        </div>""", unsafe_allow_html=True)

st.markdown("")

# --- Chat Interface ---
# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
        # Render charts if present
        if "charts" in msg and msg["charts"]:
            for chart_json_str in msg["charts"]:
                try:
                    chart_data = json.loads(chart_json_str)
                    if "chart_json" in chart_data:
                        fig = pio.from_json(chart_data["chart_json"])
                        st.plotly_chart(fig, use_container_width=True)
                except (json.JSONDecodeError, Exception):
                    pass

# Handle quick actions
if "quick_action" in st.session_state and st.session_state.quick_action:
    prompt = st.session_state.quick_action
    st.session_state.quick_action = None
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔄 Agent is analyzing... (this may take a moment for the first query)"):
            try:
                agent = init_agent()
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                result = run_agent_query(agent, prompt, history)
                
                st.markdown(result["response"])
                
                # Render charts
                for chart_json_str in result.get("charts", []):
                    try:
                        chart_data = json.loads(chart_json_str)
                        if "chart_json" in chart_data:
                            fig = pio.from_json(chart_data["chart_json"])
                            st.plotly_chart(fig, use_container_width=True)
                    except (json.JSONDecodeError, Exception):
                        pass
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "charts": result.get("charts", []),
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask me anything about your customers... (e.g., 'Segment customers into priority, regular and dormant')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔄 Agent is analyzing... (this may take a moment for the first query)"):
            try:
                agent = init_agent()
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                result = run_agent_query(agent, prompt, history)
                
                st.markdown(result["response"])
                
                # Render charts
                for chart_json_str in result.get("charts", []):
                    try:
                        chart_data = json.loads(chart_json_str)
                        if "chart_json" in chart_data:
                            fig = pio.from_json(chart_data["chart_json"])
                            st.plotly_chart(fig, use_container_width=True)
                    except (json.JSONDecodeError, Exception):
                        pass
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "charts": result.get("charts", []),
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

# Welcome message if no chat history
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; opacity: 0.7;">
        <p style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</p>
        <h3 style="font-weight: 600; margin-bottom: 0.5rem;">Welcome to the Banking Analytics Agent</h3>
        <p style="color: rgba(255,255,255,0.5); max-width: 600px; margin: 0 auto;">
            I can help you analyze customer data, segment customers, explain segments, 
            recommend products, and generate visualizations. Try one of the quick actions 
            in the sidebar or type your question below.
        </p>
        <div style="margin-top: 1.5rem; display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem;">
            <span class="tool-badge">📊 "Run EDA on the dataset"</span>
            <span class="tool-badge">👥 "Segment customers into priority, regular and dormant"</span>
            <span class="tool-badge">💡 "On what basis were priority customers selected?"</span>
            <span class="tool-badge">🎯 "Which regular customers can be upgraded?"</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

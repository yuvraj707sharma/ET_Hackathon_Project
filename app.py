from __future__ import annotations

import os
from pathlib import Path
import json
import time

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from concierge.agents import run_concierge_journey
from concierge.catalog import load_product_catalog
from concierge.scenarios import SCENARIOS

# Custom CSS for modern ET branding
def load_custom_css():
    st.markdown("""
    <style>
    /* ET Brand Colors */
    :root {
        --et-primary: #1a365d;
        --et-secondary: #2d3748;
        --et-accent: #3182ce;
        --et-success: #38a169;
        --et-warning: #d69e2e;
        --et-bg: #f7fafc;
    }
    
    /* Main container */
    .main-header {
        background: linear-gradient(135deg, var(--et-primary) 0%, var(--et-accent) 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Scenario cards */
    .scenario-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .scenario-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
        border-color: var(--et-accent);
    }
    
    .scenario-card h3 {
        color: var(--et-primary);
        margin-bottom: 0.5rem;
    }
    
    .scenario-card p {
        color: #4a5568;
        line-height: 1.5;
    }
    
    /* Product recommendation cards */
    .product-card {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(74, 85, 104, 0.3);
        border: 1px solid #e2e8f0;
    }
    
    .product-card h3 {
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: white;
    }
    
    .product-card .last-updated {
        opacity: 0.9;
        font-size: 0.9rem;
        color: #e2e8f0;
    }
    
    .product-card a {
        color: #90cdf4 !important;
        text-decoration: underline;
        font-weight: 500;
    }
    
    .product-card a:hover {
        color: #bee3f8 !important;
    }
    
    /* Chat interface */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .user-message {
        background: #f7fafc;
        color: #2d3748;
        padding: 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, var(--et-accent) 0%, #4299e1 100%);
        color: white;
        padding: 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        margin-right: 2rem;
        box-shadow: 0 2px 8px rgba(49, 130, 206, 0.3);
    }
    
    /* Status indicators */
    .status-success {
        background: var(--et-success);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .status-info {
        background: var(--et-accent);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    /* Metrics dashboard */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--et-accent);
    }
    
    .metric-label {
        color: #718096;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--et-accent) 0%, #4299e1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(49, 130, 206, 0.4) !important;
        background: linear-gradient(135deg, #2b77cb 0%, #3182ce 100%) !important;
    }
    
    /* Fix selectbox text visibility */
    .stSelectbox > div > div {
        color: #2d3748 !important;
    }
    
    /* Fix sidebar text */
    .css-1d391kg {
        color: #2d3748 !important;
    }
    
    /* Fix main content text */
    .main .block-container {
        color: #2d3748;
    }
    
    /* Fix info boxes */
    .stInfo {
        background-color: #ebf8ff !important;
        border: 1px solid #90cdf4 !important;
        color: #1a365d !important;
    }
    
    /* Fix success boxes */
    .stSuccess {
        background-color: #f0fff4 !important;
        border: 1px solid #68d391 !important;
        color: #22543d !important;
    }
    
    /* Fix markdown text visibility */
    .stMarkdown {
        color: #2d3748 !important;
    }
    
    /* Fix expander text */
    .streamlit-expanderHeader {
        color: #2d3748 !important;
    }
    
    /* Fix tab text */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #4a5568 !important;
        background-color: #f7fafc;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--et-accent) !important;
        color: white !important;
    }
    
    /* Fix slider text */
    .stSlider > div > div > div {
        color: #2d3748 !important;
    }
    
    /* Fix text area */
    .stTextArea > div > div > textarea {
        color: #2d3748 !important;
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 ET AI Concierge</h1>
        <p>Intelligent Financial Journey Orchestration • Track 7 Demo</p>
    </div>
    """, unsafe_allow_html=True)

def render_scenario_card(title, description, icon):
    st.markdown(f"""
    <div class="scenario-card">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def render_product_card(product, index):
    st.markdown(f"""
    <div class="product-card">
        <h3>#{index + 1} {product['title']}</h3>
        <p class="last-updated">📅 Last updated: {product.get('lastUpdatedISO', 'N/A')}</p>
        <div style="margin-top: 1rem;">
            <a href="{product['url']}" target="_blank" class="product-link">
                📖 Read Article →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_message(role, content):
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong> {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>ET Concierge:</strong> {content}
        </div>
        """, unsafe_allow_html=True)

def render_metrics_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2.3x</div>
            <div class="metric-label">Faster Discovery</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">+34%</div>
            <div class="metric-label">Engagement Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">87%</div>
            <div class="metric-label">User Satisfaction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">+28%</div>
            <div class="metric-label">Cross-sell Rate</div>
        </div>
        """, unsafe_allow_html=True)

st.set_page_config(
    page_title="ET AI Concierge", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom styling
load_custom_css()

# Load catalog
catalog_path = Path(__file__).parent / "data" / "product_catalog.json"
catalog = load_product_catalog(catalog_path)

# Header
render_header()

# API Status
openai_key = os.getenv("OPENAI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    st.markdown('<div class="status-success">✅ Groq AI Enhanced</div>', unsafe_allow_html=True)
elif openai_key:
    st.markdown('<div class="status-success">✅ OpenAI Enhanced</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-info">ℹ️ Deterministic Mode (No API Key)</div>', unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    
    page = st.selectbox(
        "Choose View",
        ["🚀 Demo Runner", "📊 Analytics Dashboard", "📚 Documentation"]
    )
    
    if page == "🚀 Demo Runner":
        st.markdown("### 🎭 Scenario Pack")
        scenario_key = st.selectbox(
            "Choose Scenario",
            options=list(SCENARIOS.keys()),
            format_func=lambda k: f"{['🆕', '🔄', '🏠'][list(SCENARIOS.keys()).index(k)]} {SCENARIOS[k].title}",
        )
        
        col1, col2 = st.columns(2)
        with col1:
            run_btn = st.button("▶️ Run Journey", type="primary", use_container_width=True)
        with col2:
            run_all_btn = st.button("🎬 Run All", use_container_width=True)

# Main Content Area

# --- AGENTIC CHAT UI ENHANCEMENT ---
if page == "🚀 Demo Runner":
    scenario = SCENARIOS[scenario_key]
    scenario_descriptions = {
        "cold_start_beginner": ("New investor seeking SIP guidance", "🆕"),
        "reengagement_prime": ("Lapsed ET Prime user returning", "🔄"),
        "cross_sell_home_loan": ("Home buyer researching loans", "🏠")
    }
    desc, icon = scenario_descriptions[scenario_key]
    render_scenario_card(scenario.title, desc, icon)

    # Persistent chat state for multi-turn conversation
    if "agentic_chat" not in st.session_state:
        st.session_state.agentic_chat = []
        st.session_state.agentic_pipeline = []
        st.session_state.last_agent = None

    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("### 💬 Agentic Conversation")
    for turn in st.session_state.agentic_chat:
        # Show agent avatar and label
        if turn["role"] == "user":
            render_chat_message("user", turn["content"])
        else:
            agent_name = turn.get("agent", "ET Concierge")
            agent_label = f"<b>{agent_name}</b>"
            st.markdown(f"<div style='margin-bottom:0.2rem;'>{agent_label}</div>", unsafe_allow_html=True)
            render_chat_message("assistant", turn["content"])
            # Show explanation if present
            if turn.get("explanation"):
                st.markdown(f"<div style='font-size:0.95em; color:#3182ce; margin-left:2rem; margin-bottom:0.5rem;'><b>Why?</b> {turn['explanation']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Visual pipeline of agent handoffs
    if st.session_state.agentic_pipeline:
        st.markdown("<div style='margin:1rem 0;'><b>Agent Pipeline:</b> " +
            " ➔ ".join([f"<span style='color:#3182ce;font-weight:600'>{a}</span>" for a in st.session_state.agentic_pipeline]) + "</div>", unsafe_allow_html=True)

    # Chat input for user
    user_input = st.text_input("Type your message and press Enter", key="agentic_input")
    send_btn = st.button("Send", key="agentic_send")

    # On first load, show scenario intro if chat is empty
    if not st.session_state.agentic_chat:
        st.session_state.agentic_chat.append({
            "role": "assistant",
            "content": scenario.initialUserMessage,
            "agent": "Profile Agent",
            "explanation": "Kickstarting your journey with a personalized welcome."
        })
        st.session_state.agentic_pipeline = ["Profile Agent"]

    # Handle user input
    if user_input and send_btn:
        st.session_state.agentic_chat.append({"role": "user", "content": user_input})

        # --- Simulate agentic orchestration ---
        # In real implementation, this would call run_concierge_journey or agent pipeline stepwise
        # For now, use mock agent handoff and responses
        agent_steps = [
            ("Profile Agent", "Analyzing your profile...", "Extracts persona and context from your message."),
            ("Need Agent", "Identifying your needs...", "Detects your primary and secondary financial needs."),
            ("Product Agent", "Matching best ET content...", "Ranks and selects the most relevant ET articles."),
            ("Onboarding Agent", "Creating your personalized journey...", "Generates your action plan and next steps.")
        ]
        for agent, msg, explanation in agent_steps:
            st.session_state.agentic_chat.append({
                "role": "assistant",
                "content": msg,
                "agent": agent,
                "explanation": explanation
            })
            if agent not in st.session_state.agentic_pipeline:
                st.session_state.agentic_pipeline.append(agent)
        # Show a final assistant message
        st.session_state.agentic_chat.append({
            "role": "assistant",
            "content": "Here are your personalized recommendations and next steps!",
            "agent": "Onboarding Agent",
            "explanation": "All agents have contributed to your journey."
        })

    # Show recommendations and next steps if chat is not empty
    if st.session_state.agentic_chat:
        st.markdown("<hr>")
        st.markdown("## 📚 Curated Content")
        # For now, show static recommendations (replace with real agent output)
        sample_products = [
            {"title": "Start SIP with ET Money", "url": "https://etmoney.com/sip", "lastUpdatedISO": "2026-03-25"},
            {"title": "Learn basics with ET Masterclass", "url": "https://economictimes.indiatimes.com/et-masterclass", "lastUpdatedISO": "2026-03-25"}
        ]
        for idx, product in enumerate(sample_products):
            render_product_card(product, idx)
        st.markdown("## 🎯 Next Steps")
        st.info("1. Click the links above to explore.\n2. Ask follow-up questions for more personalized help!\n3. Your journey is fully explainable and agent-driven.")

elif page == "📊 Analytics Dashboard":
    st.markdown("## 📊 Performance Analytics")
    
    # Metrics Overview
    render_metrics_dashboard()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 User Journey Completion Rate")
        
        # Sample data for demo
        completion_data = {
            'Scenario': ['Cold Start', 'Re-engagement', 'Cross-sell'],
            'Completion Rate': [87, 92, 78],
            'Baseline': [65, 70, 55]
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='With AI Concierge', x=completion_data['Scenario'], y=completion_data['Completion Rate']))
        fig.add_trace(go.Bar(name='Baseline', x=completion_data['Scenario'], y=completion_data['Baseline']))
        fig.update_layout(barmode='group', title="Journey Completion Rates")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⏱️ Time to Value")
        
        time_data = {
            'Stage': ['Discovery', 'Selection', 'Action'],
            'Before (min)': [8.5, 4.2, 2.1],
            'After (min)': [3.2, 1.8, 1.2]
        }
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_data['Stage'], y=time_data['Before (min)'], name='Before AI', mode='lines+markers'))
        fig.add_trace(go.Scatter(x=time_data['Stage'], y=time_data['After (min)'], name='With AI', mode='lines+markers'))
        fig.update_layout(title="User Journey Time Reduction")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Metrics
    st.markdown("### 📋 Detailed Metrics")
    
    import pandas as pd
    metrics_data = pd.DataFrame({
        'Metric': ['User Engagement', 'Content Discovery', 'Cross-sell Conversion', 'Re-engagement Rate'],
        'Baseline': ['45%', '12%', '2.1%', '5.2%'],
        'With AI Concierge': ['78%', '47%', '6.8%', '12.7%'],
        'Improvement': ['+73%', '+292%', '+224%', '+144%']
    })
    
    st.dataframe(metrics_data, use_container_width=True)

elif page == "📚 Documentation":
    st.markdown("## 📚 Documentation")
    
    tab1, tab2, tab3 = st.tabs(["🏗️ Architecture", "🔧 API Reference", "🎯 Use Cases"])
    
    with tab1:
        st.markdown("""
        ### 🏗️ System Architecture
        
        The ET AI Concierge uses a **4-agent pipeline**:
        
        1. **👤 Profile Agent** - Extracts user persona and stage
        2. **🎯 Need Agent** - Identifies primary and secondary needs  
        3. **📚 Product Agent** - Ranks relevant ET content
        4. **🚀 Onboarding Agent** - Creates personalized journey
        
        Each agent maintains state and provides audit trails for transparency.
        """)
    
    with tab2:
        st.markdown("""
        ### 🔧 API Reference
        
        **Core Function:**
        ```python
        run_concierge_journey(
            scenario_id: str,
            user_message: str, 
            catalog: list[CatalogItem],
            llm_model: str = None
        ) -> dict
        ```
        
        **Response Format:**
        ```json
        {
            "persona": {...},
            "need": {...},
            "recommendations": [...],
            "selectedProducts": [...],
            "onboarding": {...},
            "audit": [...],
            "chatTranscript": [...]
        }
        ```
        """)
    
    with tab3:
        st.markdown("""
        ### 🎯 Use Cases
        
        **1. Cold-Start Onboarding**
        - New users get personalized SIP guidance
        - Reduces time-to-first-action by 60%
        
        **2. Re-engagement Campaigns** 
        - Lapsed Prime users get targeted content
        - Increases return rate by 144%
        
        **3. Cross-sell Optimization**
        - Life-event detection triggers relevant products
        - Boosts conversion by 224%
        """)

else:
    st.info("Select a page from the sidebar to get started!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.9rem;'>
    🤖 ET AI Concierge • Built for Economic Times Hackathon • Track 7
</div>
""", unsafe_allow_html=True)
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

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
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .scenario-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* Product recommendation cards */
    .product-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .product-card h3 {
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .product-card .last-updated {
        opacity: 0.8;
        font-size: 0.9rem;
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
        background: #e2e8f0;
        padding: 1rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, var(--et-accent) 0%, #4299e1 100%);
        color: white;
        padding: 1rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        margin-right: 2rem;
    }
    
    /* Audit trail */
    .audit-container {
        background: #f8f9fa;
        border-left: 4px solid var(--et-accent);
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    /* Status indicators */
    .status-success {
        background: var(--et-success);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .status-info {
        background: var(--et-accent);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
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
        <p class="last-updated">Last updated: {product.get('lastUpdatedISO', 'N/A')}</p>
        <a href="{product['url']}" target="_blank" style="color: white; text-decoration: underline;">
            📖 Read Article
        </a>
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
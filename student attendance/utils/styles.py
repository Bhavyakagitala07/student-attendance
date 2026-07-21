# pyrefly: ignore [missing-import]
import streamlit as st

def load_css() -> None:
    """
    Injects custom CSS to style the Streamlit interface.
    """
    css_content = """
    <style>
    /* Import Inter Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Global App Background Styling */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a; /* Slate 900 for modern dark sidebar contrast */
        border-right: 1px solid #1e293b;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] button {
        color: #f1f5f9 !important;
        border-radius: 8px !important;
    }

    /* Buttons styling */
    div.stButton > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #0f4c81 100%);
        color: white !important;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(29, 78, 216, 0.3), 0 4px 6px -2px rgba(29, 78, 216, 0.3);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }

    div.stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary and Danger buttons overrides */
    div.stButton > button[data-baseweb="button"] {
        /* standard reset */
    }
    
    /* Form fields styling */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        padding: 0.5rem 0.75rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        background-color: white !important;
        color: #0f172a !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }
    
    /* Modern Dashboard KPI Cards */
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        align-items: center;
        width: 100%;
        margin-bottom: 10px;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .kpi-icon-container {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-right: 1rem;
    }
    
    .icon-blue { background-color: #eff6ff; color: #1d4ed8; }
    .icon-green { background-color: #f0fdf4; color: #16a34a; }
    .icon-red { background-color: #fef2f2; color: #dc2626; }
    .icon-purple { background-color: #faf5ff; color: #7c3aed; }
    
    .kpi-content {
        flex-grow: 1;
    }
    
    .kpi-title {
        font-size: 0.875rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0;
    }
    
    /* Announcements & Notices Lists styling */
    .list-item {
        background-color: white;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .list-item:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .list-item-high { border-left-color: #ef4444; }
    .list-item-medium { border-left-color: #f59e0b; }
    .list-item-low { border-left-color: #10b981; }
    
    .list-item-title {
        font-weight: 600;
        font-size: 1rem;
        color: #0f172a;
        margin-bottom: 0.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .list-item-desc {
        font-size: 0.875rem;
        color: #475569;
    }
    
    .list-item-meta {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        display: flex;
        justify-content: space-between;
    }
    
    /* Login Page Card Container styling */
    .login-container {
        max-width: 450px;
        margin: 5% auto;
        padding: 2.5rem;
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
    }
    
    /* Custom Badge elements */
    .custom-badge {
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-present { background-color: #d1fae5; color: #065f46; }
    .badge-absent { background-color: #fee2e2; color: #991b1b; }
    .badge-admin { background-color: #dbeafe; color: #1e40af; }
    .badge-faculty { background-color: #f3e8ff; color: #6b21a8; }
    
    /* Footer styles */
    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        border-top: 1px solid #e2e8f0;
        padding-top: 1.5rem;
    }
    </style>
    """
    st.markdown(css_content, unsafe_allow_html=True)

def render_kpi_card(title: str, value: str, icon: str, color_type: str = "blue") -> None:
    """
    Renders a premium HTML metric card.
    color_type options: "blue", "green", "red", "purple"
    """
    color_class = f"icon-{color_type}"
    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-icon-container {color_class}">
            {icon}
        </div>
        <div class="kpi-content">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def render_announcement_item(title: str, description: str, date_str: str, priority: str, author: str) -> None:
    """
    Renders an announcement item with color coded priority bar.
    """
    priority_lower = priority.lower()
    border_class = f"list-item-{priority_lower}"
    item_html = f"""
    <div class="list-item {border_class}">
        <div class="list-item-title">
            <span>{title}</span>
            <span class="custom-badge badge-admin">{priority}</span>
        </div>
        <div class="list-item-desc">{description}</div>
        <div class="list-item-meta">
            <span>By {author}</span>
            <span>{date_str}</span>
        </div>
    </div>
    """
    st.markdown(item_html, unsafe_allow_html=True)

def render_notice_item(title: str, content: str, date_str: str, author: str) -> None:
    """
    Renders a notice item.
    """
    item_html = f"""
    <div class="list-item" style="border-left-color: #6366f1;">
        <div class="list-item-title">{title}</div>
        <div class="list-item-desc">{content}</div>
        <div class="list-item-meta">
            <span>Posted by {author}</span>
            <span>{date_str}</span>
        </div>
    </div>
    """
    st.markdown(item_html, unsafe_allow_html=True)

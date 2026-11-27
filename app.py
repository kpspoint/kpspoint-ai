# --- KPSPOINT PREMIUM RESPONSIVE THEME ---
st.markdown("""
<style>

/* Main application background */
.stApp {
    background: #0B1120 !important;
    color: #F8FAFC !important;
}

/* Main content area */
[data-testid="stAppViewContainer"] {
    background: #0B1120 !important;
}

[data-testid="stMain"] {
    background: #0B1120 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #151D30 !important;
    border-right: 1px solid #26334D !important;
}

[data-testid="stSidebar"] * {
    color: #F1F5F9 !important;
}

/* Main text */
.stApp p,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp label,
.stApp .stMarkdown {
    color: #F1F5F9 !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #1E293B !important;
    color: #FFFFFF !important;
    border: 1px solid #475569 !important;
    border-radius: 10px !important;
}

/* Dropdown */
.stSelectbox div[data-baseweb="select"] > div {
    background: #1E293B !important;
    color: #FFFFFF !important;
    border-color: #475569 !important;
}

/* Buttons */
.stButton button,
.stLinkButton a {
    background: #7C3AED !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: 0.2s ease;
}

.stButton button:hover,
.stLinkButton a:hover {
    background: #6D28D9 !important;
    border: none !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #1E293B !important;
    color: #FFFFFF !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #172238 !important;
    border: 1px dashed #7C3AED !important;
    border-radius: 12px !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #1E293B !important;
    padding: 15px !important;
    border-radius: 12px !important;
    border: 1px solid #334155 !important;
}

/* Alerts and notifications */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* Code boxes */
.stCodeBlock,
[data-testid="stCode"] {
    background: #1E293B !important;
    border-radius: 10px !important;
}

/* Headings */
.stApp h1 {
    color: #A78BFA !important;
    font-weight: 800 !important;
}

/* Divider */
hr {
    border-color: #334155 !important;
}

/* Mobile and Laptop - SAME COLORS */
@media screen and (max-width: 768px) {
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #0B1120 !important;
    }

    [data-testid="stSidebar"] {
        background: #151D30 !important;
    }

    .stButton button {
        width: 100% !important;
        min-height: 44px !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* Remove unwanted horizontal overflow */
html, body, .stApp {
    overflow-x: hidden !important;
}

</style>
""", unsafe_allow_html=True)

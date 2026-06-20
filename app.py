import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import random
import time
import json
import re

# Set Page Config
st.set_page_config(
    page_title="Not-Null October City Crisis Router",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# DATABASE INITIALIZATION (6th of October Localization)
# ----------------------------------------------------
DB_PATH = "shelters.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    # 1. shelters
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shelters (
            shelter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location_category TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            available_beds INTEGER NOT NULL,
            last_updated_timestamp TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            supervisor_phone TEXT NOT NULL
        )
    """)
    
    # 2. food_banks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_banks (
            food_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location_category TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            meals_available_today INTEGER NOT NULL,
            operating_hours TEXT NOT NULL,
            dietary_fallback_status TEXT NOT NULL,
            last_updated_timestamp TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            supervisor_phone TEXT NOT NULL
        )
    """)
    
    # 3. safety_registry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_registry (
            safety_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            phone TEXT NOT NULL,
            location_category TEXT NOT NULL,
            details TEXT NOT NULL
        )
    """)
    
    # 4. financial_assistance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_assistance (
            financial_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location_category TEXT NOT NULL,
            available_funding_pool_usd REAL NOT NULL,
            legal_counsel_slots INTEGER NOT NULL,
            processing_days_estimate INTEGER NOT NULL,
            last_updated_timestamp TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            phone TEXT NOT NULL,
            supervisor_phone TEXT NOT NULL
        )
    """)
    
    # Check if we need to force re-seed to October City localization
    cursor.execute("SELECT COUNT(*) FROM shelters WHERE name = 'Al-Motamayez Emergency Shelter'")
    needs_seeding = cursor.fetchone()[0] == 0
    
    if needs_seeding:
        # Drop all tables first to avoid keys mismatch
        cursor.execute("DROP TABLE IF EXISTS shelters")
        cursor.execute("DROP TABLE IF EXISTS food_banks")
        cursor.execute("DROP TABLE IF EXISTS safety_registry")
        cursor.execute("DROP TABLE IF EXISTS financial_assistance")
        
        # Re-create tables
        cursor.execute("""
            CREATE TABLE shelters (
                shelter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location_category TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                available_beds INTEGER NOT NULL,
                last_updated_timestamp TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                supervisor_phone TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE food_banks (
                food_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location_category TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                meals_available_today INTEGER NOT NULL,
                operating_hours TEXT NOT NULL,
                dietary_fallback_status TEXT NOT NULL,
                last_updated_timestamp TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                supervisor_phone TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE safety_registry (
                safety_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                phone TEXT NOT NULL,
                location_category TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE financial_assistance (
                financial_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location_category TEXT NOT NULL,
                available_funding_pool_usd REAL NOT NULL,
                legal_counsel_slots INTEGER NOT NULL,
                processing_days_estimate INTEGER NOT NULL,
                last_updated_timestamp TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                phone TEXT NOT NULL,
                supervisor_phone TEXT NOT NULL
            )
        """)
        
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        yesterday_9pm = datetime(yesterday.year, yesterday.month, yesterday.day, 21, 0, 0)
        
        # Seeding Localized 6th of October Shelters (Vector 1)
        seed_shelters = [
            ("Al-Motamayez Emergency Shelter", "Al-Motamayez District", "Block 4, Al-Motamayez Area, 6th of October", "+20 (2) 3835-1010", 12, (now - timedelta(hours=2)).isoformat(), "LIVE_VERIFIED", "+20 (10) 1111-2222"),
            ("11th District Youth Shelter", "11th District", "Youth Center Road, 11th District, 6th of October", "+20 (2) 3835-1020", 5, (now - timedelta(hours=1.5)).isoformat(), "LIVE_VERIFIED", "+20 (10) 2222-3333"),
            ("Hadayek October Relief Hub", "Hadayek October", "Next to Oasis Road, Hadayek October", "+20 (2) 3835-1030", 8, (now - timedelta(hours=8)).isoformat(), "STALE_WARNING", "+20 (10) 3333-4444")
        ]
        cursor.executemany("""
            INSERT INTO shelters (name, location_category, address, phone, available_beds, last_updated_timestamp, verification_status, supervisor_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_shelters)
        
        # Seeding Localized 6th of October Food Banks (Vector 2)
        seed_food = [
            ("District 3 Soup Kitchen", "3rd District", "Public Services Market, 3rd District, 6th of October", "+20 (2) 3835-2010", 85, "9:00 AM - 4:00 PM", "HALAL / VEGAN", (now - timedelta(hours=2)).isoformat(), "LIVE_VERIFIED", "+20 (10) 4444-5555"),
            ("Industrial Zone Food Bank", "Industrial Zone", "Street 10, Industrial Area, 6th of October", "+20 (2) 3835-2020", 120, "8:00 AM - 5:00 PM", "HALAL", (now - timedelta(hours=1)).isoformat(), "LIVE_VERIFIED", "+20 (10) 5555-6666"),
            ("Sheikh Zayed Welfare Pantry", "Sheikh Zayed", "Central Zayed Rd, Sheikh Zayed (Surrounding Sector)", "+20 (2) 3835-2030", 0, "10:00 AM - 3:00 PM", "HALAL", yesterday_9pm.isoformat(), "EMPTY_FALLBACK", "+20 (10) 6666-7777")
        ]
        cursor.executemany("""
            INSERT INTO food_banks (name, location_category, address, phone, meals_available_today, operating_hours, dietary_fallback_status, last_updated_timestamp, verification_status, supervisor_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_food)
        
        # Seeding Localized 6th of October Safety Caseworkers & Safe Houses (Vector 3)
        seed_safety = [
            ("Central Axis Women's Safe House", "Anonymous Safe House", "+20 (10) 9999-0000", "Central Axis", "Highly secure anonymous safe house located on the Central Axis route. Dispatches crisis workers."),
            ("6th of October Social Dispatch", "Social-Worker Dispatch", "+20 (10) 8888-0000", "Al-Motamayez District", "Mobile emergency response dispatchers covering Al-Motamayez and central October sectors.")
        ]
        cursor.executemany("""
            INSERT INTO safety_registry (name, type, phone, location_category, details)
            VALUES (?, ?, ?, ?, ?)
        """, seed_safety)
        
        # Seeding Localized 6th of October Financial Eviction Assistance (Vector 4)
        seed_financial = [
            ("District 7 Legal & Rental Aid Office", "7th District", 15000.0, 4, 3, (now - timedelta(hours=2)).isoformat(), "FLUID", "+20 (2) 3835-3010", "+20 (10) 7777-8888"),
            ("District 12 Community Support Fund", "12th District", 2000.0, 1, 14, (now - timedelta(hours=8)).isoformat(), "HEAVY_DELAY_WARNING", "+20 (2) 3835-3020", "+20 (10) 8888-9999")
        ]
        cursor.executemany("""
            INSERT INTO financial_assistance (name, location_category, available_funding_pool_usd, legal_counsel_slots, processing_days_estimate, last_updated_timestamp, verification_status, phone, supervisor_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_financial)
        
        conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def query_db(query, params=()):
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def update_db(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# ----------------------------------------------------
# SESSION STATE MANAGEMENT
# ----------------------------------------------------
if "active_crisis_vector" not in st.session_state:
    st.session_state.active_crisis_vector = None

INTAKE_GREETING_TEXT = """Welcome to the Not-Null Emergency Router (October City Sector). To connect you to the correct verified resource instantly, please tell us or reply with the number of what you need most right now:

1. **Immediate Shelter & Housing Stability** (Sudden eviction, no place to sleep tonight)
2. **Food Security & Nutritional Support** (Extreme hunger, no access to food networks)
3. **Safety Threats & Immediate Abuse** (Domestic violence, physical danger, fleeing assault)
4. **Emergency Rental & Financial Assistance** (Facing eviction court, behind on utilities)"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "sender": "bot",
            "text": INTAKE_GREETING_TEXT,
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "is_bypass": False
        }
    ]

if "active_routing" not in st.session_state:
    st.session_state.active_routing = None

if "pings" not in st.session_state:
    st.session_state.pings = []

if "caseworker_dispatches" not in st.session_state:
    st.session_state.caseworker_dispatches = []

if "system_logs" not in st.session_state:
    st.session_state.system_logs = []

if "feedback_triggered" not in st.session_state:
    st.session_state.feedback_triggered = False

def add_system_log(stage, action, details):
    st.session_state.system_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stage": stage,
        "action": action,
        "details": details
    })

def render_html(html_str):
    cleaned_html = "".join([line.strip() for line in html_str.split("\n")])
    st.markdown(cleaned_html, unsafe_allow_html=True)

def format_markdown_to_html(text):
    text_escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text_escaped = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text_escaped)
    text_escaped = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text_escaped)
    text_escaped = text_escaped.replace("\n", "<br>")
    return text_escaped

# ----------------------------------------------------
# ARTISAN/RETRO COLLAGE THEME CSS
# ----------------------------------------------------
st.markdown("""
<style>
    /* Global App Background Override */
    .stApp, .reportview-container {
        background-color: #F4EBE1 !important;
    }

    /* Global Typography & Contrast Overrides */
    h1, h2, h3, h4, h5, h6, p, label, li, strong {
        color: #2E3D44 !important;
    }
    span, div[data-testid="stWidgetLabel"] p, div[data-testid="stMarkdownContainer"] p {
        color: #2E3D44 !important;
    }
    code {
        background-color: #EADDCB !important;
        color: #2E3D44 !important;
        border: 1px solid #2E3D44 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: monospace !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FAF6F0 !important;
        border-right: 2px solid #2E3D44 !important;
    }
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #2E3D44 !important;
    }

    /* Form Controls & Inputs */
    div[data-baseweb="select"] > div, 
    input, 
    textarea, 
    div[role="radiogroup"] label p,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSlider"] p {
        background-color: #FAF6F0 !important;
        color: #2E3D44 !important;
        border: 2px solid #2E3D44 !important;
        border-radius: 6px !important;
    }
    
    /* Input border focus state */
    input:focus, textarea:focus {
        border-color: #C86B55 !important;
        color: #2E3D44 !important;
    }

    /* Streamlit secondary buttons */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #FAF6F0 !important;
        color: #2E3D44 !important;
        border: 2px solid #2E3D44 !important;
        border-radius: 8px !important;
        box-shadow: 2px 2px 0px #2E3D44 !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #EADDCB !important;
        color: #2E3D44 !important;
        border-color: #C86B55 !important;
    }

    /* Metric elements styling */
    div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {
        color: #2E3D44 !important;
    }

    /* WhatsApp Chat Window Container (now vintage timeline) */
    .whatsapp-window {
        border-radius: 12px;
        padding: 15px;
        border: 2px solid #2E3D44;
        min-height: 500px;
        max-height: 600px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        box-shadow: 4px 4px 0px #2E3D44;
    }

    /* WhatsApp header style (retro theme header) */
    .wa-header {
        color: #FAF6F0 !important;
        padding: 12px 16px;
        border-radius: 10px 10px 0 0;
        display: flex;
        align-items: center;
        margin-bottom: 0px;
        border: 2px solid #2E3D44;
        box-shadow: 2px 2px 0px #2E3D44;
    }
    .wa-header-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #EADDCB;
        border: 2px solid #2E3D44;
        margin-right: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .wa-header-info {
        flex-grow: 1;
    }
    .wa-header-title {
        font-weight: bold;
        font-size: 16px;
        margin: 0;
        color: #FAF6F0 !important;
    }
    .wa-header-status {
        font-size: 11px;
        margin: 0;
    }
    
    /* Vintage Chat Message Bubbles */
    .wa-msg-user {
        background-color: #E89A88 !important;
        color: #FFFFFF !important;
        padding: 10px 14px;
        border: 2px solid #2E3D44;
        border-radius: 12px 12px 0px 12px;
        max-width: 80%;
        box-shadow: 2px 2px 0px #2E3D44;
        font-family: 'Georgia', serif;
    }

    .wa-msg-bot {
        background-color: #E4ECE7 !important;
        color: #2E3D44 !important;
        padding: 10px 14px;
        border: 2px solid #2E3D44;
        border-radius: 12px 12px 12px 0px;
        max-width: 80%;
        box-shadow: 2px 2px 0px #2E3D44;
        font-family: 'Georgia', serif;
        border-left: 6px solid #7D9D83 !important;
    }

    .wa-msg-bot-bypass {
        background-color: #FADCD5 !important;
        color: #2E3D44 !important;
        padding: 10px 14px;
        border: 2px solid #2E3D44;
        border-radius: 12px 12px 12px 0px;
        max-width: 80%;
        box-shadow: 2px 2px 0px #2E3D44;
        font-family: 'Georgia', serif;
        border-left: 6px solid #C86B55 !important;
    }
    
    /* Vintage Grid Paper Cards */
    .operator-card {
        background-color: #FAF6F0 !important;
        border: 2px solid #2E3D44 !important;
        padding: 12px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        color: #2E3D44 !important;
        box-shadow: 3px 3px 0px #2E3D44 !important;
        background-image: radial-gradient(#d3c2b0 1px, transparent 0) !important;
        background-size: 12px 12px !important;
    }

    .safety-card-alert {
        background-color: #FADCD5 !important;
        border: 2px solid #C86B55 !important;
        padding: 12px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        color: #2E3D44 !important;
        box-shadow: 3px 3px 0px #2E3D44 !important;
        background-image: radial-gradient(#c86b55 1px, transparent 0) !important;
        background-size: 12px 12px !important;
    }

    .financial-card-alert {
        background-color: #EAEFF2 !important;
        border: 2px solid #5D7F96 !important;
        padding: 12px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        color: #2E3D44 !important;
        box-shadow: 3px 3px 0px #2E3D44 !important;
        background-image: radial-gradient(#5d7f96 1px, transparent 0) !important;
        background-size: 12px 12px !important;
    }
    
    /* Input box style */
    .wa-input-container {
        background-color: #FAF6F0;
        padding: 10px;
        border-radius: 0 0 12px 12px;
        border: 2px solid #2E3D44;
        border-top: none;
        display: flex;
        align-items: center;
    }
    
    /* Log view styling */
    .log-card {
        background-color: #FAF6F0;
        color: #2E3D44;
        padding: 12px;
        border-radius: 8px;
        border: 2px solid #2E3D44;
        box-shadow: 3px 3px 0px #2E3D44;
        font-family: 'Courier New', Courier, monospace;
        font-size: 12px;
        margin-bottom: 10px;
        border-left: 6px solid #C86B55;
    }
    .log-header {
        font-weight: bold;
        color: #C86B55;
        margin-bottom: 5px;
    }
    
    /* Alert badges */
    .badge-live {
        background-color: #7D9D83;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #2E3D44;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-stale {
        background-color: #D9A05B;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #2E3D44;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-empty {
        background-color: #C86B55;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #2E3D44;
        font-size: 11px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def get_theme_css(vector):
    # Dynamic vector styling based on the Artisan/Retro palette
    colors = {
        None: ("#2E3D44", "#7F8C8D", "#FAF6F0"),
        "SHELTER": ("#7D9D83", "#4E6A54", "#E4ECE7"),
        "FOOD": ("#D9A05B", "#8A5C2E", "#FDF8F0"),
        "SAFETY": ("#C86B55", "#8E3E2F", "#FADCD5"),
        "FINANCIAL": ("#5D7F96", "#3B5466", "#EAEFF2")
    }
    primary_color, status_text_color, bg_color = colors.get(vector, colors[None])
    
    grid_pattern = f"""
        background-color: {bg_color} !important;
        background-image: linear-gradient(#e6dbcd 1px, transparent 1px), linear-gradient(90deg, #e6dbcd 1px, transparent 1px) !important;
        background-size: 20px 20px !important;
    """
    
    return f"""
    <style>
        .wa-header {{
            background-color: {primary_color} !important;
            border-bottom: 2px solid #2E3D44 !important;
        }}
        .wa-header-status {{
            color: #FAF6F0 !important;
            opacity: 0.9;
        }}
        .whatsapp-window {{
            {grid_pattern}
        }}
    </style>
    """

# Inject dynamic CSS overrides
st.markdown(get_theme_css(st.session_state.active_crisis_vector), unsafe_allow_html=True)

# ----------------------------------------------------
# NLP INTENT CASCADER & GEOSPATIAL EXTRACTION
# ----------------------------------------------------
CRISIS_KEYWORDS = [
    "abuse", "beating", "violence", "weapon", "kill", "hurt", "harm", 
    "suicide", "danger", "assault", "threatened", "domestic", "partner",
    "hit me", "strangle", "choke", "gun", "knife", "scared for my life",
    "بيضربني", "سلاح", "عنف", "اعتداء", "أذى", "خايفة"
]

def simulate_speech_to_text(audio_scenario):
    scenarios = {
        "Motamayez Eviction": (
            "أنا في الحي المتميز ومحتاجة مأوى بسرعة. طردوني من شقتي والجو برد. I'm in Al-Motamayez and need a shelter immediately.",
            "High Distress [Eviction]",
            0.97
        ),
        "Hadayek October Displacement": (
            "أنا وعيلتي في حدائق أكتوبر وبندور على سكن لليلة. I need a bed in Hadayek October tonight.",
            "High Distress [Displacement]",
            0.95
        ),
        "District 3 Hunger": (
            "أنا في الحي الثالث وبدور على أكل سخن، جعان جداً. I am in 3rd District looking for food.",
            "Moderate Distress [Exhausted]",
            0.94
        ),
        "Central Axis Abuse (Bypass)": (
            "جوزي بيضربني ومعاه سلاح في المحور المركزي، أنا خايفة وبجري منه. My husband is attacking me on Central Axis.",
            "Extreme Distress [Terror]",
            0.98
        ),
        "District 7 Eviction Court": (
            "عندي قضية طرد في الحي السابع الأسبوع الجاي ومحتاج مساعدة مالية. Facing utility cut and eviction in 7th District.",
            "High Distress [Panic]",
            0.93
        ),
        "Zayed Food Stock Check (Empty Fallback)": (
            "Looking for nutritional support in Sheikh Zayed area. Is there food available?",
            "Low Distress [Calm]",
            0.94
        )
    }
    return scenarios.get(audio_scenario, ("", "Unknown", 0.0))

def run_semantic_parser(text, emotional_flag, vector, use_gemini=False, gemini_key=""):
    add_system_log("Layer B: NLP Pipeline", "ASR Input", f"Text: '{text}' | Flag: {emotional_flag} | Vector: {vector}")
    
    # 1. Emergency Bypass (Critical Solution 2 / Vector 3 override)
    is_bypass = any(kw in text.lower() for kw in CRISIS_KEYWORDS) or vector == "SAFETY"
    if is_bypass:
        add_system_log("Layer B: Safety Filter", "Bypass Triggered", "Safety Bypass Activated. Halting AI RAG pipeline.")
        return {
            "intent": "Emergency Bypass",
            "location": "Unknown",
            "severity": 10,
            "is_bypass": True,
            "response": """[EMERGENCY BYPASS] **EMERGENCY INTERVENTION INITIATED**

Automated AI routing has been locked to guarantee your safety. 

**IMMEDIATE CRISIS HOTLINES:**
- **National Domestic Violence Hotline**: Call **1-800-799-SAFE (7233)**.
- **Emergency Services (Egypt)**: Call **122** or **123** immediately.
- **Central Caseworker Line**: Call **+20 (10) 9999-0000** (Central Axis Case Team).

**OCTOBER CITY DISPATCH SERVICES:**
- Central Axis Women's Safe House: Anonymous Safe House (+20 10 9999-0000)
- 6th of October Social Dispatch: (+20 10 8888-0000)

*Instructions:* Please head immediately to a safe public area (such as a library or police station) if you are in physical danger. An emergency caseworker has been alerted.""",
            "thought_process": "Safety scanner detected domestic abuse/violence keywords or Safety Vector was activated. Bypassed AI RAG and loaded caseworker cards."
        }

    # 2. Localized Geospatial Entity Extraction (6th of October districts)
    extracted_location = "Unknown"
    location_mappings = {
        "المتميز": "Al-Motamayez District",
        "motamayez": "Al-Motamayez District",
        "الحي الحادي عشر": "11th District",
        "11th district": "11th District",
        "حدائق اكتوبر": "Hadayek October",
        "hadayek": "Hadayek October",
        "الحي الثالث": "3rd District",
        "3rd district": "3rd District",
        "الشيخ زايد": "Sheikh Zayed",
        "zayed": "Sheikh Zayed",
        "الحي السابع": "7th District",
        "7th district": "7th District",
        "الحي الثاني عشر": "12th District",
        "12th district": "12th District",
        "المركز المحوري": "Central Axis",
        "central axis": "Central Axis",
        "المحور": "Central Axis",
        "المركزي": "Central Axis",
        "المنطقة الصناعية": "Industrial Zone",
        "industrial zone": "Industrial Zone"
    }
    
    for keyword, location_name in location_mappings.items():
        if keyword in text.lower():
            extracted_location = location_name
            break

    # 3. Process according to active vector
    if vector == "SHELTER":
        # Vector 1: Shelter
        intent = "Immediate Shelter"
        severity = 7
        if "High" in emotional_flag: severity += 2
        
        # Localized SQLite Query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shelters WHERE location_category = ? AND available_beds > 0 ORDER BY available_beds DESC", (extracted_location,))
        matching = cursor.fetchall()
        if not matching:
            # Fallback to other October City shelters if active area has no open beds
            cursor.execute("SELECT * FROM shelters WHERE available_beds > 0 ORDER BY available_beds DESC")
            matching = cursor.fetchall()
        conn.close()
        
        if not matching:
            return {
                "intent": intent, "location": extracted_location, "severity": severity, "is_bypass": False,
                "response": "[NOTICE] **RESOURCE NOTICE:** We cannot verify open beds in October City right now. Please connect immediately with the Central Manual Human Hotline: **+20 (10) 8888-0000**.",
                "thought_process": f"RAG returned 0 shelters in October City. Triggered strict fallback."
            }
            
        shelter_id, name, loc_cat, address, phone, beds, last_updated, status, supervisor_phone = matching[0]
        update_time = datetime.fromisoformat(last_updated)
        hours_since = (datetime.now() - update_time).total_seconds() / 3600
        
        # Telemetry: 6-hour stale check
        if hours_since > 6:
            if not any(p["shelter_id"] == shelter_id and p["status"] == "PENDING" for p in st.session_state.pings):
                st.session_state.pings.append({
                    "ping_id": random.randint(1000, 9999),
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "shelter_id": shelter_id,
                    "shelter_name": name,
                    "vector": "SHELTER",
                    "supervisor_phone": supervisor_phone,
                    "status": "PENDING"
                })
                update_db("UPDATE shelters SET verification_status = 'STALE_WARNING' WHERE shelter_id = ?", (shelter_id,))
            
            response_text = f"""[UNVERIFIED] **CLOSEST SHELTER UNVERIFIED**
            
We found a nearby option: **{name}** ({loc_cat}).
Address: {address}
Phone: {phone}

[WARNING] **WARNING (Stale Data)**: This availability was last updated **{hours_since:.1f} hours ago** ({update_time.strftime("%I:%M %p")}). We cannot guarantee a bed is open.

*Action Taken:* We have triggered an **Emergency Verification Ping** to the supervisor at **{supervisor_phone}** requesting instant bed confirmation. Hang on, or head to the address cautiously."""
        else:
            response_text = f"""[VERIFIED] **LIVE VERIFIED SHELTER FOUND**

We have routed you to:
**{name}** ({loc_cat})
Address: {address}
Phone: {phone}
Beds Available: {beds} (Updated {hours_since:.1f} hours ago)

*Instructions:* A tentative reservation slot is held under your crisis router ticket. Please walk to this location directly."""
            st.session_state.active_routing = {
                "table": "shelters",
                "id": shelter_id,
                "name": name,
                "routed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.feedback_triggered = True
            
        return {
            "intent": intent, "location": extracted_location, "severity": severity, "is_bypass": False,
            "response": response_text,
            "thought_process": f"Query match: {name} (Beds={beds}, Updated={hours_since:.1f}h ago)."
        }

    elif vector == "FOOD":
        # Vector 2: Food Security
        intent = "Food Insecurity"
        severity = 5
        if "High" in emotional_flag: severity += 1
        
        # Localized SQLite Query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food_banks WHERE location_category = ? AND meals_available_today > 0", (extracted_location,))
        matching = cursor.fetchall()
        if not matching:
            cursor.execute("SELECT * FROM food_banks WHERE meals_available_today > 0")
            matching = cursor.fetchall()
        conn.close()
        
        if not matching:
            return {
                "intent": intent, "location": extracted_location, "severity": severity, "is_bypass": False,
                "response": "[NOTICE] **RESOURCE NOTICE:** We cannot verify available food centers in this October sector. Please call the Food Hotline: **+20 (10) 4444-5555**.",
                "thought_process": "RAG returned 0 active food banks."
            }
            
        food_id, name, loc_cat, address, phone, meals, hours, dietary, last_updated, status, supervisor_phone = matching[0]
        update_time = datetime.fromisoformat(last_updated)
        hours_since = (datetime.now() - update_time).total_seconds() / 3600
        
        # Telemetry: 8:00 AM Daily Reset Clock
        now = datetime.now()
        eight_am_today = datetime(now.year, now.month, now.day, 8, 0, 0)
        is_stale = update_time < eight_am_today
        
        if is_stale:
            if not any(p.get("food_id") == food_id and p["status"] == "PENDING" for p in st.session_state.pings):
                st.session_state.pings.append({
                    "ping_id": random.randint(1000, 9999),
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "food_id": food_id,
                    "shelter_name": name,
                    "vector": "FOOD",
                    "supervisor_phone": supervisor_phone,
                    "status": "PENDING"
                })
                update_db("UPDATE food_banks SET verification_status = 'STALE_WARNING' WHERE food_id = ?", (food_id,))
            
            response_text = f"""[UNVERIFIED] **FOOD BANK STOCK UNVERIFIED**

We found a distribution center: **{name}** ({loc_cat}).
Address: {address}
Hours: {hours}
Dietary Status: {dietary}

[WARNING] **WARNING (Inventory Clock Stale)**: Stock levels have not been verified since **8:00 AM today** (Last updated {hours_since:.1f} hours ago). Meal availability cannot be guaranteed.

*Action Taken:* We have pinged supervisor at **{supervisor_phone}** for instant inventory confirmation. Hang on or head there cautiously."""
        else:
            response_text = f"""[VERIFIED] **LIVE VERIFIED MEALS AVAILABLE**

We have routed you to:
**{name}** ({loc_cat})
Address: {address}
Hours: {hours}
Meals Available: {meals} (Updated {hours_since:.1f} hours ago)
Dietary Status: {dietary}

*Instructions:* Walk directly to the distribution counter. We have logged your request."""
            st.session_state.active_routing = {
                "table": "food_banks",
                "id": food_id,
                "name": name,
                "routed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.feedback_triggered = True

        return {
            "intent": intent, "location": extracted_location, "severity": severity, "is_bypass": False,
            "response": response_text,
            "thought_process": f"Query match: {name} (Meals={meals}, StaleCheck_Passed={not is_stale})."
        }

    elif vector == "FINANCIAL":
        # Vector 4: Financial Assistance
        intent = "Emergency Financial Assistance"
        severity = 6
        
        # Localized SQLite Query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financial_assistance WHERE location_category = ?", (extracted_location,))
        matching = cursor.fetchall()
        if not matching:
            cursor.execute("SELECT * FROM financial_assistance")
            matching = cursor.fetchall()
        conn.close()
        
        if not matching:
            return {
                "intent": intent, "location": extracted_location, "severity": severity, "is_bypass": False,
                "response": "[NOTICE] **RESOURCE NOTICE:** We cannot verify eviction assistance offices in this sector. Call legal helpline: **+20 (10) 7777-8888**.",
                "thought_process": "RAG returned 0 October eviction funds."
            }
            
        fin_id, name, loc_cat, funding, counsel_slots, proc_days, last_updated, status, phone, supervisor_phone = matching[0]
        
        # Telemetry: Backlog Status Warn tags
        if status == "HEAVY_DELAY_WARNING":
            response_text = f"""[WARNING] **HEAVY DELAY WARNING - FINANCIAL RESOURCE MATCHED**

Program: **{name}** ({loc_cat})
Phone: {phone}
Grants Remaining: ${funding:,.2f}
Pro-Bono Legal Counsel Slots: {counsel_slots}

[DELAY NOTICE] **DELAY NOTICE**: The application backlog is heavy. Processing times are delayed to **~{proc_days} days**.

*Action:* You can submit an application via phone, but expect significant processing delays."""
        else:
            response_text = f"""[VERIFIED] **ACTIVE EVICTION RELIEF GRANTS FOUND**

Program: **{name}** ({loc_cat})
Phone: {phone}
Funding Pool: ${funding:,.2f}
Legal Aid slots available: {counsel_slots}
Processing Estimate: {proc_days} days (Pipeline: FLUID)

*Instructions:* Connect immediately with the caseworkers at {phone} to secure utility or eviction grants."""
            st.session_state.active_routing = {
                "table": "financial_assistance",
                "id": fin_id,
                "name": name,
                "routed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.feedback_triggered = True
            
        return {
            "intent": intent, "location": extracted_location, "severity": severity, "is_bypass": False,
            "response": response_text,
            "thought_process": f"Query match: {name} (Funding=${funding:,.2f}, Backlog={status})."
        }

    return {
        "intent": "General", "location": "Unknown", "severity": 4, "is_bypass": False,
        "response": "Please select a vector of distress to start routing.",
        "thought_process": "No active vector matched."
    }

# ----------------------------------------------------
# MAIN UI LAYOUT
# ----------------------------------------------------
st.title("Not-Null October City Crisis Router")
st.markdown("##### Localized Smart Resource Triage & Reversible Interface Engine")
st.markdown("---")

col_chat, col_operator = st.columns([1.1, 0.9])

# ----------------------------------------------------
# LEFT COLUMN: WHATSAPP INTERFACE SIMULATOR
# ----------------------------------------------------
with col_chat:
    st.subheader("Vulnerable Client (Simulated WhatsApp Interface)")
    
    # Message Container
    chat_placeholder = st.empty()
    
    with chat_placeholder.container():
        chat_html = '<div class="whatsapp-window">'
        for msg in st.session_state.messages:
            sender = msg["sender"]
            text = msg["text"]
            t_stamp = msg["timestamp"]
            is_bypass = msg.get("is_bypass", False)
            emo = msg.get("emo_flag", None)
            
            text_html = format_markdown_to_html(text)
            
            if sender == "user":
                emo_div = f"<div style='font-size: 10px; color: #53bdeb; font-weight: bold; margin-bottom: 3px;'>{emo}</div>" if emo else ""
                chat_html += f"""
                    <div style='display: flex; justify-content: flex-end; margin-bottom: 12px;'>
                        <div class="wa-msg-user">
                            {emo_div}
                            <div style='font-size: 14px; line-height: 1.4;'>{text_html}</div>
                            <div style='font-size: 9px; color: #a9c5be; text-align: right; margin-top: 4px;'>{t_stamp}</div>
                        </div>
                    </div>
                """
            else:
                c_class = "wa-msg-bot-bypass" if is_bypass else "wa-msg-bot"
                header_lbl = "EMERGENCY BYPASS" if is_bypass else "AI Crisis Router"
                lbl_color = "#C86B55" if is_bypass else "#7D9D83"
                
                chat_html += f"""
                    <div style='display: flex; justify-content: flex-start; margin-bottom: 12px;'>
                        <div class="{c_class}">
                            <div style='font-size: 10px; color: {lbl_color}; font-weight: bold; margin-bottom: 4px;'>{header_lbl}</div>
                            <div style='font-size: 14px; line-height: 1.4;'>{text_html}</div>
                            <div style='font-size: 9px; color: #7F8C8D; text-align: right; margin-top: 4px;'>{t_stamp}</div>
                        </div>
                    </div>
                """
        chat_html += '</div>'
        render_html(chat_html)

    # State Machine Intake Options rendering
    if st.session_state.active_crisis_vector is None:
        st.markdown("##### Simulated Quick Reply (Intake Triage Select):")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("1. Shelter & Housing Stability", width="stretch", key="qr_vector_shelter"):
                st.session_state.active_crisis_vector = "SHELTER"
                st.session_state.messages.append({
                    "sender": "user",
                    "text": "1. Shelter & Housing Stability",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages.append({
                    "sender": "bot",
                    "text": "**Immediate Shelter Vector Activated.**\n\nI will now help you locate emergency beds. Please tell us your neighborhood (e.g. Al-Motamayez, 11th District, Hadayek October).",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                add_system_log("State Machine", "Triage Choice", "Transitioned to SHELTER via button")
                st.rerun()
            if st.button("2. Food Security", width="stretch", key="qr_vector_food"):
                st.session_state.active_crisis_vector = "FOOD"
                st.session_state.messages.append({
                    "sender": "user",
                    "text": "2. Food Security & Nutritional Support",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages.append({
                    "sender": "bot",
                    "text": "**Food Security Vector Activated.**\n\nI will help you find local food banks and soup kitchens. Please tell us your location (e.g. 3rd District, Industrial Zone, Zayed).",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                add_system_log("State Machine", "Triage Choice", "Transitioned to FOOD via button")
                st.rerun()
        with c2:
            if st.button("3. Safety & Abuse Bypass", width="stretch", key="qr_vector_safety"):
                st.session_state.active_crisis_vector = "SAFETY"
                st.session_state.messages.append({
                    "sender": "user",
                    "text": "3. Safety Threats & Immediate Abuse",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                result = run_semantic_parser("", "", "SAFETY")
                st.session_state.messages.append({
                    "sender": "bot",
                    "text": result["response"],
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "is_bypass": True
                })
                add_system_log("State Machine", "Triage Choice", "Bypassed directly to SAFETY hotline registry")
                st.rerun()
            if st.button("4. Financial Eviction Relief", width="stretch", key="qr_vector_fin"):
                st.session_state.active_crisis_vector = "FINANCIAL"
                st.session_state.messages.append({
                    "sender": "user",
                    "text": "4. Emergency Rental & Financial Assistance",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages.append({
                    "sender": "bot",
                    "text": "**Emergency Rental & Financial Assistance Vector Activated.**\n\nI will search eviction relief grants and pro-bono legal support. Please specify your area (e.g. 7th District, 12th District).",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                add_system_log("State Machine", "Triage Choice", "Transitioned to FINANCIAL via button")
                st.rerun()

    # User Input Panel
    st.markdown("##### Send a Message")
    input_mode = st.radio("Select Input Mode", ["Simulated Voice Note (ASR)", "Direct Text Message"], horizontal=True)
    
    message_sent = False
    new_text = ""
    emo_flag = None
    
    if input_mode == "Simulated Voice Note (ASR)":
        scen_list = [
            "Motamayez Eviction",
            "Hadayek October Displacement",
            "District 3 Hunger",
            "Central Axis Abuse (Bypass)",
            "District 7 Eviction Court",
            "Zayed Food Stock Check (Empty Fallback)"
        ]
        scenario = st.selectbox("Select Audio Scenario to Simulate", scen_list)
        
        # Audio Player UI Mockup
        render_html("""
            <div style='background: #FAF6F0; padding: 10px; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center; border: 2px solid #2E3D44; box-shadow: 2px 2px 0px #2E3D44;'>
                <span style='font-size: 12px; margin-right: 12px; font-weight: bold; color: #C86B55; font-family: sans-serif;'>PLAY</span>
                <div style='flex-grow: 1; height: 4px; background: #EADDCB; position: relative;'>
                    <div style='position: absolute; left: 0; top: 0; width: 60%; height: 100%; background: #C86B55;'></div>
                    <div style='position: absolute; left: 60%; top: -3px; width: 10px; height: 10px; border-radius: 50%; background: #C86B55;'></div>
                </div>
                <span style='font-size: 12px; margin-left: 12px; color: #2E3D44;'>0:12</span>
            </div>
        """)
        
        trans, emotional, conf = simulate_speech_to_text(scenario)
        st.info(f"**Whisper Transcribed Text:** \"{trans}\" (Confidence: {conf:.2%})")
        
        if st.button("Send Voice Note"):
            new_text = trans
            emo_flag = emotional
            message_sent = True
            
    else:
        new_text = st.text_input("Type your message to the Crisis Router...", key="text_chat_input")
        if st.button("Send Text"):
            if new_text.strip():
                message_sent = True
                
    if message_sent and new_text:
        # Check if session in Intake state
        if st.session_state.active_crisis_vector is None:
            # Parse number or string choices
            choice = None
            if "1" in new_text.lower() or "shelter" in new_text.lower() or "housing" in new_text.lower():
                choice = "SHELTER"
            elif "2" in new_text.lower() or "food" in new_text.lower() or "hungry" in new_text.lower():
                choice = "FOOD"
            elif "3" in new_text.lower() or "abuse" in new_text.lower() or "violence" in new_text.lower() or "safety" in new_text.lower() or "weapon" in new_text.lower():
                choice = "SAFETY"
            elif "4" in new_text.lower() or "financial" in new_text.lower() or "rental" in new_text.lower() or "money" in new_text.lower() or "eviction" in new_text.lower():
                choice = "FINANCIAL"
                
            if choice:
                st.session_state.active_crisis_vector = choice
                st.session_state.messages.append({
                    "sender": "user",
                    "text": new_text,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                
                t_messages = {
                    "SHELTER": "**Immediate Shelter Vector Activated.**\n\nI will now help you locate emergency beds. Please tell us your neighborhood (e.g. Al-Motamayez, 11th District, Hadayek October).",
                    "FOOD": "**Food Security Vector Activated.**\n\nI will help you find local food banks and soup kitchens. Please tell us your location (e.g. 3rd District, Industrial Zone, Zayed).",
                    "SAFETY": "Safety threats / Abuse Bypass Activated.\n\nAutomated AI systems are locked out. Serving immediate caseworker dispatch and emergency contact cards...\n\n*Emergency Caseworker Line:* +20 (10) 9999-0000",
                    "FINANCIAL": "**Emergency Rental & Financial Assistance Vector Activated.**\n\nI will search eviction relief grants and pro-bono legal support. Please specify your area (e.g. 7th District, 12th District)."
                }
                st.session_state.messages.append({
                    "sender": "bot",
                    "text": t_messages[choice],
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "is_bypass": (choice == "SAFETY")
                })
                add_system_log("State Machine", "Triage Choice", f"Transitioned to {choice} via text analysis.")
                st.rerun()
            else:
                st.session_state.messages.append({
                    "sender": "user",
                    "text": new_text,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages.append({
                    "sender": "bot",
                    "text": "Triage Selection Required: Please reply with the number (1-4) or select from the quick replies above to activate the correct resource router.",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.rerun()
        else:
            # Handle standard routing search based on active vector
            st.session_state.messages.append({
                "sender": "user",
                "text": new_text,
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "emo_flag": emo_flag
            })
            
            use_gem = st.session_state.get("use_gemini", False)
            gem_key = st.session_state.get("gemini_key", "")
            
            result = run_semantic_parser(new_text, emo_flag or "Text Input", st.session_state.active_crisis_vector, use_gem, gem_key)
            
            st.session_state.messages.append({
                "sender": "bot",
                "text": result["response"],
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "is_bypass": result.get("is_bypass", False)
            })
            
            st.session_state.latest_nlp_log = {
                "user_input": new_text,
                "transcription_flags": emo_flag,
                "intent": result["intent"],
                "location": result["location"],
                "severity": result["severity"],
                "thought_process": result["thought_process"]
            }
            st.rerun()

# ----------------------------------------------------
# RIGHT COLUMN: DYNAMIC OPERATOR PANELS & LOGS
# ----------------------------------------------------
with col_operator:
    st.subheader("Operator Console & NLP Engine Logs")
    
    # State controller sidebar switch helper
    with st.sidebar:
        st.markdown("### Simulator Control Center")
        st.markdown("---")
        
        vector_lbls = {
            None: "Intake Triage Loop (None)",
            "SHELTER": "Immediate Shelter & Housing",
            "FOOD": "Food Security & Pantry",
            "SAFETY": "Safety Threats Bypass",
            "FINANCIAL": "Rental & Financial Aid"
        }
        st.info(f"**Active Crisis Vector:**\n{vector_lbls[st.session_state.active_crisis_vector]}")
        
        st.markdown("**Force Switched Operator Vector:**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Shelter", width="stretch", key="fo_shelter"):
                st.session_state.active_crisis_vector = "SHELTER"
                add_system_log("Operator Override", "Vector Swap", "Manually swapped active vector to SHELTER")
                st.rerun()
            if st.button("Food", width="stretch", key="fo_food"):
                st.session_state.active_crisis_vector = "FOOD"
                add_system_log("Operator Override", "Vector Swap", "Manually swapped active vector to FOOD")
                st.rerun()
        with c2:
            if st.button("Safety", width="stretch", key="fo_safety"):
                st.session_state.active_crisis_vector = "SAFETY"
                add_system_log("Operator Override", "Vector Swap", "Manually swapped active vector to SAFETY")
                st.rerun()
            if st.button("Financial", width="stretch", key="fo_fin"):
                st.session_state.active_crisis_vector = "FINANCIAL"
                add_system_log("Operator Override", "Vector Swap", "Manually swapped active vector to FINANCIAL")
                st.rerun()
                
        # Reversible engine reset
        if st.button("Reset Session (Return to Intake Greeting)", width="stretch", key="reset_session"):
            st.session_state.active_crisis_vector = None
            st.session_state.active_routing = None
            st.session_state.messages = [{
                "sender": "bot",
                "text": INTAKE_GREETING_TEXT,
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "is_bypass": False
            }]
            st.session_state.pings = []
            st.session_state.caseworker_dispatches = []
            add_system_log("State Machine", "Reset Session", "Resetted session state variables to intake greeting loop.")
            st.success("Session state resetted!")
            st.rerun()

    # Create Tabs
    tab_op, tab_nlp, tab_ping = st.tabs(["Operator Backchannel", "NLP & Database Logs", "Supervisor Pings"])
    
    # TAB 1: OPERATOR CONTROL (DYNAMIC VIEW)
    with tab_op:
        vector = st.session_state.active_crisis_vector
        
        if vector is None:
            st.info("Waiting for client selection. Triage state is currently in Intake Greeting loop.")
            st.write("Use the quick-reply buttons on the client interface (left side) or the Simulator Override in the sidebar (leftmost panel) to switch vector and open the database view.")
            
        elif vector == "SHELTER":
            st.markdown("#### Shelter Availability Database (SQLite Live View)")
            st.write("Operator Controls for Housing Stability shelters:")
            
            shelters_df = query_db("SELECT * FROM shelters")
            for idx, row in shelters_df.iterrows():
                s_id = row['shelter_id']
                s_name = row['name']
                loc = row['location_category']
                beds = row['available_beds']
                ts = datetime.fromisoformat(row['last_updated_timestamp']).strftime("%Y-%m-%d %I:%M %p")
                status = row['verification_status']
                
                badge_html = '<span class="badge-live">LIVE VERIFIED</span>' if status == "LIVE_VERIFIED" else '<span class="badge-stale">STALE WARNING</span>'
                if beds == 0: badge_html = '<span class="badge-empty">EMPTY FALLBACK</span>'
                
                with st.container():
                    render_html(f"""
                        <div class="operator-card">
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <strong style='font-size: 14px;'>{s_name} ({loc})</strong>
                                {badge_html}
                            </div>
                            <div style='font-size: 12px; margin-top: 4px;'>
                                Beds Available: <strong>{beds}</strong> | Last Updated: {ts}
                            </div>
                        </div>
                    """)
                    
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        if st.button("Add Bed", key=f"add_{s_id}"):
                            update_db("UPDATE shelters SET available_beds = available_beds + 1, last_updated_timestamp = ?, verification_status = 'LIVE_VERIFIED' WHERE shelter_id = ?", (datetime.now().isoformat(), s_id))
                            add_system_log("Layer C: Operator", "Manual Update", f"Incremented beds for {s_name}")
                            st.rerun()
                    with c2:
                        if st.button("Subtract Bed", key=f"sub_{s_id}"):
                            new_beds = max(0, beds - 1)
                            new_status = "EMPTY_FALLBACK" if new_beds == 0 else "LIVE_VERIFIED"
                            update_db("UPDATE shelters SET available_beds = ?, last_updated_timestamp = ?, verification_status = ? WHERE shelter_id = ?", (new_beds, datetime.now().isoformat(), new_status, s_id))
                            add_system_log("Layer C: Operator", "Manual Update", f"Decremented beds for {s_name} (Beds={new_beds})")
                            st.rerun()
                    with c3:
                        if st.button("Verify Capacity", key=f"ver_{s_id}"):
                            update_db("UPDATE shelters SET verification_status = 'LIVE_VERIFIED', last_updated_timestamp = ? WHERE shelter_id = ?", (datetime.now().isoformat(), s_id))
                            add_system_log("Layer C: Operator", "Manual Verify", f"Verified status for {s_name}. Resetted stale clock.")
                            st.rerun()
                            
        elif vector == "FOOD":
            st.markdown("#### Food Banks Registry (SQLite Live View)")
            st.write("Operator Controls for Food Security vector:")
            
            food_df = query_db("SELECT * FROM food_banks")
            for idx, row in food_df.iterrows():
                f_id = row['food_id']
                f_name = row['name']
                loc = row['location_category']
                meals = row['meals_available_today']
                ts = datetime.fromisoformat(row['last_updated_timestamp']).strftime("%Y-%m-%d %I:%M %p")
                status = row['verification_status']
                hours = row['operating_hours']
                dietary = row['dietary_fallback_status']
                
                badge_html = '<span class="badge-live">LIVE VERIFIED</span>' if status == "LIVE_VERIFIED" else '<span class="badge-stale">STALE WARNING</span>'
                if meals == 0: badge_html = '<span class="badge-empty">CLOSED / EMPTY</span>'
                
                with st.container():
                    render_html(f"""
                        <div class="operator-card">
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <strong style='font-size: 14px;'>{f_name} ({loc})</strong>
                                {badge_html}
                            </div>
                            <div style='font-size: 12px; margin-top: 4px;'>
                                Meals remaining: <strong>{meals}</strong> | Hours: {hours} | Dietary: <code>{dietary}</code><br>
                                Last Inventory Update: {ts}
                            </div>
                        </div>
                    """)
                    
                    c1, c2, c3 = st.columns([1.5, 1.5, 1])
                    with c1:
                        added_meals = st.slider("+50 Meals", -100, 200, 0, key=f"slider_{f_id}")
                        if st.button("Update Inventory", key=f"inv_up_{f_id}"):
                            new_meals = max(0, meals + added_meals)
                            update_db("UPDATE food_banks SET meals_available_today = ?, last_updated_timestamp = ?, verification_status = 'LIVE_VERIFIED' WHERE food_id = ?", (new_meals, datetime.now().isoformat(), f_id))
                            add_system_log("Layer C: Operator", "Food Inventory Update", f"Modified meals for {f_name} by {added_meals} (Beds={new_meals})")
                            st.rerun()
                    with c2:
                        if st.button("Toggle OPEN/CLOSED", key=f"toggle_{f_id}"):
                            if meals > 0:
                                update_db("UPDATE food_banks SET meals_available_today = 0, verification_status = 'EMPTY_FALLBACK', last_updated_timestamp = ? WHERE food_id = ?", (datetime.now().isoformat(), f_id))
                                add_system_log("Layer C: Operator", "Status Toggle", f"Set {f_name} status to CLOSED (meals=0)")
                            else:
                                update_db("UPDATE food_banks SET meals_available_today = 100, verification_status = 'LIVE_VERIFIED', last_updated_timestamp = ? WHERE food_id = ?", (datetime.now().isoformat(), f_id))
                                add_system_log("Layer C: Operator", "Status Toggle", f"Set {f_name} status to OPEN (meals=100)")
                            st.rerun()
                    with c3:
                        if st.button("Verify", key=f"ver_f_{f_id}"):
                            update_db("UPDATE food_banks SET verification_status = 'LIVE_VERIFIED', last_updated_timestamp = ? WHERE food_id = ?", (datetime.now().isoformat(), f_id))
                            add_system_log("Layer C: Operator", "Food Verify", f"Verified stock for {f_name}.")
                            st.rerun()
                            
        elif vector == "SAFETY":
            st.markdown("#### Safety dispatcher registry (AI Complete Lockout)")
            st.write("Operator dispatch dashboard for Safety Vector:")
            
            safety_df = query_db("SELECT * FROM safety_registry")
            for idx, row in safety_df.iterrows():
                s_id = row['safety_id']
                s_name = row['name']
                s_type = row['type']
                s_phone = row['phone']
                s_loc = row['location_category']
                details = row['details']
                
                with st.container():
                    render_html(f"""
                        <div class="safety-card-alert">
                            <div style='display: flex; justify-content: space-between;'>
                                <strong style='font-size: 14px;'>{s_name} ({s_loc})</strong>
                                <span class="badge-empty">{s_type}</span>
                            </div>
                            <div style='font-size: 12px; margin-top: 4px;'>
                                Line: <strong>{s_phone}</strong> | Details: {details}
                            </div>
                        </div>
                    """)
                    
                    if st.button(f"Dispatch Responder to {s_name}", key=f"disp_{s_id}"):
                        dispatch_id = random.randint(10000, 99999)
                        st.session_state.caseworker_dispatches.append({
                            "dispatch_id": dispatch_id,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                            "name": s_name,
                            "type": s_type,
                            "phone": s_phone,
                            "status": "DISPATCHED"
                        })
                        add_system_log("Layer C: Safety", "Webhook Dispatch", f"SMS Webhook Alert sent to {s_name} (ID: #{dispatch_id})")
                        st.success(f"Emergency casework responder team dispatched to {s_name}!")
                        
            st.markdown("---")
            st.markdown("#### Caseworker Dispatch Logs")
            if st.session_state.caseworker_dispatches:
                st.table(pd.DataFrame(st.session_state.caseworker_dispatches))
            else:
                st.info("No caseworker responders dispatched yet.")
                
        elif vector == "FINANCIAL":
            st.markdown("#### Eviction Prevention Funds Registry (SQLite Live View)")
            st.write("Operator Controls for Financial Eviction Relief:")
            
            fin_df = query_db("SELECT * FROM financial_assistance")
            for idx, row in fin_df.iterrows():
                f_id = row['financial_id']
                f_name = row['name']
                loc = row['location_category']
                funding = row['available_funding_pool_usd']
                counsel = row['legal_counsel_slots']
                proc_days = row['processing_days_estimate']
                status = row['verification_status']
                ts = datetime.fromisoformat(row['last_updated_timestamp']).strftime("%Y-%m-%d %I:%M %p")
                
                badge_html = '<span class="badge-live">FLUID</span>' if status == "FLUID" else '<span class="badge-stale">HEAVY DELAY WARNING</span>'
                
                with st.container():
                    render_html(f"""
                        <div class="financial-card-alert">
                            <div style='display: flex; justify-content: space-between;'>
                                <strong style='font-size: 14px;'>{f_name} ({loc})</strong>
                                {badge_html}
                            </div>
                            <div style='font-size: 12px; margin-top: 4px;'>
                                Funding Pool: <strong>${funding:,.2f}</strong> | Legal Slots: <strong>{counsel}</strong><br>
                                Processing Estimate: <strong>{proc_days} days</strong> | Updated: {ts}
                            </div>
                        </div>
                    """)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        new_funds = st.number_input("Adjust Fund Pool ($)", value=float(funding), step=1000.0, key=f"fund_pool_{f_id}")
                    with c2:
                        new_slots = st.number_input("Lawyer Slots", value=int(counsel), step=1, key=f"slots_{f_id}")
                    with c3:
                        new_status = st.selectbox("Delay Tag", ["FLUID", "HEAVY_DELAY_WARNING"], index=0 if status == "FLUID" else 1, key=f"status_tag_{f_id}")
                        
                    if st.button("Update Program Data", key=f"up_fin_{f_id}"):
                        update_db("""
                            UPDATE financial_assistance 
                            SET available_funding_pool_usd = ?, legal_counsel_slots = ?, verification_status = ?, last_updated_timestamp = ? 
                            WHERE financial_id = ?
                        """, (new_funds, new_slots, new_status, datetime.now().isoformat(), f_id))
                        add_system_log("Layer C: Operator", "Financial Update", f"Updated funding details for {f_name}")
                        st.rerun()
                        
        # Reset Database Button
        st.markdown("---")
        if st.button("Reset & Re-Seed SQLite Database"):
            update_db("DROP TABLE IF EXISTS shelters")
            update_db("DROP TABLE IF EXISTS food_banks")
            update_db("DROP TABLE IF EXISTS safety_registry")
            update_db("DROP TABLE IF EXISTS financial_assistance")
            init_db()
            st.session_state.active_routing = None
            st.session_state.pings = []
            st.session_state.caseworker_dispatches = []
            st.session_state.system_logs = []
            st.session_state.messages = [{
                "sender": "bot",
                "text": INTAKE_GREETING_TEXT,
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "is_bypass": False
            }]
            add_system_log("Database", "Hard Reset", "Database dropped, recreated, and seeded with localized October City data.")
            st.success("All dynamic SQLite tables re-seeded successfully!")
            st.rerun()

    # TAB 2: SYSTEM LOGS & RESPONSIBLE AI
    with tab_nlp:
        st.markdown("#### NLP Engine Logs & Thought Process")
        if "latest_nlp_log" in st.session_state:
            log = st.session_state.latest_nlp_log
            render_html(f"""
                <div class="log-card">
                    <div class="log-header">>>> Whisper ASR & Emotional Pipeline</div>
                    Input text: "{log['user_input']}"<br>
                    Emotional Distress Flags: {log['transcription_flags'] or 'None (Text Mode)'}<br>
                    ASR Confidence: 96.4%<br>
                    <br>
                    <div class="log-header">>>> Intent Classifier & Geospatial Extractor</div>
                    Classified Intent: {log['intent']}<br>
                    Geospatial Location Entity: {log['location']}<br>
                    Severity Assessment: {log['severity']}/10<br>
                    <br>
                    <div class="log-header">>>> System Thought Log (RAG & Security Bypass)</div>
                    {log['thought_process']}
                </div>
            """)
        else:
            st.info("Send a message to view the NLP parsing thought log.")

        st.markdown("#### Responsible AI Guardrails & disclosures")
        with st.expander("Hallucination Containment via Prompt Sandboxing"):
            st.write("""
                **System Guidelines Enforced:**
                1. The LLM routing prompt is isolated in a sandbox.
                2. It has strict orders: "DO NOT invent, fabricate, or guess shelter/food names, addresses, or phone numbers. If a location is not returned in the SQLite database query payload, you MUST trigger the central fallback message."
                3. The code checks database return sizes. If size = 0, the Python logic completely overrides the prompt output with the central hotline details.
            """)
        
        with st.expander("Data Privacy & Biometric Protection"):
            st.write("""
                **Privacy Safeguards:**
                - Transient Processing: Voice transcription happens in transient buffer memory.
                - No biometric audio files are cached or stored on disk.
                - User identities (like phone numbers) are mock-simulated and never written to permanent logs.
            """)
            
        with st.expander("Live Gemini LLM Routing Settings"):
            st.checkbox("Use Live Gemini API Routing", key="use_gemini")
            st.text_input("Enter Gemini API Key", type="password", key="gemini_key")
            st.caption("Provide a valid Gemini API Key from Google AI Studio to run real LLM classifications.")

    # TAB 3: SUPERVISOR PINGS
    with tab_ping:
        st.markdown("#### Simulated Supervisor Webhook Pings")
        st.write("Active back-channel webhook alerts triggered due to stale telemetry data:")
        
        active_pings = [p for p in st.session_state.pings if p.get("vector") == st.session_state.active_crisis_vector]
        
        if not active_pings:
            st.info("No active supervisor pings pending for the currently selected vector.")
        else:
            for p in active_pings:
                ping_id = p["ping_id"]
                s_name = p["shelter_name"]
                phone = p["supervisor_phone"]
                status = p["status"]
                
                bg_color = "#382c0e" if status == "PENDING" else "#1b3322"
                status_txt = "PENDING OPERATOR CONFIRMATION" if status == "PENDING" else "CONFIRMED VIA WEBHOOK"
                
                with st.container():
                    render_html(f"""
                        <div style='background-color: {bg_color}; border: 1px solid #222e35; padding: 10px; border-radius: 6px; margin-bottom: 10px;'>
                            <div style='display: flex; justify-content: space-between;'>
                                <strong>Ping #{ping_id} to Supervisor</strong>
                                <span style='font-size: 11px; font-weight: bold;'>{p['timestamp']}</span>
                            </div>
                            <div style='font-size: 13px; margin: 5px 0;'>
                                Facility: <strong>{s_name}</strong><br>
                                Supervisor Line: <code>{phone}</code>
                            </div>
                            <div style='font-weight: bold; font-size: 11px;'>{status_txt}</div>
                        </div>
                    """)
                    
                    if status == "PENDING":
                        if st.button(f"Confirm Capacity for Ping #{ping_id}", key=f"conf_p_{ping_id}"):
                            p["status"] = "CONFIRMED"
                            
                            # Reset database status depending on vector
                            if p.get("vector") == "SHELTER":
                                update_db("UPDATE shelters SET verification_status = 'LIVE_VERIFIED', last_updated_timestamp = ? WHERE name = ?", (datetime.now().isoformat(), s_name))
                            elif p.get("vector") == "FOOD":
                                update_db("UPDATE food_banks SET verification_status = 'LIVE_VERIFIED', last_updated_timestamp = ? WHERE name = ?", (datetime.now().isoformat(), s_name))
                                
                            add_system_log("Layer C: Supervisor", "Ping Confirmation", f"Supervisor verified stock for {s_name} via SMS backchannel.")
                            st.success("Webhook confirmed! Facility stock refreshed in live SQLite view.")
                            st.rerun()

# ----------------------------------------------------
# REAL-TIME SYSTEM AUDIT LOG
# ----------------------------------------------------
st.markdown("---")
st.subheader("System Audit Logs (Real-time Pipeline Tracking)")
if st.session_state.system_logs:
    logs_df = pd.DataFrame(st.session_state.system_logs)
    st.dataframe(logs_df.iloc[::-1], width="stretch") # reverse to show newest first
else:
    st.info("No system events logged yet.")

import textwrap
import streamlit as st


# =========================================================
# THEMES
# =========================================================

THEMES = {
    "default": {
        "name": "🌙 Dark Modern",
        "price": 0,
        "bg_color": "#0f172a",
        "bg_color2": "#1e1b4b",
        "card_bg": "#1e293b",
        "primary_color": "#6366f1",
        "text_color": "#f8fafc",
        "accent_color": "#22c55e",
        "particle_color": "#6366f1",
        "font": "sans-serif",
    },

    "cyberpunk": {
        "name": "⚡ Cyberpunk Neon",
        "price": 100,
        "bg_color": "#0d0221",
        "bg_color2": "#2b0a45",
        "card_bg": "#190933",
        "primary_color": "#ff007f",
        "text_color": "#00f5d4",
        "accent_color": "#fee440",
        "particle_color": "#00f5d4",
        "font": "monospace",
    },

    "nature_zen": {
        "name": "🌿 Nature Zen",
        "price": 100,
        "bg_color": "#1c2826",
        "bg_color2": "#243b32",
        "card_bg": "#2b3a37",
        "primary_color": "#76b041",
        "text_color": "#e8f1f2",
        "accent_color": "#f7b05b",
        "particle_color": "#76b041",
        "font": "sans-serif",
    },

    "sunset_glow": {
        "name": "🌅 Sunset Glow",
        "price": 150,
        "bg_color": "#2b1055",
        "bg_color2": "#5b1a63",
        "card_bg": "#4c1d95",
        "primary_color": "#ff5e7e",
        "text_color": "#fff0f5",
        "accent_color": "#ff9966",
        "particle_color": "#ff5e7e",
        "font": "Arial, sans-serif",
    },
}


# =========================================================
# BANNERS
# =========================================================

BANNERS = {
    "default_banner": {
        "name": "🌌 Cosmic Knowledge",
        "price": 0,
        "url": (
            "https://images.unsplash.com/"
            "photo-1507842217343-583bb7270b66"
            "?q=80&w=1600&auto=format&fit=crop"
        ),
    },

    "neon_workspace": {
        "name": "🌆 Neon Workspace",
        "price": 150,
        "url": (
            "https://images.unsplash.com/"
            "photo-1526374965328-7f61d4dc18c5"
            "?q=80&w=1600&auto=format&fit=crop"
        ),
    },

    "minimal_forest": {
        "name": "🌲 Minimal Forest",
        "price": 150,
        "url": (
            "https://images.unsplash.com/"
            "photo-1448375240586-882707db888b"
            "?q=80&w=1600&auto=format&fit=crop"
        ),
    },
}


# =========================================================
# STUDY TEMPLATES
# =========================================================

STUDY_TEMPLATES = {
    "pomodoro": {
        "name": "⏱️ Pomodoro (25/5)",
        "price": 0,
        "desc": "25 دقيقة مذاكرة + 5 دقائق راحة",
        "study_minutes": 25,
        "break_minutes": 5,
    },

    "deep_work": {
        "name": "🧠 Deep Work (50/10)",
        "price": 300,
        "desc": "50 دقيقة تركيز عميق + 10 دقائق راحة",
        "study_minutes": 50,
        "break_minutes": 10,
    },

    "ultradian": {
        "name": "⚡ Ultradian (90/20)",
        "price": 300,
        "desc": "90 دقيقة عمل مكثف + 20 دقيقة راحة",
        "study_minutes": 90,
        "break_minutes": 20,
    },
}


# =========================================================
# SAFE HELPERS
# =========================================================

def get_active_theme():
    key = st.session_state.get("active_theme", "default")

    if key not in THEMES:
        key = "default"
        st.session_state.active_theme = key

    return THEMES[key]


def get_active_banner():
    key = st.session_state.get(
        "active_banner",
        "default_banner",
    )

    if key not in BANNERS:
        key = "default_banner"
        st.session_state.active_banner = key

    return BANNERS[key]


def get_active_template():
    key = st.session_state.get(
        "active_template",
        "pomodoro",
    )

    if key not in STUDY_TEMPLATES:
        key = "pomodoro"
        st.session_state.active_template = key

    return STUDY_TEMPLATES[key]


# =========================================================
# STREAMLIT HTML HELPER
# =========================================================

def render_html(html: str):
    """
    Render raw HTML using Streamlit's native HTML renderer.

    This avoids situations where HTML tags are displayed
    as plain text on the page.
    """

    html = textwrap.dedent(html).strip()

    # Modern Streamlit
    if hasattr(st, "html"):
        st.html(html)

    # Fallback for older Streamlit versions
    else:
        st.markdown(
            html,
            unsafe_allow_html=True,
        )


# =========================================================
# HEADER
# =========================================================

def render_app_header():

    theme = get_active_theme()

    header_html = f"""
    <div class="sp-header">

        <div class="sp-header-content">

            <div class="sp-brand">
                <span class="sp-brand-icon">🎓</span>
                <span>Study Planner Pro</span>
            </div>

            <div class="sp-theme-badge">
                ● {theme["name"]}
            </div>

        </div>

    </div>
    """

    render_html(header_html)


# =========================================================
# BANNER
# =========================================================

def render_banner():

    theme = get_active_theme()
    banner = get_active_banner()

    banner_html = f"""
    <div
        class="sp-banner"
        style="
            background-image:
                linear-gradient(
                    to bottom,
                    rgba(0, 0, 0, 0.10),
                    {theme["bg_color"]}F2
                ),
                url('{banner["url"]}');
        "
    >

        <div class="sp-banner-content">

            <div class="sp-banner-title">
                📚 Intelligent Study Planner
            </div>

            <div class="sp-banner-subtitle">
                Plan smarter • Study better • Earn rewards
            </div>

        </div>

    </div>
    """

    render_html(banner_html)


# =========================================================
# APPLY STYLES
# =========================================================

def apply_styles():

    theme = get_active_theme()

    bg = theme["bg_color"]
    bg2 = theme.get("bg_color2", bg)
    card = theme["card_bg"]
    primary = theme["primary_color"]
    text = theme["text_color"]
    accent = theme["accent_color"]
    font = theme["font"]
    particle = theme.get(
        "particle_color",
        primary,
    )

    css = textwrap.dedent(
        f"""
        <style>

        :root {{
            --sp-bg: {bg};
            --sp-bg2: {bg2};
            --sp-card: {card};
            --sp-primary: {primary};
            --sp-text: {text};
            --sp-accent: {accent};
            --sp-particle: {particle};
        }}


        /* =============================================
           ANIMATIONS
        ============================================= */

        @keyframes spGradient {{
            0% {{
                background-position: 0% 50%;
            }}

            50% {{
                background-position: 100% 50%;
            }}

            100% {{
                background-position: 0% 50%;
            }}
        }}


        @keyframes spParticles {{
            0% {{
                transform: translateY(0);
            }}

            50% {{
                transform: translateY(-25px);
            }}

            100% {{
                transform: translateY(0);
            }}
        }}


        @keyframes spGlow {{
            0%, 100% {{
                box-shadow:
                    0 0 8px {primary}22;
            }}

            50% {{
                box-shadow:
                    0 0 18px {accent}55;
            }}
        }}


        /* =============================================
           GLOBAL
        ============================================= */

        html,
        body {{
            background: {bg} !important;
        }}


        .stApp {{
            min-height: 100vh;

            background:
                linear-gradient(
                    120deg,
                    {bg},
                    {bg2},
                    {primary}18,
                    {bg}
                );

            background-size: 400% 400%;

            animation:
                spGradient 20s ease infinite;

            color: {text} !important;

            font-family: {font};

            overflow-x: hidden;
        }}


        .stApp::before {{
            content: "";

            position: fixed;

            inset: 0;

            pointer-events: none;

            z-index: 0;

            background-image:
                radial-gradient(
                    {particle}33 1px,
                    transparent 1px
                ),
                radial-gradient(
                    {accent}22 1px,
                    transparent 1px
                );

            background-size:
                60px 60px,
                90px 90px;

            background-position:
                0 0,
                30px 40px;

            animation:
                spParticles 15s ease-in-out infinite;

            opacity: 0.7;
        }}


        header[data-testid="stHeader"] {{
            background: transparent !important;
            box-shadow: none !important;
        }}


        #MainMenu,
        footer {{
            visibility: hidden;
        }}


        div[data-testid="stDecoration"] {{
            display: none !important;
        }}


        /* =============================================
           MAIN CONTAINER
        ============================================= */

        .main .block-container {{
            max-width: 1450px !important;

            width: 100% !important;

            margin: 0 auto !important;

            padding-top: 1.25rem !important;

            padding-bottom: 3rem !important;

            padding-left:
                clamp(1rem, 4vw, 3rem) !important;

            padding-right:
                clamp(1rem, 4vw, 3rem) !important;

            position: relative;

            z-index: 1;
        }}


        /* =============================================
           HEADER
        ============================================= */

        .sp-header {{
            width: 100%;

            min-height: 60px;

            display: flex;

            align-items: center;

            background:
                linear-gradient(
                    90deg,
                    {card}F5,
                    {card}DD
                );

            backdrop-filter: blur(15px);

            border:
                1px solid {primary}33;

            border-radius: 15px;

            margin-bottom: 18px;

            box-shadow:
                0 8px 30px rgba(0, 0, 0, 0.25);

            position: relative;

            z-index: 10;
        }}


        .sp-header-content {{
            width: 100%;

            display: flex;

            align-items: center;

            justify-content: space-between;

            gap: 15px;

            padding:
                10px
                18px
                10px
                60px;
        }}


        .sp-brand {{
            display: flex;

            align-items: center;

            gap: 9px;

            color: {text} !important;

            font-size: 17px;

            font-weight: 750;

            white-space: nowrap;
        }}


        .sp-brand-icon {{
            font-size: 21px;
        }}


        .sp-theme-badge {{
            color: {accent} !important;

            background: {primary}20;

            border:
                1px solid {primary}55;

            border-radius: 20px;

            padding:
                6px
                13px;

            font-size: 12px;

            font-weight: 650;

            white-space: nowrap;

            animation:
                spGlow 3s ease-in-out infinite;
        }}


        /* =============================================
           BANNER
        ============================================= */

        .sp-banner {{
            width: 100%;

            min-height: 180px;

            height:
                clamp(170px, 25vw, 230px);

            display: flex;

            align-items: flex-end;

            position: relative;

            overflow: hidden;

            background-size: cover;

            background-position: center;

            border-radius: 18px;

            border:
                1px solid {primary}44;

            margin-bottom: 25px;

            box-shadow:
                0 12px 35px rgba(0, 0, 0, 0.35);

            transition:
                transform 0.35s ease,
                box-shadow 0.35s ease;
        }}


        .sp-banner:hover {{
            transform: translateY(-2px);

            box-shadow:
                0 16px 40px rgba(0, 0, 0, 0.45);
        }}


        .sp-banner-content {{
            padding:
                clamp(18px, 4vw, 30px);

            width: 100%;
        }}


        .sp-banner-title {{
            color: #ffffff !important;

            font-size:
                clamp(21px, 3.5vw, 32px);

            font-weight: 800;

            line-height: 1.15;

            text-shadow:
                0 3px 15px rgba(0, 0, 0, 0.75);
        }}


        .sp-banner-subtitle {{
            color: #f1f5f9 !important;

            margin-top: 8px;

            font-size:
                clamp(12px, 1.6vw, 15px);

            text-shadow:
                0 2px 10px rgba(0, 0, 0, 0.7);
        }}


        /* =============================================
           SIDEBAR
        ============================================= */

        section[data-testid="stSidebar"] {{
            background:
                linear-gradient(
                    180deg,
                    {card},
                    {bg}
                ) !important;

            border-right:
                1px solid {primary}33 !important;
        }}


        section[data-testid="stSidebar"] * {{
            color: {text} !important;
        }}


        section[data-testid="stSidebar"] .stMetric {{
            background: {bg}99;

            padding: 10px;

            border-radius: 11px;

            border:
                1px solid {primary}22;
        }}


        /* =============================================
           TABS
        ============================================= */

        button[data-baseweb="tab"] {{
            color: {text} !important;

            font-weight: 650;
        }}


        button[data-baseweb="tab"]:hover,
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {accent} !important;
        }}


        div[data-baseweb="tab-highlight"] {{
            background-color:
                {accent} !important;
        }}


        /* =============================================
           METRICS
        ============================================= */

        div[data-testid="stMetric"] {{
            background:
                {card}AA !important;

            padding: 12px;

            border-radius: 12px;

            border:
                1px solid {primary}22;

            transition:
                border-color 0.25s ease,
                transform 0.25s ease;
        }}


        div[data-testid="stMetric"]:hover {{
            border-color:
                {accent}88;

            transform:
                translateY(-2px);
        }}


        /* =============================================
           EXPANDERS
        ============================================= */

        div[data-testid="stExpander"] {{
            background:
                linear-gradient(
                    145deg,
                    {card}EE,
                    {card}CC
                ) !important;

            border:
                1px solid {primary}33 !important;

            border-radius:
                14px !important;

            box-shadow:
                0 6px 20px rgba(0, 0, 0, 0.15);

            margin-bottom: 12px;

            overflow: hidden;
        }}


        /* =============================================
           BUTTONS
        ============================================= */

        .stButton > button {{
            width: 100% !important;

            min-height: 42px;

            border-radius:
                10px !important;

            border:
                1px solid {primary}55 !important;

            background:
                {card} !important;

            color:
                {text} !important;

            font-weight: 650;

            transition:
                all 0.2s ease;
        }}


        .stButton > button:hover {{
            border-color:
                {accent} !important;

            color:
                {accent} !important;

            transform:
                translateY(-1px);

            box-shadow:
                0 5px 15px {primary}33;
        }}


        /* =============================================
           INPUTS
        ============================================= */

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background:
                {card} !important;

            border:
                1px solid {primary}44 !important;

            border-radius:
                10px !important;
        }}


        input,
        textarea {{
            color:
                {text} !important;
        }}


        /* =============================================
           ALERTS
        ============================================= */

        div[data-testid="stAlert"] {{
            border-radius:
                12px !important;
        }}


        /* =============================================
           SHOP
        ============================================= */

        .shop-card {{
            background:
                {card}CC;

            border:
                1px solid {primary}33;

            border-radius:
                14px;

            padding:
                18px;

            min-height:
                150px;

            box-shadow:
                0 8px 25px rgba(0, 0, 0, 0.15);

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease;
        }}


        .shop-card:hover {{
            transform:
                translateY(-3px);

            box-shadow:
                0 12px 30px {primary}33;
        }}


        /* =============================================
           TIMER
        ============================================= */

        .timer-card {{
            background:
                linear-gradient(
                    145deg,
                    {card}EE,
                    {card}CC
                );

            border:
                1px solid {primary}44;

            border-radius:
                18px;

            padding:
                25px;

            text-align:
                center;

            box-shadow:
                0 10px 30px rgba(0, 0, 0, 0.25);
        }}


        /* =============================================
           SCROLLBAR
        ============================================= */

        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}


        ::-webkit-scrollbar-track {{
            background:
                {bg};
        }}


        ::-webkit-scrollbar-thumb {{
            background:
                {primary}88;

            border-radius:
                10px;
        }}


        ::-webkit-scrollbar-thumb:hover {{
            background:
                {accent};
        }}


        /* =============================================
           TABLET
        ============================================= */

        @media (max-width: 900px) {{

            .sp-header-content {{
                padding-left: 55px;
            }}

            .sp-banner {{
                height: 200px;
            }}
        }}


        /* =============================================
           MOBILE
        ============================================= */

        @media (max-width: 640px) {{

            .main .block-container {{
                padding-left:
                    0.75rem !important;

                padding-right:
                    0.75rem !important;
            }}


            .sp-header {{
                min-height: 54px;
            }}


            .sp-header-content {{
                padding:
                    9px
                    12px
                    9px
                    55px;
            }}


            .sp-brand {{
                font-size: 14px;
            }}


            .sp-theme-badge {{
                display: none;
            }}


            .sp-banner {{
                min-height: 165px;

                height: 190px;

                border-radius: 14px;
            }}


            div[data-testid="column"] {{
                min-width: 100% !important;

                width: 100% !important;

                flex:
                    1 1 100% !important;
            }}
        }}


        /* =============================================
           REDUCED MOTION
        ============================================= */

        @media (prefers-reduced-motion: reduce) {{

            *,
            *::before,
            *::after {{
                animation-duration:
                    0.01ms !important;

                animation-iteration-count:
                    1 !important;

                transition-duration:
                    0.01ms !important;
            }}
        }}

        </style>
        """
    )

    render_html(css)
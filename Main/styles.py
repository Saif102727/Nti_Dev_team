import html as html_lib
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
            "https://6a9e5c12b9f3f1e956cb1136.imgix.net/"
            "%F0%9F%8C%86-Neon-study_banner-588013.png"
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
# COURSES
# =========================================================
#
# Difficulty badge + prerequisite "chips" used on the Courses tab,
# instead of a plain difficulty number and a comma-separated string.

COURSE_DIFFICULTY_STYLES = {
    1: {"emoji": "🟢", "label": "Very Easy", "color": "#34d399"},
    2: {"emoji": "🟢", "label": "Easy", "color": "#4ade80"},
    3: {"emoji": "🟡", "label": "Moderate", "color": "#fbbf24"},
    4: {"emoji": "🟠", "label": "Hard", "color": "#fb923c"},
    5: {"emoji": "🔴", "label": "Very Hard", "color": "#f87171"},
}

DEFAULT_DIFFICULTY_STYLE = {
    "emoji": "⚪",
    "label": "Unrated",
    "color": "#94a3b8",
}


def get_difficulty_style(level) -> dict:
    try:
        level = int(level)
    except (TypeError, ValueError):
        level = 0

    return COURSE_DIFFICULTY_STYLES.get(level, DEFAULT_DIFFICULTY_STYLE)


def render_prerequisite_chips(prerequisites):

    if not prerequisites:
        st.caption("No prerequisites required.")
        return

    chips_html = "".join(
        f'<span class="prereq-chip">{html_lib.escape(str(item))}</span>'
        for item in prerequisites
    )

    render_html(
        f"""
        <div class="prereq-chip-row">
            {chips_html}
        </div>
        """
    )


# =========================================================
# ACADEMIC EVENTS
# =========================================================
#
# Renders academic events (assignments, quizzes, midterms, finals...)
# as a themed, week-grouped timeline instead of plain text lines.

EVENT_TYPE_STYLES = {
    "quiz": {"icon": "🧩", "label": "Quiz", "color": "#38bdf8"},
    "assignment": {"icon": "📝", "label": "Assignment", "color": "#34d399"},
    "midterm": {"icon": "📘", "label": "Midterm", "color": "#fbbf24"},
    "final": {"icon": "🎓", "label": "Final", "color": "#f87171"},
    "project": {"icon": "🛠️", "label": "Project", "color": "#a78bfa"},
    "exam": {"icon": "🧾", "label": "Exam", "color": "#fb923c"},
}

DEFAULT_EVENT_STYLE = {"icon": "📌", "label": "Event", "color": "#818cf8"}


def get_event_style(event_name: str) -> dict:
    lowered = (event_name or "").lower()

    for keyword, style in EVENT_TYPE_STYLES.items():
        if keyword in lowered:
            return style

    return DEFAULT_EVENT_STYLE


def _event_value(item, key, default=None):
    """Supports both dataclass/object data and dictionaries."""

    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)


def render_academic_events(events):

    if not events:
        st.info("No academic events available.")
        return

    grouped: dict[int, list] = {}

    for event in events:

        try:
            week = int(
                _event_value(event, "week_number", 0) or 0
            )
        except (TypeError, ValueError):
            week = 0

        grouped.setdefault(week, []).append(event)

    weeks_sorted = sorted(grouped.keys())

    week_rows_html = []

    for week in weeks_sorted:

        event_cards_html = []

        for event in grouped[week]:

            event_name = str(
                _event_value(event, "event_name", "Event")
            )

            course_id = str(
                _event_value(event, "course_id", "N/A")
            )

            style = get_event_style(event_name)

            event_cards_html.append(
                f"""
                <div class="event-card" style="--event-color: {style['color']};">
                    <div class="event-card-badge">
                        {style['icon']} {html_lib.escape(style['label'])}
                    </div>
                    <div class="event-card-name">
                        {html_lib.escape(event_name)}
                    </div>
                    <div class="event-card-course">
                        📚 {html_lib.escape(course_id)}
                    </div>
                </div>
                """
            )

        week_rows_html.append(
            f"""
            <div class="event-week-row">
                <div class="event-week-marker">
                    <div class="event-week-dot"></div>
                    <div class="event-week-label">Week {week}</div>
                </div>
                <div class="event-week-cards">
                    {''.join(event_cards_html)}
                </div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="event-timeline">
            {''.join(week_rows_html)}
        </div>
        """
    )


# =========================================================
# SHOP — PREVIEW CARDS
# =========================================================
#
# One shared visual system for every purchasable item in the shop
# (Banners, Themes, Study Templates): a media box (image / color
# swatch / ratio bar depending on the item type) topped with a
# status ribbon, and a dark-gradient overlay carrying the name +
# the "💎 N Points" badge. The actual "Use" / "Buy" button stays a
# real st.button rendered right after this, since Streamlit widgets
# can't live inside raw HTML.

SHOP_STATUS_STYLES = {
    "active": ("✓ Active", "is-active"),
    "owned": ("Owned", "is-owned"),
    "locked": ("🔒 Locked", "is-locked"),
}


def _shop_status(status: str):
    return SHOP_STATUS_STYLES.get(
        status,
        SHOP_STATUS_STYLES["locked"],
    )


def _render_shop_preview_card(media_html: str, name: str, price, status: str):

    label, css_class = _shop_status(status)

    render_html(
        f"""
        <div class="shop-preview-card">
            <div class="shop-preview-media">
                {media_html}
                <div class="shop-preview-status {css_class}">
                    {label}
                </div>
                <div class="shop-preview-overlay">
                    <div class="shop-preview-title">
                        {html_lib.escape(str(name))}
                    </div>
                    <div class="shop-preview-price">
                        💎 {price} Points
                    </div>
                </div>
            </div>
        </div>
        """
    )


# ---------------------------------------------------------
# Banners — the media is the actual banner image
# ---------------------------------------------------------

def render_shop_banner_card(item: dict, status: str = "locked"):

    name = item.get("name", "Banner")
    price = item.get("price", 0)
    url = html_lib.escape(str(item.get("url", "")), quote=True)

    media_html = f"""
    <img
        class="shop-preview-image"
        src="{url}"
        alt="{html_lib.escape(str(name))}"
        loading="lazy"
        onerror="
            this.style.display='none';
            this.parentElement.classList.add('shop-preview-media-error');
        "
    />
    """

    _render_shop_preview_card(media_html, name, price, status)


# ---------------------------------------------------------
# Themes — the media is a live swatch of the theme's own colors
# ---------------------------------------------------------

def render_shop_theme_card(item: dict, status: str = "locked"):

    name = item.get("name", "Theme")
    price = item.get("price", 0)

    bg = item.get("bg_color", "#1e293b")
    bg2 = item.get("bg_color2", bg)
    primary = item.get("primary_color", "#6366f1")
    accent = item.get("accent_color", "#22c55e")
    card = item.get("card_bg", bg)

    media_html = f"""
    <div
        class="theme-swatch"
        style="background: linear-gradient(135deg, {bg}, {bg2});"
    >
        <span class="theme-swatch-dot" style="background:{primary};"></span>
        <span class="theme-swatch-dot" style="background:{accent};"></span>
        <span class="theme-swatch-dot" style="background:{card};"></span>
    </div>
    """

    _render_shop_preview_card(media_html, name, price, status)


# ---------------------------------------------------------
# Study templates — the media is a study/break ratio bar
# ---------------------------------------------------------

def render_shop_template_card(item: dict, status: str = "locked"):

    theme = get_active_theme()
    primary = theme["primary_color"]
    accent = theme["accent_color"]

    name = item.get("name", "Template")
    price = item.get("price", 0)

    try:
        study_minutes = max(0, int(item.get("study_minutes", 0)))
    except (TypeError, ValueError):
        study_minutes = 0

    try:
        break_minutes = max(0, int(item.get("break_minutes", 0)))
    except (TypeError, ValueError):
        break_minutes = 0

    total_minutes = max(1, study_minutes + break_minutes)
    study_pct = round(study_minutes / total_minutes * 100)
    break_pct = 100 - study_pct

    media_html = f"""
    <div
        class="template-visual"
        style="background: linear-gradient(135deg, {primary}, {accent});"
    >
        <div class="template-ratio-bar">
            <div
                class="template-ratio-segment"
                style="width: {study_pct}%; background: rgba(255,255,255,0.92);"
            ></div>
            <div
                class="template-ratio-segment"
                style="width: {break_pct}%; background: rgba(255,255,255,0.28);"
            ></div>
        </div>
        <div class="template-ratio-labels">
            <span>🧠 {study_minutes}m focus</span>
            <span>☕ {break_minutes}m break</span>
        </div>
    </div>
    """

    _render_shop_preview_card(media_html, name, price, status)




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
           SHOP — PREVIEW CARDS (banners / themes / templates)
        ============================================= */

        .shop-preview-card {{
            border-radius: 16px;

            overflow: hidden;

            margin-bottom: 10px;

            border:
                1px solid {primary}33;

            box-shadow:
                0 10px 28px rgba(0, 0, 0, 0.25);

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease,
                border-color 0.25s ease;
        }}


        .shop-preview-card:hover {{
            transform:
                translateY(-4px);

            border-color:
                {accent}88;

            box-shadow:
                0 16px 36px {primary}40;
        }}


        .shop-preview-media {{
            position: relative;

            width: 100%;

            aspect-ratio: 16 / 9;

            background:
                linear-gradient(
                    145deg,
                    {card},
                    {bg}
                );
        }}


        .shop-preview-image {{
            width: 100%;

            height: 100%;

            object-fit: cover;

            display: block;
        }}


        .shop-preview-media-error {{
            display: flex;

            align-items: center;

            justify-content: center;
        }}


        .shop-preview-media-error::after {{
            content: "🖼️ Preview unavailable";

            font-size: 13px;

            font-weight: 600;

            color: {text};

            opacity: 0.55;
        }}


        .shop-preview-overlay {{
            position: absolute;

            left: 0;

            right: 0;

            bottom: 0;

            padding: 34px 16px 12px;

            background:
                linear-gradient(
                    to top,
                    rgba(0, 0, 0, 0.88),
                    rgba(0, 0, 0, 0.15) 65%,
                    rgba(0, 0, 0, 0) 100%
                );
        }}


        .shop-preview-title {{
            color: #ffffff !important;

            font-size: 15px;

            font-weight: 750;

            line-height: 1.25;

            text-shadow:
                0 2px 10px rgba(0, 0, 0, 0.65);
        }}


        .shop-preview-price {{
            display: inline-block;

            margin-top: 6px;

            font-size: 11.5px;

            font-weight: 650;

            color: #ffffff;

            background: {primary}CC;

            padding: 3px 10px;

            border-radius: 999px;

            backdrop-filter: blur(4px);
        }}


        .shop-preview-status {{
            position: absolute;

            top: 10px;

            right: 10px;

            font-size: 11px;

            font-weight: 700;

            letter-spacing: 0.3px;

            padding: 4px 11px;

            border-radius: 999px;

            backdrop-filter: blur(6px);

            z-index: 2;
        }}


        .shop-preview-status.is-active {{
            background: {accent}E6;

            color: #0f172a;
        }}


        .shop-preview-status.is-owned {{
            background: rgba(255, 255, 255, 0.16);

            color: #ffffff;

            border:
                1px solid rgba(255, 255, 255, 0.35);
        }}


        .shop-preview-status.is-locked {{
            background: rgba(0, 0, 0, 0.55);

            color: #f1f5f9;

            border:
                1px solid rgba(255, 255, 255, 0.2);
        }}


        /* -----------------------------------------------
           THEME SWATCH (media content for Theme cards)
        ----------------------------------------------- */

        .theme-swatch {{
            width: 100%;

            height: 100%;

            display: flex;

            align-items: center;

            justify-content: center;

            gap: 10px;
        }}


        .theme-swatch-dot {{
            width: 22px;

            height: 22px;

            border-radius: 50%;

            border:
                2px solid rgba(255, 255, 255, 0.55);

            box-shadow:
                0 3px 10px rgba(0, 0, 0, 0.35);
        }}


        /* -----------------------------------------------
           TEMPLATE RATIO VISUAL (media content for
           Study Template cards)
        ----------------------------------------------- */

        .template-visual {{
            width: 100%;

            height: 100%;

            display: flex;

            flex-direction: column;

            align-items: center;

            justify-content: center;

            gap: 10px;

            padding: 0 22px;
        }}


        .template-ratio-bar {{
            width: 100%;

            max-width: 220px;

            height: 10px;

            display: flex;

            border-radius: 999px;

            overflow: hidden;

            box-shadow:
                0 3px 10px rgba(0, 0, 0, 0.25);
        }}


        .template-ratio-segment {{
            height: 100%;
        }}


        .template-ratio-labels {{
            width: 100%;

            max-width: 220px;

            display: flex;

            justify-content: space-between;

            font-size: 12px;

            font-weight: 650;

            color: #ffffff;

            text-shadow:
                0 2px 8px rgba(0, 0, 0, 0.35);
        }}


        /* =============================================
           COURSES — PREREQUISITE CHIPS
        ============================================= */

        .prereq-chip-row {{
            display: flex;

            flex-wrap: wrap;

            gap: 8px;

            margin-top: 4px;
        }}


        .prereq-chip {{
            display: inline-block;

            font-size: 12.5px;

            font-weight: 600;

            color: {text};

            background: {primary}1F;

            border:
                1px solid {primary}55;

            border-radius: 999px;

            padding: 4px 12px;
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
           ACADEMIC EVENTS
        ============================================= */

        .event-timeline {{
            position: relative;

            padding-left: 4px;

            margin-top: 6px;
        }}


        .event-week-row {{
            display: flex;

            align-items: flex-start;

            gap: 16px;

            margin-bottom: 20px;
        }}


        .event-week-marker {{
            display: flex;

            flex-direction: column;

            align-items: center;

            min-width: 64px;

            position: relative;
        }}


        .event-week-dot {{
            width: 12px;

            height: 12px;

            border-radius: 50%;

            background: {accent};

            box-shadow:
                0 0 0 4px {accent}33;

            margin-bottom: 6px;
        }}


        .event-week-row:not(:last-child)
        .event-week-marker::after {{
            content: "";

            position: absolute;

            top: 18px;

            bottom: -20px;

            width: 2px;

            background:
                linear-gradient(
                    to bottom,
                    {primary}66,
                    {primary}11
                );
        }}


        .event-week-label {{
            font-size: 12px;

            font-weight: 700;

            color: {text};

            opacity: 0.85;

            white-space: nowrap;
        }}


        .event-week-cards {{
            flex: 1;

            display: flex;

            flex-wrap: wrap;

            gap: 10px;
        }}


        .event-card {{
            background:
                linear-gradient(
                    145deg,
                    {card}EE,
                    {card}CC
                );

            border:
                1px solid var(--event-color, {primary});

            border-left:
                4px solid var(--event-color, {primary});

            border-radius: 12px;

            padding: 10px 14px;

            min-width: 180px;

            box-shadow:
                0 4px 14px rgba(0, 0, 0, 0.15);

            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease;
        }}


        .event-card:hover {{
            transform:
                translateY(-2px);

            box-shadow:
                0 8px 20px
                var(--event-color, {primary})33;
        }}


        .event-card-badge {{
            display: inline-block;

            font-size: 11px;

            font-weight: 700;

            letter-spacing: 0.3px;

            color: var(--event-color, {primary});

            background:
                var(--event-color, {primary})1A;

            padding: 2px 8px;

            border-radius: 999px;

            margin-bottom: 6px;
        }}


        .event-card-name {{
            font-size: 14px;

            font-weight: 650;

            color: {text};

            margin-bottom: 2px;
        }}


        .event-card-course {{
            font-size: 12px;

            color: {text};

            opacity: 0.65;
        }}


        @media (max-width: 640px) {{

            .event-week-row {{
                flex-direction: column;

                gap: 8px;
            }}

            .event-week-marker {{
                flex-direction: row;

                min-width: auto;
            }}

            .event-week-dot {{
                margin-bottom: 0;

                margin-right: 6px;
            }}

            .event-week-row:not(:last-child)
            .event-week-marker::after {{
                display: none;
            }}
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
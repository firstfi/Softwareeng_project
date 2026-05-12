import hashlib
import sqlite3
from datetime import date, timedelta

import streamlit as st

st.set_page_config(
    page_title="StudySync",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Database ──────────────────────────────────────────────────────────────────

DB = "users.db"


def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    conn = get_conn()
    conn.cursor().executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT NOT NULL,
            exam_date   TEXT,
            estimated_h REAL DEFAULT 10,
            color       TEXT DEFAULT '#7C6DF8',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            subject_id  INTEGER NOT NULL,
            study_date  TEXT NOT NULL,
            duration    INTEGER NOT NULL,
            confidence  INTEGER DEFAULT 3,
            FOREIGN KEY (user_id)    REFERENCES users(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        );
        CREATE TABLE IF NOT EXISTS streaks (
            user_id         INTEGER PRIMARY KEY,
            last_study_date TEXT,
            current_streak  INTEGER DEFAULT 0,
            max_streak      INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


init_db()

# ── Auth ──────────────────────────────────────────────────────────────────────

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, _hash(password)))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_conn()
    row = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (username, _hash(password))).fetchone()
    conn.close()
    return row[0] if row else None

# ── Data helpers ──────────────────────────────────────────────────────────────

def get_subjects(uid):
    conn = get_conn()
    rows = conn.execute("SELECT id,name,exam_date,estimated_h,color FROM subjects WHERE user_id=? ORDER BY exam_date", (uid,)).fetchall()
    conn.close(); return rows

def add_subject(uid, name, exam_date, est_h, color):
    conn = get_conn()
    conn.execute("INSERT INTO subjects (user_id,name,exam_date,estimated_h,color) VALUES (?,?,?,?,?)", (uid,name,exam_date,est_h,color))
    conn.commit(); conn.close()

def delete_subject(sid):
    conn = get_conn()
    conn.execute("DELETE FROM sessions WHERE subject_id=?", (sid,))
    conn.execute("DELETE FROM subjects WHERE id=?", (sid,))
    conn.commit(); conn.close()

def add_session(uid, sid, study_date, duration, confidence):
    conn = get_conn()
    conn.execute("INSERT INTO sessions (user_id,subject_id,study_date,duration,confidence) VALUES (?,?,?,?,?)", (uid,sid,study_date,duration,confidence))
    conn.commit(); conn.close()
    _update_streak(uid, study_date)

def get_sessions(uid):
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.study_date,s.duration,s.confidence,sub.name,sub.color
        FROM sessions s JOIN subjects sub ON s.subject_id=sub.id
        WHERE s.user_id=? ORDER BY s.study_date DESC""", (uid,)).fetchall()
    conn.close(); return rows

def get_subject_minutes(uid):
    conn = get_conn()
    rows = conn.execute("SELECT subject_id,SUM(duration) FROM sessions WHERE user_id=? GROUP BY subject_id", (uid,)).fetchall()
    conn.close(); return {r[0]: r[1] for r in rows}

def get_week_sessions(uid):
    ws = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.study_date,s.duration,sub.name FROM sessions s
        JOIN subjects sub ON s.subject_id=sub.id
        WHERE s.user_id=? AND s.study_date>=? ORDER BY s.study_date""", (uid, ws)).fetchall()
    conn.close(); return rows

def _update_streak(uid, study_date):
    conn = get_conn()
    row = conn.execute("SELECT last_study_date,current_streak,max_streak FROM streaks WHERE user_id=?", (uid,)).fetchone()
    d = date.fromisoformat(study_date)
    if row is None:
        conn.execute("INSERT INTO streaks VALUES (?,?,1,1)", (uid, study_date))
    else:
        last, cur, mx = row
        ld = date.fromisoformat(last) if last else None
        if ld == d:
            pass
        elif ld == d - timedelta(days=1):
            cur += 1; mx = max(mx, cur)
            conn.execute("UPDATE streaks SET last_study_date=?,current_streak=?,max_streak=? WHERE user_id=?", (study_date,cur,mx,uid))
        else:
            conn.execute("UPDATE streaks SET last_study_date=?,current_streak=1 WHERE user_id=?", (study_date,uid))
    conn.commit(); conn.close()

def get_streak(uid):
    conn = get_conn()
    row = conn.execute("SELECT current_streak,max_streak,last_study_date FROM streaks WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    return (row[0], row[1], row[2]) if row else (0, 0, None)

# ── Design tokens ─────────────────────────────────────────────────────────────

# Pastel card colours rotating through subjects (inspired by the mockup cards)
CARD_PALETTES = [
    {"bg": "#EDE9FF", "accent": "#7C6DF8"},   # lavender
    {"bg": "#D4F5E9", "accent": "#34C98C"},   # mint
    {"bg": "#FFE4F0", "accent": "#F472B6"},   # pink
    {"bg": "#FEF3C7", "accent": "#F59E0B"},   # amber
    {"bg": "#DBEAFE", "accent": "#3B82F6"},   # sky blue
    {"bg": "#FCE7F3", "accent": "#EC4899"},   # rose
]

def palette(i):
    return CARD_PALETTES[i % len(CARD_PALETTES)]

# ── CSS ───────────────────────────────────────────────────────────────────────

def inject_css(dark: bool):
    if dark:
        bg        = "#0E0D1F"
        surface   = "#1C1B2E"
        surface2  = "#252440"
        text      = "#E8E6FF"
        muted     = "#8B85B8"
        border    = "rgba(124,109,248,0.15)"
        shadow    = "0 8px 32px rgba(0,0,0,0.4)"
        hero_text = "#FFFFFF"
    else:
        bg        = "#F4F2FF"
        surface   = "#FFFFFF"
        surface2  = "#EDE9FF"
        text      = "#1A1640"
        muted     = "#6B648F"
        border    = "rgba(124,109,248,0.12)"
        shadow    = "0 8px 32px rgba(90,80,200,0.10)"
        hero_text = "#FFFFFF"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {{ font-family: 'Inter', sans-serif !important; }}

    .stApp {{
        background: {bg} !important;
        color: {text} !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {surface} !important;
        border-right: 1px solid {border} !important;
    }}
    [data-testid="stSidebar"] * {{ color: {text} !important; }}

    /* ── Hide default header decoration ── */
    [data-testid="stHeader"] {{ background: transparent !important; }}

    /* ── Hero banner ── */
    .hero {{
        background: linear-gradient(135deg, #7C6DF8 0%, #5B8DEF 50%, #34C98C 100%);
        border-radius: 28px;
        padding: 2.2rem 2.5rem;
        color: {hero_text};
        box-shadow: 0 12px 40px rgba(124,109,248,0.35);
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }}
    .hero::before {{
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }}
    .hero::after {{
        content: '';
        position: absolute;
        bottom: -60px; right: 80px;
        width: 140px; height: 140px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }}
    .hero h1 {{
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0 0 0.3rem;
        letter-spacing: -0.5px;
    }}
    .hero .subtitle {{
        font-size: 1rem;
        opacity: 0.88;
        margin: 0;
    }}
    .hero .badge {{
        display: inline-block;
        background: rgba(255,255,255,0.22);
        border-radius: 20px;
        padding: 0.25rem 0.9rem;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.7rem;
        backdrop-filter: blur(8px);
    }}

    /* ── Stat cards ── */
    .stat-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 22px;
        padding: 1.4rem 1.2rem;
        text-align: center;
        box-shadow: {shadow};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .stat-card:hover {{ transform: translateY(-4px); box-shadow: 0 16px 48px rgba(124,109,248,0.18); }}
    .stat-card .icon {{
        font-size: 1.8rem;
        display: block;
        margin-bottom: 0.4rem;
    }}
    .stat-card .value {{
        font-size: 2rem;
        font-weight: 800;
        color: #7C6DF8;
        line-height: 1;
    }}
    .stat-card .label {{
        font-size: 0.8rem;
        color: {muted};
        margin-top: 0.3rem;
        font-weight: 500;
    }}

    /* ── Subject / course cards ── */
    .course-card {{
        border-radius: 22px;
        padding: 1.4rem;
        box-shadow: {shadow};
        margin-bottom: 0.8rem;
        transition: transform 0.2s ease;
        position: relative;
        overflow: hidden;
    }}
    .course-card:hover {{ transform: translateY(-3px); }}
    .course-card .tag {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.65;
        margin-bottom: 0.4rem;
    }}
    .course-card h3 {{
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0 0 0.3rem;
        color: #1A1640;
    }}
    .course-card .meta {{
        font-size: 0.82rem;
        color: #4A4570;
        margin: 0;
    }}
    .course-card .pill {{
        display: inline-block;
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(6px);
        border-radius: 14px;
        padding: 0.25rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #1A1640;
        margin-top: 0.7rem;
    }}

    /* ── Session history item ── */
    .session-item {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 2px 12px rgba(124,109,248,0.07);
    }}

    /* ── Day cell (week recap) ── */
    .day-cell {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 1rem 0.5rem;
        text-align: center;
        box-shadow: {shadow};
    }}
    .day-cell.today {{
        background: linear-gradient(135deg, #7C6DF8, #5B8DEF);
        border: none;
    }}
    .day-cell.today * {{ color: #fff !important; }}
    .day-cell .day-name {{ font-size: 0.75rem; font-weight: 600; color: {muted}; }}
    .day-cell .day-min  {{ font-size: 1.3rem; font-weight: 800; color: #7C6DF8; margin: 0.2rem 0; }}
    .day-cell .day-lbl  {{ font-size: 0.65rem; color: {muted}; }}

    /* ── Nav buttons in sidebar ── */
    .stButton > button {{
        border-radius: 16px !important;
        border: 1px solid {border} !important;
        background: transparent !important;
        color: {text} !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
    }}
    .stButton > button:hover {{
        background: {surface2} !important;
        border-color: #7C6DF8 !important;
        color: #7C6DF8 !important;
        transform: none !important;
    }}

    /* ── Primary action button ── */
    .btn-primary > button {{
        background: linear-gradient(135deg, #7C6DF8, #5B8DEF) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
        box-shadow: 0 6px 20px rgba(124,109,248,0.35) !important;
        transition: all 0.2s ease !important;
    }}
    .btn-primary > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(124,109,248,0.45) !important;
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {{
        background: {surface} !important;
        border: 1.5px solid {border} !important;
        border-radius: 14px !important;
        color: {text} !important;
        padding: 0.6rem 1rem !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: #7C6DF8 !important;
        box-shadow: 0 0 0 3px rgba(124,109,248,0.15) !important;
    }}

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #7C6DF8, #34C98C) !important;
        border-radius: 100px !important;
    }}
    .stProgress > div > div > div {{
        background: {surface2} !important;
        border-radius: 100px !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {surface} !important;
        border-radius: 16px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid {border} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px !important;
        color: {muted} !important;
        font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #7C6DF8, #5B8DEF) !important;
        color: #fff !important;
    }}

    /* ── Expander ── */
    .streamlit-expanderHeader {{
        background: {surface} !important;
        border-radius: 14px !important;
        border: 1px solid {border} !important;
        color: {text} !important;
        font-weight: 600 !important;
    }}

    /* ── Alerts ── */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 14px !important;
    }}

    /* ── Section headers ── */
    .section-header {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {text};
        margin: 1.5rem 0 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    /* ── Divider ── */
    hr {{ border-color: {border} !important; }}

    /* ── Sidebar user chip ── */
    .user-chip {{
        background: linear-gradient(135deg, #7C6DF8, #5B8DEF);
        border-radius: 20px;
        padding: 0.8rem 1rem;
        color: #fff;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }}

    /* ── Urgency badges ── */
    .badge-red   {{ background:#FFE4E4; color:#D92D20; border-radius:8px; padding:2px 8px; font-size:.75rem; font-weight:700; }}
    .badge-amber {{ background:#FEF3C7; color:#B45309; border-radius:8px; padding:2px 8px; font-size:.75rem; font-weight:700; }}
    .badge-green {{ background:#D4F5E9; color:#065F46; border-radius:8px; padding:2px 8px; font-size:.75rem; font-weight:700; }}

    </style>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────

for k, v in [("logged_in", False), ("user_id", None), ("username", ""), ("dark_mode", False), ("page", "Dashboard")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Auth screen ───────────────────────────────────────────────────────────────

def show_auth():
    inject_css(False)
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div class="hero" style="text-align:center; margin-top:2rem">
            <div class="badge">✦ Beta</div>
            <h1>StudySync</h1>
            <p class="subtitle">Dein intelligenter Lernplaner</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["  Einloggen  ", "  Registrieren  "])

        with tab1:
            u = st.text_input("Benutzername", placeholder="dein-name", key="li_u")
            p = st.text_input("Passwort", type="password", placeholder="••••••••", key="li_p")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.button("Einloggen →", key="btn_login", use_container_width=True):
                uid = login_user(u.strip(), p)
                if uid:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = uid
                    st.session_state.username  = u.strip()
                    st.rerun()
                else:
                    st.error("Benutzername oder Passwort falsch.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            nu = st.text_input("Neuer Benutzername", placeholder="dein-name", key="reg_u")
            np = st.text_input("Neues Passwort", type="password", placeholder="••••••••", key="reg_p")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.button("Account erstellen →", key="btn_reg", use_container_width=True):
                if nu.strip() and np.strip():
                    if register_user(nu.strip(), np):
                        st.success("Account erstellt – jetzt einloggen!")
                    else:
                        st.warning("Benutzername bereits vergeben.")
                else:
                    st.warning("Bitte alle Felder ausfüllen.")
            st.markdown('</div>', unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def show_sidebar():
    with st.sidebar:
        st.markdown(f'<div class="user-chip">👤 {st.session_state.username}</div>', unsafe_allow_html=True)

        nav = [
            ("🏠", "Dashboard"),
            ("📖", "Lernziele"),
            ("📈", "Fortschritt"),
            ("⏱️", "Lernsession"),
            ("📅", "Wochenrecap"),
        ]
        for icon, label in nav:
            active = "btn-primary" if st.session_state.page == label else ""
            if active:
                st.markdown(f'<div class="{active}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()
            if active:
                st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.session_state.dark_mode = st.toggle("🌙  Dark Mode", value=st.session_state.dark_mode)
        st.divider()
        if st.button("🚪  Ausloggen", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id   = None
            st.session_state.username  = ""
            st.rerun()


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_dashboard():
    uid = st.session_state.user_id
    cur_streak, max_streak, _ = get_streak(uid)
    subjects  = get_subjects(uid)
    sessions  = get_sessions(uid)
    today_min = sum(s[1] for s in sessions if s[0] == date.today().isoformat())

    # Hero
    day_name = date.today().strftime("%A, %d. %B")
    st.markdown(f"""
    <div class="hero">
        <div class="badge">📅 {day_name}</div>
        <h1>Guten Tag! 👋</h1>
        <p class="subtitle">Bereit zum Lernen? Dein Streak: 🔥 {cur_streak} Tage</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "🔥", str(cur_streak), "Streak (Tage)"),
        (c2, "⭐", str(max_streak), "Bester Streak"),
        (c3, "📚", str(len(subjects)), "Fächer"),
        (c4, "⏱️", f"{today_min}", "Heute (min)"),
    ]
    for col, icon, val, lbl in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <span class="icon">{icon}</span>
                <div class="value">{val}</div>
                <div class="label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    # Upcoming exams
    st.markdown('<div class="section-header">📋 Bevorstehende Prüfungen</div>', unsafe_allow_html=True)
    upcoming = sorted([s for s in subjects if s[2]], key=lambda x: x[2])

    if not upcoming:
        st.info("Noch keine Prüfungsdaten. Füge unter **Lernziele** Fächer hinzu.")
    else:
        cols = st.columns(min(len(upcoming), 3))
        for i, sub in enumerate(upcoming[:3]):
            sid, name, exam_date, est_h, color = sub
            pal = palette(i)
            dl = (date.fromisoformat(exam_date) - date.today()).days
            if dl <= 7:
                badge = f'<span class="badge-red">🔴 {dl} Tage</span>'
            elif dl <= 14:
                badge = f'<span class="badge-amber">🟡 {dl} Tage</span>'
            else:
                badge = f'<span class="badge-green">🟢 {dl} Tage</span>'

            with cols[i % 3]:
                st.markdown(f"""
                <div class="course-card" style="background:{pal['bg']}">
                    <div class="tag">Prüfung</div>
                    <h3>{name}</h3>
                    <p class="meta">📅 {exam_date} · {est_h}h geschätzt</p>
                    <div style="margin-top:.6rem">{badge}</div>
                </div>""", unsafe_allow_html=True)

    # Recent sessions
    if sessions:
        st.markdown('<div class="section-header">🕐 Zuletzt gelernt</div>', unsafe_allow_html=True)
        for row in sessions[:5]:
            study_date, duration, confidence, name, color = row
            stars = "⭐" * confidence + "☆" * (5 - confidence)
            pal = palette(list({s[1] for s in subjects}).index(name) if name in [s[1] for s in subjects] else 0)
            st.markdown(f"""
            <div class="session-item">
                <div style="width:10px;height:44px;background:{pal['accent']};border-radius:6px;flex-shrink:0"></div>
                <div style="flex:1">
                    <div style="font-weight:700;font-size:.95rem">{name}</div>
                    <div style="font-size:.82rem;color:#6B648F">{study_date} · {duration} min</div>
                </div>
                <div style="font-size:.9rem">{stars}</div>
            </div>""", unsafe_allow_html=True)


def page_lernziele():
    uid = st.session_state.user_id

    st.markdown("""
    <div class="hero" style="padding:1.6rem 2rem">
        <h1 style="font-size:1.8rem">📖 Lernziele</h1>
        <p class="subtitle">Verwalte deine Fächer und Prüfungstermine</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("➕  Neues Fach hinzufügen"):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Fachname", placeholder="z.B. Mathematik")
        with c2:
            exam = st.date_input("Prüfungsdatum", min_value=date.today())
        with c3:
            est_h = st.number_input("Lernstunden (geschätzt)", min_value=1.0, max_value=500.0, value=20.0, step=1.0)

        color_options = {"Lavendel 💜": "#7C6DF8", "Mint 💚": "#34C98C", "Pink 🩷": "#F472B6",
                         "Himmelblau 💙": "#3B82F6", "Amber 🟡": "#F59E0B", "Rose 🌸": "#EC4899"}
        color_name = st.selectbox("Farbe", list(color_options.keys()))
        color = color_options[color_name]

        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Fach speichern", use_container_width=True):
            if name.strip():
                add_subject(uid, name.strip(), exam.isoformat(), est_h, color)
                st.success(f"✅ {name} gespeichert!")
                st.rerun()
            else:
                st.warning("Bitte Fachname eingeben.")
        st.markdown('</div>', unsafe_allow_html=True)

    subjects = get_subjects(uid)
    minutes  = get_subject_minutes(uid)

    if not subjects:
        st.info("Noch keine Fächer angelegt.")
        return

    st.markdown('<div class="section-header">📚 Deine Fächer</div>', unsafe_allow_html=True)

    for i, sub in enumerate(subjects):
        sid, name, exam_date, est_h, color = sub
        pal       = palette(i)
        done_min  = minutes.get(sid, 0)
        done_h    = done_min / 60
        progress  = min(done_h / est_h, 1.0) if est_h > 0 else 0.0
        days_left = (date.fromisoformat(exam_date) - date.today()).days if exam_date else None
        dl_text   = f"{days_left} Tage" if days_left is not None else "–"

        c1, c2 = st.columns([11, 1])
        with c1:
            st.markdown(f"""
            <div class="course-card" style="background:{pal['bg']}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <div class="tag">Fach</div>
                        <h3>{name}</h3>
                        <p class="meta">📅 Prüfung: {exam_date or '–'} · noch {dl_text} · {done_h:.1f} / {est_h}h gelernt</p>
                    </div>
                    <div style="font-size:2rem;opacity:0.4">📖</div>
                </div>
            </div>""", unsafe_allow_html=True)
            st.progress(progress, text=f"{progress*100:.0f}% abgeschlossen")
        with c2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{sid}"):
                delete_subject(sid)
                st.rerun()


def page_fortschritt():
    uid      = st.session_state.user_id
    subjects = get_subjects(uid)
    minutes  = get_subject_minutes(uid)

    st.markdown("""
    <div class="hero" style="padding:1.6rem 2rem">
        <h1 style="font-size:1.8rem">📈 Fortschritt</h1>
        <p class="subtitle">Dein Lernfortschritt pro Fach</p>
    </div>
    """, unsafe_allow_html=True)

    if not subjects:
        st.info("Keine Fächer vorhanden. Geh zu Lernziele.")
        return

    for i, sub in enumerate(subjects):
        sid, name, exam_date, est_h, color = sub
        pal      = palette(i)
        done_min = minutes.get(sid, 0)
        done_h   = done_min / 60
        progress = min(done_h / est_h, 1.0) if est_h > 0 else 0.0

        conn = get_conn()
        avg_conf = conn.execute("SELECT AVG(confidence) FROM sessions WHERE subject_id=? AND user_id=?", (sid, uid)).fetchone()[0]
        conn.close()

        if avg_conf is None:
            conf_label, conf_color = "Noch keine Sessions", "#94A3B8"
        elif avg_conf >= 4:
            conf_label, conf_color = "😎 Sehr sicher", "#34C98C"
        elif avg_conf >= 3:
            conf_label, conf_color = "🙂 Gut", "#3B82F6"
        elif avg_conf >= 2:
            conf_label, conf_color = "😐 Unsicher", "#F59E0B"
        else:
            conf_label, conf_color = "😰 Braucht Übung", "#F472B6"

        days_left = (date.fromisoformat(exam_date) - date.today()).days if exam_date else None

        st.markdown(f"""
        <div class="course-card" style="background:{pal['bg']}">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <div class="tag">Fach · {exam_date or '–'} · noch {days_left or '?'} Tage</div>
                    <h3>{name}</h3>
                    <p class="meta">{done_h:.1f} / {est_h}h · {done_min} Minuten gelernt</p>
                </div>
                <div style="text-align:right">
                    <span style="background:{conf_color}22;color:{conf_color};border-radius:10px;padding:4px 12px;font-size:.82rem;font-weight:700">
                        {conf_label}
                    </span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.progress(progress, text=f"{progress*100:.0f}%  ·  {done_h:.1f} / {est_h}h abgeschlossen")
        st.markdown("")


def page_lernsession():
    uid      = st.session_state.user_id
    subjects = get_subjects(uid)

    st.markdown("""
    <div class="hero" style="padding:1.6rem 2rem">
        <h1 style="font-size:1.8rem">⏱️ Lernsession</h1>
        <p class="subtitle">Session eintragen und Streak aufrechterhalten</p>
    </div>
    """, unsafe_allow_html=True)

    if not subjects:
        st.info("Bitte zuerst Fächer unter **Lernziele** anlegen.")
        return

    subject_map = {s[1]: s[0] for s in subjects}

    c1, c2 = st.columns(2)
    with c1:
        chosen     = st.selectbox("Fach", list(subject_map.keys()))
        duration   = st.number_input("Lernzeit (Minuten)", min_value=5, max_value=480, value=30, step=5)
    with c2:
        study_date = st.date_input("Datum", value=date.today())
        confidence = st.slider("Selbsteinschätzung (Spaced Repetition)", 1, 5, 3,
                               help="1 = sehr unsicher · 5 = perfekt")

    conf_map = {1: ("😰", "Sehr unsicher", "#F472B6"),
                2: ("😐", "Unsicher",      "#F59E0B"),
                3: ("🙂", "OK",            "#3B82F6"),
                4: ("😊", "Gut",           "#34C98C"),
                5: ("😎", "Perfekt",       "#7C6DF8")}
    e, lbl, clr = conf_map[confidence]
    st.markdown(f"""
    <div style="background:{clr}18;border:1.5px solid {clr}44;border-radius:14px;padding:.8rem 1.2rem;margin:.5rem 0">
        <span style="font-size:1.4rem">{e}</span>
        <span style="font-weight:700;color:{clr};margin-left:.5rem">{lbl}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    if st.button("✅  Session speichern", use_container_width=True):
        add_session(uid, subject_map[chosen], study_date.isoformat(), duration, confidence)
        st.success(f"🎉 {duration} Minuten **{chosen}** eingetragen!")
        st.balloons()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Today
    sessions = get_sessions(uid)
    today_s  = [s for s in sessions if s[0] == date.today().isoformat()]
    if today_s:
        st.markdown('<div class="section-header">📌 Heute bereits gelernt</div>', unsafe_allow_html=True)
        total = sum(s[1] for s in today_s)
        st.markdown(f"""
        <div class="stat-card" style="text-align:left;margin-bottom:.8rem">
            <span style="font-size:.85rem;font-weight:600;color:#6B648F">Gesamt heute</span>
            <div class="value" style="font-size:1.8rem">{total} min</div>
        </div>""", unsafe_allow_html=True)
        for s in today_s:
            _, dur, conf, name, c = s
            stars = "⭐" * conf + "☆" * (5 - conf)
            st.markdown(f"""
            <div class="session-item">
                <div style="width:10px;height:40px;background:{c};border-radius:6px;flex-shrink:0"></div>
                <div style="flex:1"><b>{name}</b><div style="font-size:.82rem;color:#6B648F">{dur} min</div></div>
                <div>{stars}</div>
            </div>""", unsafe_allow_html=True)


def page_wochenrecap():
    uid        = st.session_state.user_id
    rows       = get_week_sessions(uid)
    cur, mx, _ = get_streak(uid)
    today      = date.today()
    ws         = today - timedelta(days=today.weekday())

    days = {(ws + timedelta(days=i)).isoformat(): 0 for i in range(7)}
    for d, dur, _ in rows:
        if d in days:
            days[d] += dur

    total_min  = sum(days.values())
    study_days = sum(1 for v in days.values() if v > 0)

    st.markdown(f"""
    <div class="hero" style="padding:1.6rem 2rem">
        <h1 style="font-size:1.8rem">📅 Wochenrecap</h1>
        <p class="subtitle">KW {today.isocalendar()[1]} · {ws.strftime('%d.%m.')} – {(ws + timedelta(days=6)).strftime('%d.%m.%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    c1, c2, c3 = st.columns(3)
    for col, icon, val, lbl in [
        (c1, "⏱️", f"{total_min} min", "Diese Woche"),
        (c2, "📆", f"{study_days} / 7", "Lerntage"),
        (c3, "🔥", str(cur), "Aktueller Streak"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <span class="icon">{icon}</span>
                <div class="value">{val}</div>
                <div class="label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    # Day grid
    st.markdown('<div class="section-header">📊 Tagesübersicht</div>', unsafe_allow_html=True)
    day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    cols = st.columns(7)
    for i, (d_iso, mins) in enumerate(days.items()):
        d_obj    = date.fromisoformat(d_iso)
        lbl      = day_names[d_obj.weekday()]
        is_today = d_obj == today
        clr      = "#FFFFFF" if is_today else ("#7C6DF8" if mins > 0 else "#94A3B8")
        cls      = "day-cell today" if is_today else "day-cell"
        with cols[i]:
            st.markdown(f"""
            <div class="{cls}">
                <div class="day-name">{lbl}</div>
                <div class="day-min" style="color:{clr}">{mins}</div>
                <div class="day-lbl">min</div>
            </div>""", unsafe_allow_html=True)

    # Streak motivation
    st.markdown("")
    if cur == 0:
        st.warning("🌱 Starte heute deinen Streak – trag eine Session ein!")
    elif cur < 3:
        st.info(f"🔥 {cur} Tage – du bist am Starten, bleib dran!")
    elif cur < 7:
        st.success(f"💪 Starker Streak: {cur} Tage – weiter so!")
    else:
        st.success(f"🏆 Unglaublich – {cur} Tage am Stück! Du bist eine Lernmaschine!")

    # Session list
    if rows:
        st.markdown('<div class="section-header">📝 Sessions diese Woche</div>', unsafe_allow_html=True)
        for d, dur, name in rows:
            st.markdown(f"- **{d}**  ·  {name}  ·  {dur} min")
    else:
        st.info("Diese Woche noch keine Sessions eingetragen.")


# ── Main ──────────────────────────────────────────────────────────────────────

if not st.session_state.logged_in:
    show_auth()
else:
    inject_css(st.session_state.dark_mode)
    show_sidebar()

    p = st.session_state.page
    if   p == "Dashboard":   page_dashboard()
    elif p == "Lernziele":   page_lernziele()
    elif p == "Fortschritt": page_fortschritt()
    elif p == "Lernsession": page_lernsession()
    elif p == "Wochenrecap": page_wochenrecap()

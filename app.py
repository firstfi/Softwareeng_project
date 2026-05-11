from turtle import color
import time
import datetime
from datetime import datetime
import hashlib
import sqlite3
import streamlit as st

#Datenbank 


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )

    user = c.fetchone()
    conn.close()

    return user is not None


init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""



    tab1, tab2 = st.tabs(["Login", "Registrieren"])

    with tab1:
        username = st.text_input("Benutzername", key="login_username")
        password = st.text_input("Passwort", type="password", key="login_password")

        if st.button("Einloggen"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Benutzername oder Passwort falsch.")

    with tab2:
        new_username = st.text_input("Neuer Benutzername", key="register_username")
        new_password = st.text_input("Neues Passwort", type="password", key="register_password")

        if st.button("Registrieren"):
            if new_username.strip() and new_password.strip():
                success = register_user(new_username, new_password)

                if success:
                    st.success("Account erstellt. Du kannst dich jetzt einloggen.")
                else:
                    st.warning("Benutzername existiert bereits.")
            else:
                st.warning("Bitte alles ausfüllen.")





st.set_page_config(
    page_title="StudyFlow - Dein Lerntracker",
    page_icon="📚",
    layout="wide",
)


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False



def inject_css(dark: bool):
    bg = "#0F172A" if dark else "#F8FAFC"
    card = "#111827" if dark else "#FFFFFF"
    text = "#E5E7EB" if dark else "#0F172A"
    muted = "#94A3B8" if dark else "#64748B"

    border = (
        "rgba(148, 163, 184, 0.25)"
        if dark else
        "rgba(15, 23, 42, 0.08)"
    )

    shadow = (
        "0 20px 45px rgba(0,0,0,.25)"
        if dark else
        "0 20px 45px rgba(15,23,42,.08)"
    )

    input_bg = (
        "rgba(255,255,255,0.08)"
        if dark else
        "#FFFFFF"
    )

    st.markdown(
        f"""
        <style>

       
        .stApp {{
            background: {bg};
            color: {text};
        }}

   
        [data-testid="stSidebar"] {{
            background: {card};
            border-right: 1px solid {border};
            color: {text};
        }}

        
        .hero {{
            padding: 2.5rem;
            border-radius: 30px;
            background: linear-gradient(135deg, #6366F1, #10B981);
            color: white;
            box-shadow: {shadow};
            margin-bottom: 2rem;
        }}

        .hero h1 {{
            font-size: 3.2rem;
            margin-bottom: .5rem;
            font-weight: 700;
        }}

        .hero p {{
            font-size: 1.1rem;
            opacity: .92;
        }}

      
        .card {{
            background: {card};
            color: {text};
            border: 1px solid {border};
            border-radius: 24px;
            padding: 1.6rem;
            box-shadow: {shadow};
            margin-bottom: 1rem;
            transition: 0.2s ease;
        }}

        .card:hover {{
            transform: translateY(-3px);
        }}

        .card h2 {{
            margin-bottom: .5rem;
        }}

        .muted {{
            color: {muted};
        }}

       
        .stTextInput > div > div > input {{
            background: {input_bg};
            color: {text};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 0.95rem 1rem;
            font-size: 1rem;
            transition: all 0.2s ease;
        }}

        .stTextInput > div > div > input:focus {{
            border: 1px solid #6366F1;
            box-shadow: 0 0 0 4px rgba(99,102,241,.20);
        }}

        
        .stTextInput input::placeholder {{
            color: {muted};
        }}

      
        .stButton button {{
            width: 100%;
            border-radius: 18px;
            padding: 0.8rem 1rem;
            border: none;
            background: linear-gradient(135deg, #6366F1, #10B981);
            color: white;
            font-weight: 600;
            transition: 0.2s ease;
        }}

        .stButton button:hover {{
            transform: scale(1.02);
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.markdown("Tracke deinen LearnFlow")

    st.session_state.dark_mode = st.toggle(
        "Dark Mode",
        value=st.session_state.dark_mode
    )


inject_css(st.session_state.dark_mode)


st.markdown(
    """
    <div class="hero">
        <h1>Study Flow</h1>
        <p>
            Eine moderne Lern-App mit elegantem Light & Dark Mode.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card">
            <h2>Lernen</h2>
            <p class="muted">
                Tracke deine täglichen Lernfortschritte.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h2>Streak</h2>
            <p class="muted">
                Bleib jeden Tag motiviert und sammle Lernserien.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if "lernziele" not in st.session_state:
    st.session_state.lernziele = []

fach = st.text_input(
    "Lernfach",
    placeholder="z.B. Mathematik, Python, Geschichte ..."
)

zeit = st.text_input(
    "Lernzeit",
    placeholder="Wie lange möchtest du lernen? z.B. 30 Minuten"
)

st.markdown(
    f"""
    <div class="card">
        <h2>Fach: {fach}</h2>
        <p class="muted">
            Lernzeit: {zeit}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("Lernziel speichern"):
    if fach.strip() and zeit.strip():
        st.session_state.lernziele.append({
            "fach": fach,
            "zeit": zeit
        })
        st.success("Lernziel wurde gespeichert!")
    else:
        st.warning("Bitte gib ein Fach und eine Lernzeit ein.")



if st.session_state.lernziele:
    st.markdown("## Gespeicherte Lernziele")

    for ziel in st.session_state.lernziele:
        st.markdown(
            f"""
            <div class="card">
                <h2>Fach: {ziel["fach"]}</h2>
                <p class="muted">Lernzeit: {ziel["zeit"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )



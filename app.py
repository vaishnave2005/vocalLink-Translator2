import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import database as db
import os
import uuid
from streamlit_mic_recorder import speech_to_text

# ── Bootstrap ────────────────────────────────────────────────────────────────
db.create_db()

st.set_page_config(
    page_title="Sofia — English ↔ Spanish Translator",
    layout="wide",
    page_icon="🎙️",
    initial_sidebar_state="expanded"
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Background ── */
.stApp {
    background: #0d1117 !important;
    color: #f0f2f5 !important;
    min-height: 100vh;
}

/* ── Hide Streamlit default clutter ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1f2937 !important;
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] * { color: #f0f2f5 !important; }
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span { color: #d1d5db !important; }

/* ── All Headings ── */
h1 { color: #ffffff !important; font-weight: 800 !important; }
h2 { color: #f9fafb !important; font-weight: 700 !important; }
h3 { color: #f3f4f6 !important; font-weight: 600 !important; }
h4, h5, h6 { color: #e5e7eb !important; font-weight: 600 !important; }

/* ── Paragraph & regular text ── */
p, span, div { color: #e5e7eb; }

/* ── Labels (Streamlit widgets) ── */
label, .stTextInput label, .stTextArea label,
.stRadio label, .stSelectbox label,
[data-testid="stWidgetLabel"] p {
    color: #f9fafb !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.01em;
}

/* ── Text Inputs ── */
.stTextInput input {
    background: #1f2937 !important;
    color: #f9fafb !important;
    border: 1.5px solid #374151 !important;
    border-radius: 10px !important;
    font-size: 0.97rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.6rem 0.85rem !important;
    transition: border-color 0.2s;
}
.stTextInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}
.stTextInput input::placeholder { color: #6b7280 !important; }

/* ── Text Areas ── */
.stTextArea textarea {
    background: #1f2937 !important;
    color: #f9fafb !important;
    border: 1.5px solid #374151 !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    line-height: 1.6 !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.2s;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}
.stTextArea textarea::placeholder { color: #6b7280 !important; }
.stTextArea textarea:disabled {
    background: #161d29 !important;
    color: #c8d6e5 !important;
    border-color: #2d3748 !important;
    opacity: 1 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.6rem 1.6rem !important;
    letter-spacing: 0.02em;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.5) !important;
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1f2937;
    border-radius: 12px;
    padding: 5px;
    gap: 4px;
    border: 1px solid #374151;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: #9ca3af !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.18s;
}
.stTabs [data-baseweb="tab"]:hover { color: #e5e7eb !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.4);
}
/* Tab content text */
.stTabs [data-baseweb="tab-panel"] * { color: #f9fafb !important; }

/* ── Radio ── */
.stRadio > div {
    background: #1f2937;
    border-radius: 14px;
    padding: 6px 10px;
    border: 1px solid #374151;
    display: flex;
    gap: 8px;
}
.stRadio [data-testid="stMarkdownContainer"] p { color: #f9fafb !important; font-weight: 600 !important; }
.stRadio label { color: #f9fafb !important; font-weight: 500 !important; font-size: 0.93rem !important; }

/* ── Divider ── */
hr { border-color: #1f2937 !important; margin: 1.5rem 0 !important; }

/* ── Alerts / Info boxes ── */
.stAlert { border-radius: 12px !important; font-weight: 500; }
[data-testid="stInfo"] {
    background: rgba(99,102,241,0.12) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: #c7d2fe !important;
    border-radius: 12px !important;
}
[data-testid="stInfo"] p { color: #c7d2fe !important; font-weight: 500; }
[data-testid="stSuccess"] {
    background: rgba(16,185,129,0.12) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    color: #6ee7b7 !important;
    border-radius: 12px !important;
}
[data-testid="stSuccess"] p { color: #6ee7b7 !important; }
[data-testid="stError"] {
    background: rgba(239,68,68,0.12) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    color: #fca5a5 !important;
    border-radius: 12px !important;
}
[data-testid="stError"] p { color: #fca5a5 !important; }
[data-testid="stWarning"] {
    background: rgba(245,158,11,0.12) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stWarning"] p { color: #fcd34d !important; }

/* ── Audio player ── */
audio { width: 100%; border-radius: 12px; margin-top: 8px; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Custom Component Styles ── */
.sofia-header {
    text-align: center;
    padding: 32px 0 16px;
}
.sofia-logo {
    font-size: 3rem;
    line-height: 1;
}
.sofia-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 8px 0 4px;
    line-height: 1.2;
}
.sofia-subtitle {
    font-size: 1rem;
    color: #9ca3af !important;
    font-weight: 400;
    margin-top: 4px;
}

.login-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 38px 36px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5);
}

.panel-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 18px;
    padding: 24px 26px;
    height: 100%;
}
.panel-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f9fafb;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1f2937;
}

.lang-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #1e3a5f, #1e2d40);
    border: 1px solid #2563eb55;
    color: #93c5fd;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
}
.direction-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 14px 24px;
    margin: 10px 0 20px;
}
.direction-arrow {
    font-size: 1.4rem;
    color: #818cf8;
}

.label-tag {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #818cf8 !important;
    margin-bottom: 6px;
    display: block;
}

.history-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s, background 0.2s;
    cursor: default;
}
.history-card:hover {
    border-color: #374151;
    background: #161d2b;
}
.history-timestamp {
    font-size: 0.76rem;
    color: #6b7280 !important;
    font-weight: 500;
}
.history-direction {
    display: inline-block;
    font-size: 0.74rem;
    font-weight: 700;
    background: rgba(99,102,241,0.18);
    color: #a5b4fc !important;
    border-radius: 6px;
    padding: 2px 9px;
    margin: 6px 0 8px;
    letter-spacing: 0.04em;
}
.history-original {
    font-size: 0.92rem;
    color: #f3f4f6 !important;
    font-weight: 500;
    margin-bottom: 4px;
}
.history-translated {
    font-size: 0.88rem;
    color: #9ca3af !important;
    font-style: italic;
}

.sidebar-profile {
    background: linear-gradient(135deg, #1e1b4b, #1e3a5f);
    border-bottom: 1px solid #1f2937;
    padding: 28px 16px 22px;
    text-align: center;
}
.sidebar-avatar {
    font-size: 2.8rem;
    margin-bottom: 8px;
}
.sidebar-name {
    font-size: 1rem;
    font-weight: 700;
    color: #f9fafb !important;
}
.sidebar-email {
    font-size: 0.76rem;
    color: #9ca3af !important;
    font-weight: 400;
    margin-top: 3px;
    word-break: break-all;
}

.empty-history {
    text-align: center;
    padding: 40px 20px;
    color: #6b7280 !important;
    font-size: 0.9rem;
}
.empty-history .icon { font-size: 2.5rem; margin-bottom: 10px; }

.section-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 22px;
}
.section-divider-line {
    flex: 1;
    height: 1px;
    background: #1f2937;
}
.section-divider-text {
    font-size: 0.85rem;
    font-weight: 700;
    color: #4b5563 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
_defaults = {
    'logged_in': False,
    'user_email': '',
    'input_text': '',
    'translated_text': '',
    'last_saved_input': '',
    'audio_file': '',
    'mode': 'English ➔ Spanish',
    'auto_translate': False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ──────────────────────────────────────────────────────────────────
def do_translation(text, src, dest):
    translated = GoogleTranslator(source=src, target=dest).translate(text)
    audio_path = f"speech_{uuid.uuid4().hex[:8]}.mp3"
    gTTS(text=translated, lang=dest).save(audio_path)
    old = st.session_state.get('audio_file', '')
    if old and old != audio_path and os.path.exists(old):
        try: os.remove(old)
        except: pass
    return translated, audio_path


# ════════════════════════════════════════════════════════════════════════════
#   LOGIN / REGISTER
# ════════════════════════════════════════════════════════════════════════════
if not st.session_state['logged_in']:

    st.markdown("""
        <div class="sofia-header">
            <div class="sofia-logo">🎙️</div>
            <div class="sofia-title">Sofia AI Studio</div>
            <div class="sofia-subtitle">English ↔ Spanish Voice Translator</div>
        </div>
    """, unsafe_allow_html=True)

    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        tab_signin, tab_signup = st.tabs(["🔐   Sign In", "✨   Create Account"])

        with tab_signin:
            st.markdown("<br>", unsafe_allow_html=True)
            email_in = st.text_input("Email address", key="login_email",
                                     placeholder="you@example.com")
            pass_in  = st.text_input("Password", type="password", key="login_pass",
                                     placeholder="Enter your password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In →", key="btn_login", use_container_width=True):
                if not email_in or not pass_in:
                    st.warning("⚠️  Please fill in both fields.")
                elif db.verify_user(email_in, pass_in):
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email_in
                    st.rerun()
                else:
                    st.error("❌  Invalid email or password.")

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            new_email = st.text_input("Email address", key="reg_email",
                                      placeholder="you@example.com")
            new_pass  = st.text_input("Password", type="password", key="reg_pass",
                                      placeholder="At least 6 characters")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account →", key="btn_signup", use_container_width=True):
                if not new_email or not new_pass:
                    st.warning("⚠️  Please fill in both fields.")
                elif len(new_pass) < 6:
                    st.warning("⚠️  Password must be at least 6 characters.")
                elif db.add_user(new_email, new_pass):
                    st.success("✅  Account created! Now sign in.")
                else:
                    st.error("❌  An account with that email already exists.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div style='text-align:center; margin-top:40px; color:#4b5563; font-size:0.8rem;'>
            Sofia AI Studio &nbsp;·&nbsp; English ↔ Spanish &nbsp;·&nbsp; Powered by Google
        </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#   MAIN APP
# ════════════════════════════════════════════════════════════════════════════
else:
    user = st.session_state['user_email']

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-profile">
                <div class="sidebar-avatar">👤</div>
                <div class="sidebar-name">Sofia Studio</div>
                <div class="sidebar-email">{user}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪  Log Out", key="btn_logout", use_container_width=True):
            for k, v in _defaults.items():
                st.session_state[k] = v
            st.rerun()

        st.markdown("""
            <div class="section-divider">
                <div class="section-divider-line"></div>
                <div class="section-divider-text">Recent Activity</div>
                <div class="section-divider-line"></div>
            </div>
        """, unsafe_allow_html=True)

        history = db.get_history(user)
        if history:
            for orig, tran, direct, ts in history[:4]:
                st.markdown(f"""
                    <div class="history-card">
                        <div class="history-timestamp">🕐 {ts[:16]}</div>
                        <div class="history-direction">{direct}</div>
                        <div class="history-original">{orig[:45]}{"…" if len(orig)>45 else ""}</div>
                        <div class="history-translated">→ {tran[:45]}{"…" if len(tran)>45 else ""}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="empty-history">
                    <div class="icon">📭</div>
                    No translations yet.<br>Start speaking or typing!
                </div>
            """, unsafe_allow_html=True)

    # ── App Header ────────────────────────────────────────────────────────────
    st.markdown("""
        <div style='text-align:center; padding:8px 0 4px;'>
            <span style='font-size:1.8rem;'>🎙️</span>
            <h1 style='font-size:2rem; font-weight:800; margin:4px 0 2px;
                       background:linear-gradient(135deg,#818cf8,#c084fc);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;'>
                Voice-to-Voice Studio
            </h1>
            <p style='color:#9ca3af; font-size:0.95rem; margin:0;'>
                Speak or type below — Sofia will translate and speak back
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Direction Toggle ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    mode = st.radio(
        "Translation direction",
        ["🇬🇧  English  ➔  Spanish  🇪🇸", "🇪🇸  Spanish  ➔  English  🇬🇧"],
        horizontal=True,
        key="mode_radio",
        label_visibility="collapsed"
    )

    is_en_to_es = "English" in mode.split("➔")[0]
    src_l  = 'en' if is_en_to_es else 'es'
    dest_l = 'es' if is_en_to_es else 'en'
    sr_lang = 'en-US' if src_l == 'en' else 'es-ES'
    mode_label = "English ➔ Spanish" if is_en_to_es else "Spanish ➔ English"
    src_name  = "English 🇬🇧" if src_l == 'en' else "Spanish 🇪🇸"
    dest_name = "Spanish 🇪🇸" if dest_l == 'es' else "English 🇬🇧"

    # Direction visual banner
    st.markdown(f"""
        <div class="direction-banner">
            <span class="lang-badge">🗣️ {src_name}</span>
            <span class="direction-arrow">→</span>
            <span class="lang-badge">🔊 {dest_name}</span>
        </div>
    """, unsafe_allow_html=True)

    # ── Two-Column Layout ─────────────────────────────────────────────────────
    col_in, col_out = st.columns(2, gap="medium")

    # ── INPUT PANEL ───────────────────────────────────────────────────────────
    with col_in:
        st.markdown(f"""
            <div class="panel-card">
                <div class="panel-title">
                    📥 Input — <span style='color:#818cf8; font-weight:700;'>{src_name}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── Three input modes as tabs ─────────────────────────────────────
        tab_mic, tab_upload, tab_type = st.tabs([
            "🎤  Record Voice",
            "📂  Upload Audio",
            "✍️  Type Text"
        ])

        # ── TAB 1: Mic Recorder ───────────────────────────────────────────
        with tab_mic:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div style='font-size:0.85rem; color:#9ca3af; margin-bottom:12px;'>
                    Press <b style='color:#f9fafb;'>Start Recording</b>, speak clearly,
                    then press <b style='color:#f9fafb;'>Stop & Transcribe</b>.
                </div>
            """, unsafe_allow_html=True)

            heard = speech_to_text(
                start_prompt="⏺  Start Recording",
                stop_prompt="⏹  Stop & Transcribe",
                just_once=True,
                use_container_width=True,
                language=sr_lang,
                key="mic_stt"
            )

            if heard:
                st.session_state['input_text'] = heard
                st.session_state['last_saved_input'] = ''
                st.session_state['auto_translate'] = True
                st.success(f"✅  Heard: **{heard}**")
            elif heard is not None and heard == '':
                st.warning("🎙️  No speech detected — try again and speak clearly.")

        # ── TAB 2: Upload Audio / Video File ─────────────────────────────
        with tab_upload:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div style='font-size:0.85rem; color:#9ca3af; margin-bottom:12px;'>
                    Upload an <b style='color:#f9fafb;'>audio or video file</b>.
                    Sofia will extract the speech and translate it automatically.<br>
                    <span style='color:#6b7280;'>Supported: WAV · MP3 · OGG · FLAC · M4A · <b style='color:#818cf8;'>MP4</b></span>
                </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Upload audio or video file",
                type=["wav", "mp3", "ogg", "flac", "m4a", "mp4"],
                label_visibility="collapsed",
                key="audio_uploader"
            )

            if uploaded_file is not None:
                file_ext = uploaded_file.name.rsplit('.', 1)[-1].lower()
                file_size_kb = round(uploaded_file.size / 1024, 1)

                # Preview the file
                if file_ext == "mp4":
                    st.video(uploaded_file)
                else:
                    st.audio(uploaded_file, format=f"audio/{file_ext}")

                st.markdown(f"""
                    <div style='font-size:0.8rem; color:#6b7280; margin:6px 0 10px;'>
                        {'🎬' if file_ext == 'mp4' else '🎵'} {uploaded_file.name}
                        &nbsp;·&nbsp; {file_size_kb} KB
                        &nbsp;·&nbsp; <span style='color:#818cf8;'>{file_ext.upper()}</span>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("🔍  Transcribe & Translate", key="btn_transcribe_upload",
                             use_container_width=True):

                    spinner_msg = ("🎬  Extracting audio from video…"
                                   if file_ext == "mp4" else
                                   "🎵  Transcribing audio file…")

                    with st.spinner(spinner_msg):
                        try:
                            import speech_recognition as sr_lib
                            import tempfile, os as _os

                            audio_bytes_data = uploaded_file.read()
                            recognizer = sr_lib.Recognizer()
                            wav_path = None

                            # ── Save uploaded file to temp ────────────────
                            with tempfile.NamedTemporaryFile(
                                suffix=f".{file_ext}", delete=False
                            ) as tmp:
                                tmp.write(audio_bytes_data)
                                tmp_path = tmp.name

                            # ── Extract audio from MP4 using moviepy ──────
                            if file_ext == "mp4":
                                from moviepy import VideoFileClip
                                wav_path = tmp_path.replace(".mp4", "_audio.wav")
                                clip = VideoFileClip(tmp_path)
                                clip.audio.write_audiofile(
                                    wav_path, fps=16000,
                                    nbytes=2, codec='pcm_s16le',
                                    logger=None
                                )
                                clip.close()
                                transcribe_path = wav_path
                            else:
                                transcribe_path = tmp_path

                            # ── Transcribe with Google STT ────────────────
                            try:
                                with sr_lib.AudioFile(transcribe_path) as source:
                                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                                    audio_data = recognizer.record(source)
                                transcribed = recognizer.recognize_google(
                                    audio_data, language=sr_lang
                                )
                                st.session_state['input_text'] = transcribed
                                st.session_state['last_saved_input'] = ''
                                st.session_state['auto_translate'] = True
                                st.success(f"✅  Transcribed: **{transcribed}**")

                            finally:
                                _os.unlink(tmp_path)
                                if wav_path and _os.path.exists(wav_path):
                                    _os.unlink(wav_path)

                        except sr_lib.UnknownValueError:
                            st.error("❌  No clear speech found. Try a louder/clearer recording.")
                        except sr_lib.RequestError as e:
                            st.error(f"❌  Google STT error: {e}")
                        except Exception as e:
                            st.error(f"❌  Error processing file: {e}")

        # ── TAB 3: Type Text ──────────────────────────────────────────────
        with tab_type:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            typed = st.text_area(
                "Input text",
                value=st.session_state['input_text'],
                height=145,
                placeholder=f"Type in {src_name.split(' ')[0]} here…",
                label_visibility="collapsed",
                key="text_input_area"
            )

            char_count = len(typed.strip())
            st.markdown(f"""
                <div style='text-align:right; font-size:0.76rem; color:#6b7280;
                            margin-top:4px; font-weight:500;'>
                    {char_count} character{'s' if char_count != 1 else ''}
                </div>
            """, unsafe_allow_html=True)

            if typed != st.session_state['input_text']:
                st.session_state['input_text'] = typed
                st.session_state['translated_text'] = ''
                st.session_state['last_saved_input'] = ''

        st.markdown("<br>", unsafe_allow_html=True)
        translate_clicked = st.button("🌐  Translate Now", key="btn_translate",
                                      use_container_width=True)

    # ── OUTPUT PANEL ──────────────────────────────────────────────────────────
    with col_out:
        st.markdown(f"""
            <div class="panel-card">
                <div class="panel-title">
                    📤 Translation — <span style='color:#c084fc; font-weight:700;'>{dest_name}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        current_input = st.session_state['input_text'].strip()
        auto_translate = st.session_state.pop('auto_translate', False)

        # ── Auto-translate on voice OR manual button click ────────────────
        should_translate = (translate_clicked and current_input) or \
                           (auto_translate and current_input)

        if should_translate:
            label = "🎙️  Translating your voice…" if auto_translate else "Translating…"
            with st.spinner(label):
                try:
                    translated, audio_path = do_translation(current_input, src_l, dest_l)
                    st.session_state['translated_text'] = translated
                    st.session_state['audio_file'] = audio_path
                    if current_input != st.session_state['last_saved_input']:
                        db.save_history(user, current_input, translated, mode_label)
                        st.session_state['last_saved_input'] = current_input
                except Exception as ex:
                    st.error(f"❌  Translation failed: {ex}")
        elif translate_clicked and not current_input:
            st.warning("⚠️  Please enter some text or record your voice first.")

        if st.session_state['translated_text']:
            st.markdown("<span class='label-tag'>Translated text</span>",
                        unsafe_allow_html=True)
            st.text_area(
                "Translated output",
                value=st.session_state['translated_text'],
                height=160,
                disabled=True,
                label_visibility="collapsed",
                key="output_area"
            )

            audio_path = st.session_state.get('audio_file', '')
            if audio_path and os.path.exists(audio_path):
                st.markdown("<span class='label-tag' style='margin-top:12px;'>🔊 Listen to translation</span>",
                            unsafe_allow_html=True)
                with open(audio_path, 'rb') as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format='audio/mp3')
                st.download_button(
                    label="⬇️  Download Audio",
                    data=audio_bytes,
                    file_name=f"sofia_translation.mp3",
                    mime="audio/mpeg",
                    use_container_width=True,
                    key="btn_download"
                )
        else:
            # Placeholder state
            placeholder_msg = (
                "👈  Click **Translate Now** to get the result."
                if current_input else
                "Record your voice or type text on the left, then click **Translate Now**."
            )
            st.markdown(f"""
                <div style='background:#0d1117; border:1.5px dashed #1f2937; border-radius:12px;
                            padding:48px 24px; text-align:center; margin-top:34px;'>
                    <span style='font-size:2rem;'>🌐</span>
                    <p style='color:#6b7280; font-size:0.92rem; margin-top:10px; font-weight:500;'>
                        {placeholder_msg}
                    </p>
                </div>
            """, unsafe_allow_html=True)

    # ── Full History ──────────────────────────────────────────────────────────
    st.markdown("""
        <div class="section-divider" style='margin-top:36px;'>
            <div class="section-divider-line"></div>
            <div class="section-divider-text">📜 Translation History</div>
            <div class="section-divider-line"></div>
        </div>
    """, unsafe_allow_html=True)

    history_data = db.get_history(user)

    if history_data:
        for orig, tran, direct, ts in history_data:
            st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
                        <span class="history-timestamp">📅 {ts[:19]}</span>
                        <span class="history-direction">{direct}</span>
                    </div>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px;'>
                        <div>
                            <div style='font-size:0.72rem; font-weight:700; text-transform:uppercase;
                                        letter-spacing:0.07em; color:#6b7280; margin-bottom:5px;'>
                                Original
                            </div>
                            <div style='font-size:0.95rem; color:#f3f4f6; font-weight:500;
                                        line-height:1.5;'>{orig}</div>
                        </div>
                        <div>
                            <div style='font-size:0.72rem; font-weight:700; text-transform:uppercase;
                                        letter-spacing:0.07em; color:#818cf8; margin-bottom:5px;'>
                                Sofia's Translation
                            </div>
                            <div style='font-size:0.95rem; color:#c7d2fe; font-weight:500;
                                        line-height:1.5; font-style:italic;'>{tran}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="empty-history" style='border:1.5px dashed #1f2937;
                         border-radius:14px; padding:50px 20px;'>
                <div class="icon">📭</div>
                <b style='color:#e5e7eb;'>No translation history yet</b><br>
                <span style='color:#6b7280;'>Your translations will appear here.</span>
            </div>
        """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
        <div style='text-align:center; margin-top:48px; padding: 20px 0;
                    border-top:1px solid #1f2937; color:#4b5563; font-size:0.78rem;'>
            Sofia AI Studio &nbsp;·&nbsp; English ↔ Spanish &nbsp;·&nbsp;
            Powered by Google Translate & gTTS
        </div>
    """, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import random
import time

# 🔐 Password Gate
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 🔐 Password Gate using secrets
real_password = st.secrets["auth"]["password"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center;'>🔒 Naughty Truth or Dare</h2>", unsafe_allow_html=True)

    pwd = st.text_input("Enter the secret password to play:", type="password")
    submitted = st.button("🔓 Unlock")

    if submitted:
        if pwd == real_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password. Try again.")

    st.stop()


# Load CSV
df = pd.read_csv("truth_or_dare.csv")

# Init session state
for key, default in {
    'used_truths': set(),
    'used_dares': set(),
    'history': [],
    'scores': [0, 0],
    'turn': 0,
    'names': ["Player 1", "Player 2"],
    'game_started': False,
    'last': "",
    'last_type': None,
    'last_idx': None,
    'clear_prompt': False,
    'fade_out': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# 🎨 Styling with animations
st.markdown("""
<style>
.main { background-color: #111827; color: white; }

.stButton > button {
    font-size: 20px;
    padding: 16px 36px;
    margin: 0.5em 0;
    border-radius: 10px;
    width: 100%;
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}
div[data-testid="column"] button:first-child {
    background-color: #ef4444 !important;
    color: white;
}
div[data-testid="column"] button:nth-child(1) {
    background-color: #3b82f6 !important;
    color: white;
}

.prompt-box {
    border-radius: 15px;
    background-color: #1f2937;
    padding: 20px;
    font-size: 20px;
    margin-top: 20px;
    text-align: center;
    color: white;
    border: 2px solid #3b82f6;
    animation: fadeIn 0.5s ease-in-out;
}

.fade-out {
    animation: fadeOut 0.5s ease-in-out;
}

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes fadeOut {
    0% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-10px); }
}

.scoreboard {
    background-color: #1f2937;
    padding: 10px 20px;
    border-radius: 10px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🔥 Naughty Truth or Dare</h1>", unsafe_allow_html=True)

# Step 1: Clear after animation if flagged
if st.session_state.clear_prompt:
    st.session_state.last = ""
    st.session_state.last_idx = None
    st.session_state.last_type = None
    st.session_state.clear_prompt = False
    st.session_state.fade_out = False

# Player name setup
if not st.session_state.game_started:
    st.subheader("🎮 Enter Player Names")
    st.session_state.names[0] = st.text_input("Player 1", st.session_state.names[0])
    st.session_state.names[1] = st.text_input("Player 2", st.session_state.names[1])
    if st.button("▶️ Start Game"):
        st.session_state.game_started = True
else:
    st.markdown(f"### 🎯 It's {st.session_state.names[st.session_state.turn]}'s turn")
    st.markdown("### 🎲 Choose one:")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💬 Truth"):
            subset = df[df['type'] == 'truth']
            available = subset[~subset.index.isin(st.session_state.used_truths)]
            if not available.empty:
                choice = available.sample(1)
                st.session_state.last = choice.iloc[0]['text']
                st.session_state.last_idx = choice.index[0]
                st.session_state.last_type = 'truth'
                st.session_state.used_truths.add(choice.index[0])
                st.session_state.history.append((st.session_state.turn, choice.index[0], 'truth'))
                st.session_state.fade_out = False

    with col2:
        if st.button("🎲 Dare"):
            subset = df[df['type'] == 'dare']
            available = subset[~subset.index.isin(st.session_state.used_dares)]
            if not available.empty:
                choice = available.sample(1)
                st.session_state.last = choice.iloc[0]['text']
                st.session_state.last_idx = choice.index[0]
                st.session_state.last_type = 'dare'
                st.session_state.used_dares.add(choice.index[0])
                st.session_state.history.append((st.session_state.turn, choice.index[0], 'dare'))
                st.session_state.fade_out = False

    # Display the prompt
    if st.session_state.last:
        st.markdown(f"### 👤 {st.session_state.names[st.session_state.turn]}'s turn")
        css_class = "prompt-box fade-out" if st.session_state.fade_out else "prompt-box"
        st.markdown(f"<div class='{css_class}'>{st.session_state.last}</div>", unsafe_allow_html=True)

        col3, col4, col5 = st.columns(3)
        with col3:
            if st.button("✅ Completed"):
                st.session_state.scores[st.session_state.turn] += 1
                st.session_state.turn = 1 - st.session_state.turn
                st.session_state.fade_out = True
                st.session_state.clear_prompt = True
                st.rerun()


        with col4:
            if st.button("❌ Skipped"):
                st.session_state.turn = 1 - st.session_state.turn
                st.session_state.fade_out = True
                st.session_state.clear_prompt = True
                st.rerun()


        with col5:
            if st.button("🔙 Back"):
                if st.session_state.history:
                    last_turn, last_idx, last_type = st.session_state.history.pop()
                    st.session_state.turn = last_turn
                    if last_type == 'truth':
                        st.session_state.used_truths.discard(last_idx)
                    else:
                        st.session_state.used_dares.discard(last_idx)
                    st.session_state.last = ""

    st.markdown("<div class='scoreboard'>", unsafe_allow_html=True)
    st.subheader("🏆 Scoreboard")
    st.write(f"👤 {st.session_state.names[0]}: {st.session_state.scores[0]}")
    st.write(f"👤 {st.session_state.names[1]}: {st.session_state.scores[1]}")
    st.markdown("</div>", unsafe_allow_html=True)

    col6, col7 = st.columns(2)
    with col6:
        if st.button("🔄 Full Reset"):
            for key in ['used_truths', 'used_dares', 'history', 'scores', 'last', 'last_idx', 'last_type']:
                st.session_state[key] = set() if isinstance(st.session_state[key], set) else [] if isinstance(st.session_state[key], list) else 0 if isinstance(st.session_state[key], int) else ""
            st.session_state.scores = [0, 0]
            st.session_state.turn = 0
    with col7:
        if st.button("👥 Change Players"):
            st.session_state.game_started = False
            st.session_state.last = ""
            st.session_state.clear_prompt = False
            st.session_state.fade_out = False

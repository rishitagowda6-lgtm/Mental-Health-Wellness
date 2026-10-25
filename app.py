import streamlit as st
import re
import time
from streamlit_autorefresh import st_autorefresh

# --- Page Configuration ---
st.set_page_config(
    page_title="Student Wellbeing Companion",
    page_icon="🌱",
    layout="wide"
)

# --- Crisis Detection Keywords & Helplines ---
CRISIS_KEYWORDS = [
    r"\bsuicid(?:e|al)\b", r"\bself[\s-]?harm\b", r"\bkill myself\b",
    r"\bend my life\b", r"\bwant(?:ing)? to die\b", r"\bhurt myself\b",
    r"\bhopeless\b", r"\bcan['’]?t go on\b", r"\bno reason to live\b",
    r"\btake my own life\b",
]

HELPLINES = {
    "India": [
        {"name": "Tele-MANAS (24/7)", "number": "14416 / 1-800-891-4416", "url": "https://telemanas.mohfw.gov.in/"},
        {"name": "AASRA (24/7)", "number": "+91 22 2754 6669", "url": "https://www.aasra.info/helpline.html"},
    ],
    "United States": [
        {"name": "988 Suicide & Crisis Lifeline (call or text)", "number": "988", "url": "https://988lifeline.org/"},
    ],
    "International": [
        {"name": "Befrienders Worldwide", "number": "Find a local centre", "url": "https://www.befrienders.org/"},
        {"name": "Find A Helpline", "number": "Find support by country", "url": "https://findahelpline.com/"},
    ]
}

def check_crisis_triggers(text: str) -> bool:
    """Check if input text contains safety crisis keywords."""
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def render_crisis_banner():
    """Display prominent crisis intervention resources."""
    st.error("**Immediate support is available**")
    st.markdown(
        "I'm glad you told me. You deserve support from a person who can be with you right now. "
        "If you may be in immediate danger, call your local emergency number or go to the nearest emergency department. "
        "Choose a resource below; availability can depend on your location."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("India")
        for helpline in HELPLINES["India"]:
            st.markdown(f"- **[{helpline['name']}]({helpline['url']})**: `{helpline['number']}`")
            
    with col2:
        st.subheader("United States and worldwide")
        for helpline in HELPLINES["United States"] + HELPLINES["International"]:
            st.markdown(f"- **[{helpline['name']}]({helpline['url']})**: `{helpline['number']}`")

    st.caption("Emergency numbers: 112 in India, 911 in the U.S., or your local emergency service.")

# --- Empathetic AI System Prompting ---
SYSTEM_PROMPT = """
You are a warm, empathetic, and encouraging Student Wellbeing Assistant designed specifically for engineering students facing academic stress, burnout, and exam pressure.

Your Goals:
1. Provide gentle validation and empathetic active listening.
2. Guide students through effective study habits, such as Pomodoro time-blocking.
3. Help reframe negative cognitive distortions (e.g., "I'm going to fail everything", "I'm not smart enough") into balanced, constructive perspectives.
4. Encourage practical, grounding micro-breaks and relaxation techniques.

Tone Guidelines:
- Non-judgmental, calm, patient, and supportive.
- Avoid giving medical or psychiatric diagnoses.
- Keep suggestions actionable, structured, and low-pressure.
"""

def generate_empathetic_response(prompt: str) -> str:
    """
    Simulated empathetic response engine.
    (Replace this function with an API call to OpenAI, Gemini, or Anthropic using SYSTEM_PROMPT).
    """
    prompt_lower = prompt.lower()
    
    if "pomodoro" in prompt_lower or "study" in prompt_lower or "exam" in prompt_lower:
        return (
            "Engineering coursework can feel overwhelming, but breaking it down into manageable chunks helps! "
            "How about trying a quick 25-minute focused session followed by a strict 5-minute break?\n\n"
            "What is one small task on your list we can focus on for just 25 minutes?"
        )
    elif "fail" in prompt_lower or "stupid" in prompt_lower or "stress" in prompt_lower:
        return (
            "It is completely understandable to feel stressed when facing tough technical subjects. "
            "Remind yourself: feeling overwhelmed right now does not mean you are incapable.\n\n"
            "Let's reframe this together: What is one concept you *do* understand, or one small step you can take right now?"
        )
    else:
        return (
            "I hear you. Academic pressure can really weigh on you. "
            "Take a deep breath. You are doing the best you can under heavy expectations.\n\n"
            "Would you like to try a quick breathing exercise, plan out your next study session, or talk through what's on your mind?"
        )

def format_remaining(seconds: int) -> str:
    """Format non-negative seconds as a compact timer value."""
    minutes, seconds = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def render_breathing_timer() -> None:
    """Render a non-blocking 4-7-8 breathing guide."""
    running = st.session_state.get("breathing_started_at") is not None
    cycles = st.session_state.get("breathing_cycles", 3)
    total_seconds = cycles * 19

    if running:
        st_autorefresh(interval=1000, key="breathing_refresh")
        elapsed = int(time.time() - st.session_state.breathing_started_at)
        remaining = total_seconds - elapsed
        if remaining <= 0:
            st.session_state.breathing_started_at = None
            st.success("Exercise complete. Take a moment before returning to your day.")
        else:
            phase_second = elapsed % 19
            if phase_second < 4:
                phase, phase_remaining = "Inhale gently", 4 - phase_second
            elif phase_second < 11:
                phase, phase_remaining = "Hold softly", 11 - phase_second
            else:
                phase, phase_remaining = "Exhale slowly", 19 - phase_second
            st.metric(phase, f"{phase_remaining}s")
            st.progress(min(elapsed / total_seconds, 1.0), text=f"Cycle {elapsed // 19 + 1} of {cycles}")

    start_col, reset_col = st.columns(2)
    if start_col.button("Start", key="start_breathing", disabled=running, use_container_width=True):
        st.session_state.breathing_cycles = st.session_state.breathing_cycle_count
        st.session_state.breathing_started_at = time.time()
        st.rerun()
    if reset_col.button("Reset", key="reset_breathing", disabled=not running, use_container_width=True):
        st.session_state.breathing_started_at = None
        st.rerun()


def render_pomodoro_timer() -> None:
    """Render a configurable, rerun-friendly focus countdown."""
    running = st.session_state.get("pomodoro_started_at") is not None
    duration = st.session_state.get("pomodoro_duration_seconds", 25 * 60)

    if running:
        st_autorefresh(interval=1000, key="pomodoro_refresh")
        elapsed = int(time.time() - st.session_state.pomodoro_started_at)
        remaining = duration - elapsed
        if remaining <= 0:
            st.session_state.pomodoro_started_at = None
            st.session_state.pomodoro_duration_seconds = 0
            st.success("Focus session complete. A short break is yours to take.")
        else:
            st.metric("Time remaining", format_remaining(remaining))
            st.progress(min(elapsed / duration, 1.0), text="Focus session")

    start_col, reset_col = st.columns(2)
    if start_col.button("Start focus", key="start_pomodoro", disabled=running, use_container_width=True):
        st.session_state.pomodoro_duration_seconds = st.session_state.pomodoro_minutes * 60
        st.session_state.pomodoro_started_at = time.time()
        st.rerun()
    if reset_col.button("Reset", key="reset_pomodoro", disabled=not running, use_container_width=True):
        st.session_state.pomodoro_started_at = None
        st.rerun()


# --- App UI Layout ---
st.title("Student Wellbeing Companion")
st.caption("A calm, low-pressure space for engineering students navigating study stress and burnout.")

# Sidebar Tools
with st.sidebar:
    st.header("Quick tools")
    
    # Timer timestamps persist across Streamlit reruns.
    st.subheader("4-7-8 breathing")
    st.session_state.setdefault("breathing_started_at", None)
    st.session_state.setdefault("breathing_cycles", 3)
    st.session_state.breathing_cycle_count = st.selectbox("Cycles", [1, 2, 3, 4, 5], index=2)
    render_breathing_timer()

    st.markdown("---")
    
    st.subheader("Pomodoro focus")
    st.session_state.setdefault("pomodoro_started_at", None)
    st.session_state.setdefault("pomodoro_duration_seconds", 25 * 60)
    st.session_state.pomodoro_minutes = st.number_input("Focus duration (minutes)", min_value=1, max_value=60, value=25)
    render_pomodoro_timer()

    st.markdown("---")
    st.markdown("**Need immediate support?**")
    if st.button("Show crisis resources", use_container_width=True):
        st.session_state["show_crisis"] = True

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your wellbeing companion. How are you feeling about your studies today?"}
    ]
st.session_state.setdefault("crisis_flagged", False)
st.session_state.setdefault("show_crisis", False)

if st.session_state.crisis_flagged or st.session_state.show_crisis:
    render_crisis_banner()
    if not st.session_state.crisis_flagged and st.button("Close crisis resources"):
        st.session_state.show_crisis = False
        st.rerun()

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input & Safety Interception
if st.session_state.crisis_flagged:
    st.warning("Chat replies are paused for this session. Crisis resources remain available above.")
elif user_input := st.chat_input("Share what's on your mind..."):
    # Render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # Safety Check: Intercept severe distress / self-harm triggers
    if check_crisis_triggers(user_input):
        st.session_state.crisis_flagged = True
        st.session_state.show_crisis = True
        st.rerun()
    else:
        # Generate and render empathetic response
        response = generate_empathetic_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
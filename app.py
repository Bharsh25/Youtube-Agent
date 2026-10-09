import os
import re
import uuid

import streamlit as st
from dotenv import load_dotenv

from translator import SUPPORTED_LANGUAGES, translate_analysis
from youtube_analyzer import build_yt_agent

load_dotenv()

st.set_page_config(
    page_title="YouTube Video Analyzer",
    page_icon="📹",
    layout="centered",
)

# Matches watch?v=, youtu.be/, shorts/, and embed/ URLs.
VIDEO_ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})")


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets (deployment) or .env / env vars (local)."""
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")


def extract_video_id(url: str) -> str | None:
    match = VIDEO_ID_RE.search(url)
    return match.group(1) if match else None


def render_with_download(text: str, video_id: str, label: str) -> None:
    st.markdown(text)
    st.download_button(
        label=f"⬇️ Download {label} (.md)",
        data=text,
        file_name=f"analysis_{video_id}_{label.lower()}.md",
        mime="text/markdown",
        key=f"dl_{video_id}_{label}",
    )


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
st.title("📹 YouTube Video Analyzer")
st.markdown(
    "Paste a YouTube link to get a timestamped breakdown, key takeaways, "
    "and referenced resources. Translate it into Hindi or Marathi if you like."
)

api_key = get_api_key()
if not api_key:
    st.error(
        "GROQ_API_KEY not found. Add it to a `.env` file locally, "
        "or to Streamlit secrets when deployed."
    )
    st.stop()

with st.sidebar:
    st.header("Settings")
    languages = st.multiselect(
        "Translate analysis into",
        SUPPORTED_LANGUAGES,
        default=[],
    )
    st.divider()
    st.caption("Analysis uses video captions. Videos without captions can't be timestamped.")

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
video_url = st.text_input(
    "YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

if st.button("Analyze Video", type="primary"):
    video_id = extract_video_id(video_url.strip()) if video_url else None

    if not video_id:
        st.warning("Please enter a valid YouTube video URL.")
    else:
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
        # A new session per analysis, so re-running a video doesn't inherit old context.
        session_id = f"{video_id}-{uuid.uuid4().hex[:8]}"
        try:
            with st.spinner("Fetching transcript and analyzing the video..."):
                agent = build_yt_agent(api_key)
                response = agent.run(
                    f"Analyze this YouTube video: {clean_url}",
                    session_id=session_id,
                )
                english = response.content or "The agent returned an empty response."

            translations: dict[str, str] = {}
            if languages:
                with st.spinner(f"Translating into {', '.join(languages)}..."):
                    translations = translate_analysis(english, languages, api_key)

            st.session_state["result"] = {
                "video_id": video_id,
                "session_id": session_id,
                "english": english,
                "translations": translations,
                "qa": [],
            }
        except Exception as exc:
            st.session_state["result"] = None
            st.error(
                "Analysis failed. The video may have no captions, or the "
                f"transcript service may be unavailable.\n\nDetails: {exc}"
            )

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
result = st.session_state.get("result")
if result:
    video_id = result["video_id"]

    st.divider()
    st.video(f"https://www.youtube.com/watch?v={video_id}")

    tab_names = ["English", *result["translations"].keys()]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        render_with_download(result["english"], video_id, "English")
    for tab, (language, text) in zip(tabs[1:], result["translations"].items()):
        with tab:
            render_with_download(text, video_id, language)

    # Follow-ups use this analysis's session, so the agent sees its history.
    st.subheader("💬 Ask a follow-up")
    with st.form("followup_form", clear_on_submit=True):
        question = st.text_input("Question about this video")
        submitted = st.form_submit_button("Ask")
    if submitted and question.strip():
        try:
            with st.spinner("Thinking..."):
                agent = build_yt_agent(api_key)
                answer = agent.run(
                    question,
                    session_id=result["session_id"],
                )
            result["qa"].append((question, answer.content or ""))
        except Exception as exc:
            st.error(f"Could not answer that question: {exc}")

    for question, answer in result["qa"]:
        st.markdown(f"**Q:** {question}")
        st.markdown(answer)
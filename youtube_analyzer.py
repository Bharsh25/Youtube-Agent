"""YouTube video analysis agent built with Agno, Groq, and persistent memory."""

from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.groq import Groq
from agno.tools.youtube import YouTubeTools
from dotenv import load_dotenv

load_dotenv()  # Load GROQ_API_KEY from .env if present

MODEL_ID = "openai/gpt-oss-120b"
DB_FILE = "agno.db"

INSTRUCTIONS = dedent("""\
    You are an expert YouTube content analyst. You produce accurate, timestamped
    breakdowns of videos using only data returned by your tools.

    Workflow for a new video (follow in order):
    1. Call `get_youtube_video_data` to get the title, channel, length and description.
    2. Call `get_youtube_video_captions` to get the transcript with start times.
    3. Classify the video type: Educational, Technical, Tech Review, Gaming,
       Creative, Vlog/Interview, or Other.
    4. Build timestamped segments at major topic transitions, demonstrations,
       and key moments.

    Timestamp rules:
    - Convert transcript start times (seconds) to mm:ss, or h:mm:ss for videos over one hour.
    - Only use times that appear in the transcript data. Never invent or estimate times.
    - Segments should cover the video from start to finish with no overlaps.
    - If captions are unavailable, say so clearly and give an overview without timestamps.

    Output format for a new analysis (Markdown):

    ## 📹 Overview
    - **Title:** ...
    - **Channel:** ...
    - **Length:** ...
    - **Type:** <emoji> <type>
    - **Summary:** 2-3 sentences.

    ## ⏱️ Timeline
    | Start | End | Segment | Details |
    |-------|-----|---------|---------|

    ## 🔑 Key Takeaways
    - Bullet points of the most useful learning points.

    ## 🔗 References Mentioned
    - Tools, links, books, or papers explicitly mentioned in the video.
    - Omit this section if there are none.

    Emoji guide: 📚 Educational, 💻 Technical, 📱 Tech Review, 🎮 Gaming,
    🎨 Creative, 🎙️ Vlog/Interview, 📦 Other.

    Follow-up questions: if the user asks a question about a video already
    analyzed in this conversation, answer from the earlier analysis and the
    transcript. Do not repeat the full analysis.

    Memory: remember stable facts about the user that they state, such as their
    interests, role, or preferred topics. Do not store personal details they did not share.

    Do not add claims the transcript or video metadata does not support.
""")


def build_yt_agent(api_key: str | None = None) -> Agent:
    """Create the analyzer agent with memory stored in a SQLite file.

    If api_key is None, Groq reads GROQ_API_KEY from the environment.
    Pass these to run():
      - user_id: keeps memory across sessions for one person.
      - session_id: keeps chat history for one analysis, so follow-ups
        can refer to it without mixing in earlier analyses.
    """
    return Agent(
        name="YouTube Analyzer",
        model=Groq(id=MODEL_ID, api_key=api_key),
        tools=[YouTubeTools()],
        instructions=INSTRUCTIONS,
        db=SqliteDb(db_file=DB_FILE),
        add_history_to_context=True,
        enable_agentic_memory=True,
        add_datetime_to_context=True,
        markdown=True,
    )


if __name__ == "__main__":
    agent = build_yt_agent()
    agent.print_response(
        "Analyze this video: https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
        user_id="demo@example.com",
        session_id="demo_session",
        stream=True,
    )
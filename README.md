# 📹 YouTube Video Analyzer

Paste a YouTube link and get a timestamped breakdown, key takeaways, and the resources mentioned in the video. Translate the analysis into Hindi or Marathi, then ask follow-up questions about it.

Built with **Agno**, **Groq** (`openai/gpt-oss-120b`), and **Streamlit**.

<img width="1917" height="917" alt="Screenshot 2026-10-10 012345" src="https://github.com/user-attachments/assets/25cd66d1-1154-4385-b19f-cba977c98191" />

<img width="727" height="825" alt="Screenshot 2026-10-10 012401" src="https://github.com/user-attachments/assets/238b2607-c332-4972-9174-e4f7a6be317c" />



## ✨ Features

- **Timestamped timeline:** segments with start and end times, taken from the video's captions
- **Structured analysis:** overview, video type, key takeaways, and references
- **Multi-language output:** Hindi and Marathi translations in their own tabs, with the layout and timestamps preserved
- **Follow-up Q&A:** ask questions about a specific video, with the earlier analysis as context
- **Export:** download any version as a Markdown file

---

## 🧱 Tech Stack

| Layer | Tools |
|---|---|
| Agent framework | Agno |
| LLM | Groq, `openai/gpt-oss-120b` |
| Video data | YouTube captions and metadata via Agno's YouTube tools |
| UI | Streamlit |
| Storage | SQLite (chat history) |

---

## 🚀 Quick Start

```bash
git clone https://github.com/Bharsh25/Youtube-Agent.git
cd Youtube-Agent

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env               # then add your GROQ_API_KEY
streamlit run app.py
```

Open http://localhost:8501 in your browser.

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push the repository to GitHub (`.env` is git-ignored).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **Create app**.
3. Select the repo and branch, and set the main file to `app.py`.
4. Under **Advanced settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

5. Click **Deploy**.

---

## 📁 Project Structure

```
Youtube-Agent/
├── app.py                # Streamlit UI
├── youtube_analyzer.py   # Analysis agent and tools
├── translator.py         # Per-language translation agents
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## ⚠️ Limitations

- Videos without captions can't be analyzed for timestamps.
- Auto-generated captions can contain errors, which carry into the analysis.
- YouTube sometimes blocks transcript requests from cloud servers. If the app works locally but fails when deployed, this is the likely cause.

---

## 🛠️ Built With

[Agno](https://github.com/agno-agi/agno) · [Groq](https://groq.com) · [Streamlit](https://streamlit.io) · [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

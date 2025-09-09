# Smart Resume Reviewer — Hackathon Starter Kit

An LLM-powered web app that reviews resumes and gives tailored, constructive feedback for a specific job role.

## Quick Start (Streamlit)

```bash
# 1) Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure (optional but recommended)
# Copy .env.example to .env and set your API key/model
# If you skip this, the app still runs in "Rule-based (offline)" mode.
cp .env.example .env

# 4) Run
streamlit run app.py
```

## What it does

- Upload a resume (PDF or paste text) and select a target job role
- Optionally upload/paste a Job Description (JD)
- Get section-wise feedback: structure, content, tone
- See missing skills/keywords, clarity/formatting tips, and tailoring suggestions
- Optional LLM review (OpenAI) + offline rule-based fallback
- Export feedback JSON and an improved-resume draft (TXT + PDF)

## Features & Architecture

```
SmartResumeReviewer/
├─ app.py                     # Streamlit UI
├─ requirements.txt
├─ .env.example               # Config template for API keys/settings
├─ README.md
├─ sample_data/
│  ├─ sample_resume.txt
│  └─ sample_job_description.txt
└─ src/
   ├─ parser.py               # PDF/text parsing & cleanup
   ├─ reviewer.py             # LLM prompts + rule-based fallback
   ├─ scorer.py               # Keyword matching + section scoring
   ├─ llm.py                  # LLM provider abstraction (OpenAI)
   └─ utils.py                # Helpers (pdf export, hashing, etc.)
```

### Privacy & Security

- Files are processed in-memory and not uploaded anywhere except your configured LLM provider (if enabled).
- If you don't set an API key, only local/offline analysis will be performed.
- Add your own data retention policy/notice as needed for production.

## Configuration

Set environment variables in `.env`:
```
OPENAI_API_KEY=sk-...           # optional
LLM_MODEL=gpt-4o-mini           # or gpt-4.1, etc. (optional)
MAX_TOKENS=1200                 # safety cap for generation
TEMPERATURE=0.2                 # generation creativity
```

You can also run **entirely offline** using the rule-based engine. Just leave `OPENAI_API_KEY` unset.

## Bonus Ideas (Optional)

- JD ↔ Resume comparison heatmap
- Multi-language support
- Version tracking across uploads
- PDF export with highlights
- Save/load review sessions (local JSON)
- Fine-tune keyword lists by role/industry

## License

MIT — do whatever you want, at your own risk. Contributions welcome.

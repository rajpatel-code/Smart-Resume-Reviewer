import io
import os
import json
import fitz  # PyMuPDF
import streamlit as st
from dotenv import load_dotenv
from src.parser import extract_text_from_pdf, normalize_text
from src.reviewer import build_feedback, build_improved_resume
from src.scorer import score_resume_against_jd, extract_keywords_from_jd
from src.utils import export_txt, export_feedback_pdf

load_dotenv()

st.set_page_config(
    page_title="Smart Resume Reviewer",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Smart Resume Reviewer")
st.caption("LLM-powered resume feedback — with an offline fallback.")

with st.expander("🔒 Privacy & Usage", expanded=False):
    st.markdown("""
- Your resume is processed locally in this app session.
- If you configure an LLM API key, text is sent to that provider for analysis.
- No files are stored server-side beyond your session.
- This is a hackathon starter and **not** production-hardened.
""")

# Sidebar: configuration
st.sidebar.header("⚙️ Settings")
use_llm = st.sidebar.toggle("Use LLM (OpenAI)", value=bool(os.getenv("OPENAI_API_KEY")))
model = st.sidebar.text_input("Model", os.getenv("LLM_MODEL", "gpt-4o-mini"))
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, float(os.getenv("TEMPERATURE", 0.2)))
max_tokens = st.sidebar.number_input("Max Tokens", 256, 4000, int(os.getenv("MAX_TOKENS", 1200)))

st.sidebar.divider()
st.sidebar.markdown("**Tips**")
st.sidebar.markdown("- Provide a clear Job Description for better feedback")
st.sidebar.markdown("- Keep achievements measurable (numbers/impact)")
st.sidebar.markdown("- Tailor keywords to the role")

# Inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Resume")
    resume_pdf = st.file_uploader("Upload resume PDF", type=["pdf"], accept_multiple_files=False)
    resume_text_input = st.text_area("...or paste resume text", height=220, placeholder="Paste your resume text here")
    if resume_pdf is not None:
        try:
            resume_text = extract_text_from_pdf(resume_pdf)
        except Exception as e:
            st.error(f"Failed to parse PDF: {e}")
            resume_text = ""
    else:
        resume_text = resume_text_input or ""
    resume_text = normalize_text(resume_text)

with col2:
    st.subheader("🎯 Target Role & Job Description")
    target_role = st.text_input("Target Job Role", placeholder="e.g., Data Scientist, Product Manager")
    jd_pdf = st.file_uploader("Optional: Upload JD PDF", type=["pdf"], accept_multiple_files=False, key="jd_pdf")
    jd_text_input = st.text_area("...or paste Job Description", height=220, placeholder="Paste a job description here")
    if jd_pdf is not None:
        try:
            jd_text = extract_text_from_pdf(jd_pdf)
        except Exception as e:
            st.error(f"Failed to parse JD PDF: {e}")
            jd_text = ""
    else:
        jd_text = jd_text_input or ""
    jd_text = normalize_text(jd_text)

# Action
run = st.button("🚀 Review Resume", type="primary", use_container_width=True)

if run:
    if not resume_text.strip():
        st.warning("Please upload a resume PDF or paste resume text.")
        st.stop()
    if not target_role.strip():
        st.warning("Please enter a target job role.")
        st.stop()

    with st.spinner("Analyzing..."):
        # Extract JD keywords and score
        jd_keywords = extract_keywords_from_jd(jd_text, target_role)
        scores, found_keywords, missing_keywords = score_resume_against_jd(resume_text, jd_keywords)

        # Build feedback (LLM or rule-based)
        feedback = build_feedback(
            resume_text=resume_text,
            target_role=target_role,
            jd_text=jd_text,
            jd_keywords=jd_keywords,
            scores=scores,
            use_llm=use_llm,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        improved_resume = build_improved_resume(
            resume_text=resume_text,
            target_role=target_role,
            jd_text=jd_text,
            use_llm=use_llm,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    st.success("Analysis complete!")

    # Layout for results
    t1, t2 = st.tabs(["📑 Feedback", "🧩 Improved Resume Draft"])

    with t1:
        st.subheader("Section-wise Feedback")
        st.markdown(f"**Target Role:** {target_role}")
        if jd_text.strip():
            st.markdown("**JD Provided:** Yes")
        else:
            st.markdown("**JD Provided:** No")

        # Show scores
        st.markdown("### Scores")
        st.json(scores)

        # Keywords
        st.markdown("### Keyword Analysis")
        st.write("**Found:**", ", ".join(sorted(found_keywords)) or "—")
        st.write("**Missing:**", ", ".join(sorted(missing_keywords)) or "—")

        # Feedback JSON
        st.markdown("### Detailed Feedback (JSON)")
        st.json(feedback)

        # Downloads
        fb_json = json.dumps(feedback, indent=2, ensure_ascii=False)
        st.download_button("⬇️ Download Feedback (JSON)", fb_json, file_name="feedback.json", mime="application/json")

        # Export feedback PDF
        pdf_bytes = export_feedback_pdf(feedback, target_role=target_role)
        st.download_button("⬇️ Download Feedback (PDF)", data=pdf_bytes, file_name="feedback.pdf", mime="application/pdf")

    with t2:
        st.subheader("Improved Resume Draft (TXT)")
        st.text_area(label="", value=improved_resume, height=400)
        st.download_button("⬇️ Download Draft (TXT)", export_txt(improved_resume), file_name="improved_resume.txt", mime="text/plain")

st.divider()
st.caption("Built for hackathons — extend as you like!")
# file: app.py

import os
import tempfile
import streamlit as st
from Resume_AI import select_best_projects, prompt_gpt4o, generate_cover_letter_body

st.set_page_config(page_title="AI Resume & Cover Letter Generator")
st.title("🧠 AI Resume & Cover Letter Generator")

# Clear session state on refresh
if st.button("🔄 Refresh App"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Input Fields ---
with st.form("job_input_form"):
    job_title = st.text_input("Job Title")
    company_name = st.text_input("Company Name")
    company_location = st.text_input("Company Location")
    job_description = st.text_area("Job Description", height=300)
    submitted = st.form_submit_button("Submit")

# Shared temp directory
temp_dir = tempfile.mkdtemp()

if submitted:
    st.session_state["job_title"] = job_title
    st.session_state["company_name"] = company_name
    st.session_state["company_location"] = company_location
    st.session_state["job_description"] = job_description

# --- Resume Generation ---
if st.session_state.get("job_description"):
    st.subheader("Generate Documents")
    col1, col2 = st.columns(2)

    if col1.button("📄 Generate Resume"):
        resume_tex, resume_pdf_path = prompt_gpt4o(
            st.session_state["job_title"],
            st.session_state["company_name"],
            st.session_state["company_location"],
            st.session_state["job_description"],
            temp_dir
        )
        st.session_state["resume_tex"] = resume_tex
        st.session_state["resume_pdf"] = resume_pdf_path

    if col2.button("✉️ Generate Cover Letter"):
        cover_letter_tex, cover_pdf_path = generate_cover_letter_body(
            st.session_state["job_title"],
            st.session_state["company_name"],
            st.session_state["company_location"],
            st.session_state["job_description"],
            temp_dir
        )
        st.session_state["cover_letter_tex"] = cover_letter_tex
        st.session_state["cover_letter_pdf"] = cover_pdf_path

# --- Display Results ---
# --- Display Results ---
if "resume_tex" in st.session_state:
    st.subheader("📄 Resume Preview")
    st.text_area("Generated LaTeX for Resume", st.session_state["resume_tex"], height=300)

    safe_company = "".join(c for c in st.session_state["company_name"] if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    resume_file_name = f"Mohamed_Sahad_M_{safe_company}.pdf"

    with open(st.session_state["resume_pdf"], "rb") as f:
        st.download_button("⬇️ Download Resume PDF", f, file_name=resume_file_name)

if "cover_letter_tex" in st.session_state:
    st.subheader("✉️ Cover Letter Preview")
    st.text_area("Generated LaTeX for Cover Letter", st.session_state["cover_letter_tex"], height=300)

    safe_company = "".join(c for c in st.session_state["company_name"] if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    cover_letter_file_name = f"cover_letter_{safe_company}.pdf"

    with open(st.session_state["cover_letter_pdf"], "rb") as f:
        st.download_button("⬇️ Download Cover Letter PDF", f, file_name=cover_letter_file_name)


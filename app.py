import streamlit as st
import pandas as pd
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills_from_text
from analysis import analyze_skills, get_final_fit
from job_scraper import scrape_job_description
# Import both LLM functions now
from llm_analyzer import find_mandatory_skills_with_llm, find_experience_with_llm

# --- App Title and Configuration ---
st.set_page_config(layout="wide")
st.title("🧠 LLM-Powered Resume and JD Analyzer")
st.write("Automatically extracts and classifies mandatory skills and experience from a job description.")

# --- Initialize session state ---
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = "Paste a job description here..."
if 'mandatory_skills' not in st.session_state:
    st.session_state.mandatory_skills = ""
if 'llm_details' not in st.session_state:
    st.session_state.llm_details = []
# --- NEW: Add experience to session state ---
if 'experience' not in st.session_state:
    st.session_state.experience = 5 # A reasonable default


# --- UI Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Provide Job Description")
    # (The URL fetcher and manual paste sections remain the same)
    st.subheader("Fetch from URL")
    jd_url = st.text_input("Enter Job Posting URL")
    if st.button("Fetch & Parse JD"):
        if jd_url:
            with st.spinner(f"Fetching content from {jd_url}..."):
                scraped_text = scrape_job_description(jd_url)
                st.session_state.jd_text = scraped_text
                st.session_state.llm_details = []
                st.session_state.mandatory_skills = ""
                if "Error:" in scraped_text: st.error(scraped_text)
                else: st.success("Successfully fetched JD!")
                st.rerun()
        else:
            st.warning("Please enter a URL.")
    st.subheader("Paste Manually")
    st.text_area("Job Description Content", height=250, key="jd_text")

    st.header("2. Auto-Detect Skills & Experience")
    # --- FIX: Renamed button for clarity ---
    if st.button("🤖 Auto-detect Skills & Experience (with LLM)"):
        if st.session_state.jd_text and "Paste a job description" not in st.session_state.jd_text:
            with st.spinner("LLM is analyzing the JD... This will take a moment, especially on the first run."):
                # --- Part 1: Analyze Skills (as before) ---
                all_skills = extract_skills_from_text(st.session_state.jd_text)
                mandatory_skills_list, llm_details = find_mandatory_skills_with_llm(st.session_state.jd_text, all_skills)
                st.session_state.mandatory_skills = ", ".join(mandatory_skills_list)
                st.session_state.llm_details = llm_details
                
                # --- Part 2 (NEW): Analyze for Experience ---
                extracted_exp = find_experience_with_llm(st.session_state.jd_text)
                if extracted_exp is not None:
                    st.session_state.experience = extracted_exp # Update state
                    st.success("LLM analysis complete! Review the skills and experience below.")
                else:
                    st.warning("LLM found skills, but could not determine years of experience. Please enter it manually.")
                
                st.rerun()
        else:
            st.warning("Please provide a job description above before analyzing.")
    
    # (LLM Analysis Details expander remains the same)
    if st.session_state.llm_details:
        with st.expander("🔍 LLM Skill Analysis Details", expanded=False):
            st.write("See how the LLM classified each skill found in the JD:")
            df = pd.DataFrame(st.session_state.llm_details)
            st.dataframe(df, use_container_width=True)

    st.header("3. Review and Analyze")
    st.text_input("Mandatory Skills (auto-populated by LLM, editable)", key="mandatory_skills")
    
    # --- FIX: This number input is now controlled by session state ---
    st.number_input("Minimum Years of Experience Required", min_value=0, key="experience")
    
    jd_ctc_input = st.number_input("Budget / Maximum CTC", min_value=0, value=150000, step=10000)

with col2:
    st.header("4. Provide Candidate Details")
    uploaded_resume = st.file_uploader("Upload Candidate's Resume (PDF only)", type=["pdf"])
    candidate_experience_input = st.number_input("Candidate's Total Years of Experience", min_value=0, value=4)
    candidate_ctc_input = st.number_input("Candidate's Expected CTC", min_value=0, value=140000, step=10000)


# --- Analysis Trigger ---
if st.button("Analyze Final Fit", type="primary"):
    if uploaded_resume is not None and st.session_state.jd_text:
        with st.spinner('Running final analysis...'):
            # This logic remains the same and should work correctly
            resume_bytes = uploaded_resume.read()
            resume_text = extract_text_from_pdf(resume_bytes)

            if resume_text is None:
                st.error("Could not read the PDF file.")
            else:
                resume_skills = extract_skills_from_text(resume_text)
                jd_skills = extract_skills_from_text(st.session_state.jd_text)
                mandatory_skills_list = [skill.strip() for skill in st.session_state.mandatory_skills.split(',') if skill.strip()]

                skill_analysis = analyze_skills(jd_skills, resume_skills, mandatory_skills_list)
                
                jd_data = {"min_experience": st.session_state.experience, "max_ctc": jd_ctc_input}
                candidate_data = {"total_experience": candidate_experience_input, "expected_ctc": candidate_ctc_input}
                final_score, explanation, details = get_final_fit(skill_analysis, jd_data, candidate_data)

                st.subheader("Analysis Result")
                if details['fit_status'] == "Not Fit":
                    st.error(f"**Status: {details['fit_status']}**")
                    st.write(details['reason'])
                else:
                    st.success(f"**Final Fit Score: {final_score}%**")
                    st.info(explanation)
                
                st.markdown("---")
                st.subheader("Detailed Skill Match")
                with st.expander("**Mandatory Skills**", expanded=True):
                    st.markdown(f"✅ **Matched:** {', '.join(details['matched_mandatory'])}" if details['matched_mandatory'] else "None")
                    st.markdown(f"❌ **Missing:** {', '.join(details['missing_mandatory'])}" if details['missing_mandatory'] else "None")
                with st.expander("**Other Skills from JD**"):
                    st.markdown(f"✅ **Matched:** {', '.join(details['matched_non_mandatory'])}" if details['matched_non_mandatory'] else "None")
                    st.markdown(f"❌ **Missing:** {', '.join(details['missing_non_mandatory'])}" if details['missing_non_mandatory'] else "None")

                # --- NEW: Expander for Bonus Skills ---
                with st.expander("**Bonus Skills (Candidate skills not in JD)**"):
                    if details['bonus_skills']:
                        # Display as a formatted list for better readability
                        bonus_skills_str = "<ul>" + "".join([f"<li>{skill}</li>" for skill in details['bonus_skills']]) + "</ul>"
                        st.markdown(bonus_skills_str, unsafe_allow_html=True)
                    else:
                        st.markdown("None")
    else:
        st.warning("Please upload a resume and provide a job description.")         # --- Detailed Skill Match ---
              
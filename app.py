import streamlit as st
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills_from_text
from analysis import analyze_skills, get_final_fit
from job_scraper import scrape_job_description # <-- IMPORT THE NEW FUNCTION

# --- App Title and Configuration ---
st.set_page_config(layout="wide")
st.title("🤖 Automated Resume and JD Fit Analyzer")
st.write("Fetch a job description from a URL or paste it manually, then upload a resume to see the fit score.")

# --- Initialize session state for JD text ---
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = """
    Job Title: Senior Python Developer
    
    Paste a job description here, or enter a URL above and click 'Fetch'.
    
    Required Skills: Python, AWS, Django.
    """

# --- UI Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("Job Description")
    
    # --- NEW: URL Scraper Section ---
    st.subheader("Option 1: Fetch JD from URL")
    jd_url = st.text_input("Enter Job Posting URL")
    if st.button("Fetch & Parse Job Description"):
        if jd_url:
            with st.spinner(f"Fetching content from {jd_url}..."):
                scraped_text = scrape_job_description(jd_url)
                st.session_state.jd_text = scraped_text # Update session state
                if "Error:" in scraped_text:
                    st.error(scraped_text)
                else:
                    st.success("Successfully fetched and parsed the job description!")
        else:
            st.warning("Please enter a URL.")
    
    # --- JD Text Area ---
    st.subheader("Option 2: Paste JD Manually")
    # The value of this text area is now controlled by session state
    jd_text = st.text_area("Job Description Content", height=300, value=st.session_state.jd_text)
    
    st.subheader("Analysis Parameters")
    mandatory_skills_input = st.text_input("Mandatory Skills (comma-separated)", "Python, AWS, Django")
    jd_experience_input = st.number_input("Minimum Years of Experience Required", min_value=0, value=5)
    jd_ctc_input = st.number_input("Budget / Maximum CTC", min_value=0, value=150000, step=10000)

with col2:
    st.header("Candidate Profile")
    uploaded_resume = st.file_uploader("Upload Candidate's Resume (PDF only)", type=["pdf"])
    candidate_experience_input = st.number_input("Candidate's Total Years of Experience", min_value=0, value=4)
    candidate_ctc_input = st.number_input("Candidate's Expected CTC", min_value=0, value=140000, step=10000)


# --- Analysis Trigger (Main logic remains the same) ---
if st.button("Analyze Fit", type="primary"):
    # The rest of your app.py's analysis logic goes here, unchanged.
    # It will use the 'jd_text' variable which is now populated either
    # by the scraper or by the user's manual input.
    if uploaded_resume is not None and jd_text:
        with st.spinner('Analyzing... This may take a moment.'):
            # 1. Extract Text and Skills
            resume_bytes = uploaded_resume.read()
            resume_text = extract_text_from_pdf(resume_bytes)

            if resume_text is None:
                st.error("Could not read the PDF file. Please try another file.")
            else:
                resume_skills = extract_skills_from_text(resume_text)
                jd_skills = extract_skills_from_text(jd_text)
                mandatory_skills_list = [skill.strip() for skill in mandatory_skills_input.split(',')]

                # 2. Perform Skill Analysis
                skill_analysis = analyze_skills(jd_skills, resume_skills, mandatory_skills_list)
                
                # 3. Structure JD and Candidate data for final scoring
                jd_data = {
                    "min_experience": jd_experience_input,
                    "max_ctc": jd_ctc_input
                }
                candidate_data = {
                    "total_experience": candidate_experience_input,
                    "expected_ctc": candidate_ctc_input
                }

                # 4. Get Final Score and Display Results
                final_score, explanation, details = get_final_fit(skill_analysis, jd_data, candidate_data)

                st.subheader("Analysis Result")

                if details['fit_status'] == "Not Fit":
                    st.error(f"**Status: {details['fit_status']}**")
                    st.write(details['reason'])
                else:
                    st.success(f"**Final Fit Score: {final_score}%**")
                    st.info(explanation)

                # --- Detailed Skill Breakdown ---
                st.markdown("---")
                st.subheader("Detailed Skill Match")
                
                with st.expander("**Mandatory Skills**", expanded=True):
                    if details['matched_mandatory']:
                        st.markdown("✅ **Matched:** " + ", ".join(details['matched_mandatory']))
                    if details['missing_mandatory']:
                        st.markdown("❌ **Missing:** " + ", ".join(details['missing_mandatory']))

                with st.expander("**Other Skills from JD**"):
                    if details['matched_non_mandatory']:
                        st.markdown("✅ **Matched:** " + ", ".join(details['matched_non_mandatory']))
                    if details['missing_non_mandatory']:
                        st.markdown("❌ **Missing:** " + ", ".join(details['missing_non_mandatory']))
    else:
        st.warning("Please upload a resume and provide a job description.")

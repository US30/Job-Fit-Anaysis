import streamlit as st
from analysis import get_final_fit
from database import connect_to_mongo, save_analysis_data

# --- App Title ---
st.title("Job Description Skill Fit Analysis")
st.write("This tool analyzes a candidate's profile against a job description and provides a fit score.")

# --- Database Connection ---
# Attempt to connect to MongoDB when the app starts.
# The connection object is stored in Streamlit's session state to persist it.
if 'db' not in st.session_state:
    st.session_state.db = connect_to_mongo()

if st.session_state.db is None:
    st.error("Failed to connect to the database. Please check your connection string and network settings. The app will work, but data will not be saved.")

# --- Input Forms in Columns for a Better Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("Job Description")
    jd_title = st.text_input("Job Title", "Senior Python Developer")
    jd_skills_input = st.text_area("Required Skills (comma-separated)", "Python, MongoDB, API, Docker, AWS")
    jd_experience_input = st.number_input("Minimum Years of Experience", min_value=0, value=5)
    jd_ctc_input = st.number_input("Budget / Maximum CTC", min_value=0, value=150000, step=10000)

with col2:
    st.header("Candidate Profile")
    candidate_name = st.text_input("Candidate Name", "John Doe")
    candidate_skills_input = st.text_area("Candidate's Skills (comma-separated)", "Python, Flask, MongoDB, AWS")
    candidate_experience_input = st.number_input("Candidate's Total Experience", min_value=0, value=4)
    candidate_ctc_input = st.number_input("Candidate's Expected CTC", min_value=0, value=140000, step=10000)

# --- Analysis Trigger ---
if st.button("Analyze Fit", type="primary"):
    # 1. Structure the input data into dictionaries
    jd = {
        "title": jd_title,
        "required_skills": [skill.strip() for skill in jd_skills_input.split(',')],
        "min_experience": jd_experience_input,
        "max_ctc": jd_ctc_input
    }
    
    candidate = {
        "name": candidate_name,
        "skills": [skill.strip() for skill in candidate_skills_input.split(',')],
        "total_experience": candidate_experience_input,
        "expected_ctc": candidate_ctc_input
    }
    
    # 2. Call the analysis function
    final_fit_score, explanation = get_final_fit(jd, candidate)
    
    # 3. Display the output
    st.subheader("Analysis Result")
    st.markdown(f"## Candidate Fit Score: **{final_fit_score}%**")
    st.info(explanation)

    # 4. Save the data to MongoDB if the connection is available
    if st.session_state.db is not None:
        analysis_result = {
            "final_score": final_fit_score,
            "summary": explanation
        }
        
        # We can add the result to the candidate document for context
        candidate['analysis_result'] = analysis_result

        if save_analysis_data(st.session_state.db, jd, candidate, analysis_result):
            st.success("Analysis data successfully saved to MongoDB Atlas!")
        else:
            st.warning("Could not save the analysis data to the database.")

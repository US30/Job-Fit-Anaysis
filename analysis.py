def analyze_skills(jd_text_skills, resume_skills, mandatory_skills_list):
    """
    Analyzes skills based on mandatory and non-mandatory categories.
    Implements the 'Not Fit' rule for mandatory skills.
    """
    # Normalize all skill lists to sets for efficient operations
    resume_skills_set = {skill.lower() for skill in resume_skills}
    jd_skills_set = {skill.lower() for skill in jd_text_skills}
    mandatory_skills_set = {skill.lower() for skill in mandatory_skills_list}

    # 1. Check for mandatory skills
    missing_mandatory = mandatory_skills_set - resume_skills_set
    
    if missing_mandatory:
        return {
            "fit_status": "Not Fit",
            "reason": f"Missing {len(missing_mandatory)} mandatory skill(s).",
            "matched_mandatory": list(mandatory_skills_set.intersection(resume_skills_set)),
            "missing_mandatory": list(missing_mandatory),
            "matched_non_mandatory": [],
            "missing_non_mandatory": []
        }

    # 2. If all mandatory skills are present, proceed with scoring
    non_mandatory_skills_set = jd_skills_set - mandatory_skills_set
    matched_non_mandatory = non_mandatory_skills_set.intersection(resume_skills_set)
    missing_non_mandatory = non_mandatory_skills_set - resume_skills_set

    # Calculate skill fit score ONLY based on non-mandatory skills
    if not non_mandatory_skills_set:
        skill_fit_percent = 100.0 # No non-mandatory skills to match
    else:
        skill_fit_percent = (len(matched_non_mandatory) / len(non_mandatory_skills_set)) * 100

    return {
        "fit_status": "Fit",
        "skill_fit_percent": round(skill_fit_percent, 2),
        "matched_mandatory": list(mandatory_skills_set),
        "missing_mandatory": [],
        "matched_non_mandatory": list(matched_non_mandatory),
        "missing_non_mandatory": list(missing_non_mandatory)
    }

def get_final_fit(skill_analysis_result, jd, candidate):
    """
    Calculates the final weighted fit score if the candidate is a 'Fit'.
    """
    # If the mandatory skill check failed, the candidate is not a fit.
    if skill_analysis_result['fit_status'] == "Not Fit":
        return 0, skill_analysis_result['reason'], skill_analysis_result

    # Weights
    SKILL_WEIGHT = 0.50
    EXPERIENCE_WEIGHT = 0.30
    CTC_WEIGHT = 0.20
    
    # Get skill fit from the detailed analysis
    skill_fit_percent = skill_analysis_result['skill_fit_percent']

    # Calculate experience fit (reusing old functions for simplicity)
    if jd['min_experience'] == 0:
        experience_fit_percent = 100.0
    elif candidate['total_experience'] >= jd['min_experience']:
        experience_fit_percent = 100.0
    else:
        experience_fit_percent = (candidate['total_experience'] / jd['min_experience']) * 100

    # Calculate CTC fit
    if candidate['expected_ctc'] <= jd['max_ctc']:
        ctc_fit_percent = 100.0
    else:
        ctc_fit_percent = (jd['max_ctc'] / candidate['expected_ctc']) * 100

    # Calculate final weighted score
    final_score = (skill_fit_percent * SKILL_WEIGHT) + \
                  (experience_fit_percent * EXPERIENCE_WEIGHT) + \
                  (ctc_fit_percent * CTC_WEIGHT)

    explanation = (
        f"Skill Fit: {skill_fit_percent}%, "
        f"Experience Fit: {round(experience_fit_percent, 2)}%, "
        f"CTC Fit: {round(ctc_fit_percent, 2)}%"
    )
    
    return round(final_score, 2), explanation, skill_analysis_result

def analyze_skills(jd_text_skills, resume_skills, mandatory_skills_list):
    """
    Analyzes skills based on mandatory, non-mandatory, and bonus categories.
    Implements the 'Not Fit' rule for mandatory skills.
    """
    # Normalize all skill lists to sets for efficient operations
    resume_skills_set = {skill.lower() for skill in resume_skills}
    jd_skills_set = {skill.lower() for skill in jd_text_skills}
    mandatory_skills_set = {skill.lower() for skill in mandatory_skills_list}

    # --- FIX: Calculate all skill categories upfront for complete reporting ---

    # 1. Mandatory skills comparison
    matched_mandatory = mandatory_skills_set.intersection(resume_skills_set)
    missing_mandatory = mandatory_skills_set - resume_skills_set

    # 2. Non-mandatory skills comparison
    non_mandatory_skills_set = jd_skills_set - mandatory_skills_set
    matched_non_mandatory = non_mandatory_skills_set.intersection(resume_skills_set)
    missing_non_mandatory = non_mandatory_skills_set - resume_skills_set

    # --- NEW: Calculate bonus skills (skills in resume but not in JD) ---
    bonus_skills = resume_skills_set - jd_skills_set

    # 3. Determine fit status and calculate score
    if missing_mandatory:
        # If any mandatory skill is missing, the status is "Not Fit".
        fit_status = "Not Fit"
        skill_fit_percent = 0
        reason = f"Missing {len(missing_mandatory)} mandatory skill(s)."
    else:
        # If all mandatory skills are present, the status is "Fit".
        fit_status = "Fit"
        reason = "All mandatory skills are present."
        # The score is based on the match of non-mandatory skills.
        if not non_mandatory_skills_set:
            skill_fit_percent = 100.0 # Perfect score if no non-mandatory skills are required.
        else:
            skill_fit_percent = (len(matched_non_mandatory) / len(non_mandatory_skills_set)) * 100

    # 4. Return a complete dictionary with all calculated data
    return {
        "fit_status": fit_status,
        "skill_fit_percent": round(skill_fit_percent, 2),
        "reason": reason,
        "matched_mandatory": list(matched_mandatory),
        "missing_mandatory": list(missing_mandatory),
        "matched_non_mandatory": list(matched_non_mandatory),
        "missing_non_mandatory": list(missing_non_mandatory),
        "bonus_skills": list(bonus_skills) # Add the new data to the result
    }

# The get_final_fit function does not need any changes, as it just passes the dictionary through.
def get_final_fit(skill_analysis_result, jd, candidate):
    """
    Calculates the final weighted fit score if the candidate is a 'Fit'.
    """
    if skill_analysis_result['fit_status'] == "Not Fit":
        # The reason is now more specific, coming directly from the analysis
        return 0, skill_analysis_result['reason'], skill_analysis_result

    # Weights
    SKILL_WEIGHT = 0.50
    EXPERIENCE_WEIGHT = 0.30
    CTC_WEIGHT = 0.20
    
    skill_fit_percent = skill_analysis_result['skill_fit_percent']

    if jd['min_experience'] == 0:
        experience_fit_percent = 100.0
    elif candidate['total_experience'] >= jd['min_experience']:
        experience_fit_percent = 100.0
    else:
        experience_fit_percent = (candidate['total_experience'] / jd['min_experience']) * 100

    if candidate['expected_ctc'] <= jd['max_ctc']:
        ctc_fit_percent = 100.0
    else:
        ctc_fit_percent = (jd['max_ctc'] / candidate['expected_ctc']) * 100

    final_score = (skill_fit_percent * SKILL_WEIGHT) + \
                  (experience_fit_percent * EXPERIENCE_WEIGHT) + \
                  (ctc_fit_percent * CTC_WEIGHT)

    explanation = (
        f"Skill Fit (Non-Mandatory): {skill_fit_percent}%, "
        f"Experience Fit: {round(experience_fit_percent, 2)}%, "
        f"CTC Fit: {round(ctc_fit_percent, 2)}%"
    )
    
    return round(final_score, 2), explanation, skill_analysis_result
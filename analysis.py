def calculate_skill_fit(jd_skills, candidate_skills):
    """Calculates the skill fit percentage."""
    # Ensure skills are compared in a case-insensitive and whitespace-trimmed manner
    jd_skills_set = {skill.lower().strip() for skill in jd_skills}
    candidate_skills_set = {skill.lower().strip() for skill in candidate_skills}

    if not jd_skills_set:
        return 100.0  # If JD requires no skills, it's a perfect fit.

    matching_skills = jd_skills_set.intersection(candidate_skills_set)
    fit_percentage = (len(matching_skills) / len(jd_skills_set)) * 100
    
    return round(fit_percentage, 2), len(matching_skills), len(jd_skills_set)

def calculate_experience_fit(jd_experience, candidate_experience):
    """Calculates the experience fit percentage."""
    if jd_experience == 0:
        return 100.0 # If no experience is required, it's a perfect fit.
    
    if candidate_experience >= jd_experience:
        return 100.0
    
    fit_percentage = (candidate_experience / jd_experience) * 100
    return round(fit_percentage, 2)

def calculate_ctc_fit(jd_ctc, candidate_ctc):
    """Calculates the CTC fit percentage."""
    if candidate_ctc <= jd_ctc:
        return 100.0
    
    # If expected CTC is higher, scale down the fit percentage
    fit_percentage = (jd_ctc / candidate_ctc) * 100
    return round(fit_percentage, 2)

def get_final_fit(jd, candidate):
    """Calculates the final weighted fit score."""
    # Weights
    SKILL_WEIGHT = 0.50
    EXPERIENCE_WEIGHT = 0.30
    CTC_WEIGHT = 0.20

    # Calculate individual fits
    skill_fit_percent, matched_skills_count, required_skills_count = calculate_skill_fit(jd['required_skills'], candidate['skills'])
    experience_fit_percent = calculate_experience_fit(jd['min_experience'], candidate['total_experience'])
    ctc_fit_percent = calculate_ctc_fit(jd['max_ctc'], candidate['expected_ctc'])

    # Calculate final weighted score
    final_score = (skill_fit_percent * SKILL_WEIGHT) + \
                  (experience_fit_percent * EXPERIENCE_WEIGHT) + \
                  (ctc_fit_percent * CTC_WEIGHT)

    # Create a short explanation
    explanation = (
        f"Matched {matched_skills_count}/{required_skills_count} skills ({skill_fit_percent}% fit). "
        f"Experience is an {experience_fit_percent}% fit. "
        f"CTC is a {ctc_fit_percent}% fit."
    )
    
    return round(final_score, 2), explanation

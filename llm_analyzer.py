import streamlit as st
from transformers import pipeline
import re

# --- Caching the Zero-Shot Classifier for Skills ---
@st.cache_resource
def get_classifier():
    print("Loading zero-shot classification model...")
    try:
        return pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0)
    except Exception:
        print("GPU not available for classifier, falling back to CPU.")
        return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# --- NEW: Caching the Question Answering model for Experience ---
@st.cache_resource
def get_qa_pipeline():
    print("Loading Question Answering model...")
    # This model is smaller and optimized for extracting answers from text.
    try:
        return pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=0)
    except Exception:
        print("GPU not available for QA, falling back to CPU.")
        return pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

classifier = get_classifier()
qa_pipeline = get_qa_pipeline()

# (The get_context_line and find_mandatory_skills_with_llm functions remain unchanged)
def get_context_line(text, entity):
    # ... (no changes to this function)
    pattern = re.compile(r'\b' + re.escape(entity) + r'\b', re.IGNORECASE)
    match = pattern.search(text)
    if not match: return ""
    start = text.rfind('\n', 0, match.start()) + 1
    end = text.find('\n', match.end())
    if end == -1: end = len(text)
    return text[start:end].strip()

def find_mandatory_skills_with_llm(jd_text, all_skills_from_jd):
    # ... (no changes to this function)
    if not all_skills_from_jd: return [], []
    mandatory_skills = []
    analysis_details = []
    candidate_labels = ["this is a required skill", "this is an optional skill"]
    CONFIDENCE_THRESHOLD = 0.70
    sequences_to_classify = []
    skills_in_sequence = []
    for skill in all_skills_from_jd:
        context = get_context_line(jd_text, skill)
        if context:
            sequences_to_classify.append(context)
            skills_in_sequence.append(skill)
    if not sequences_to_classify: return [], []
    results = classifier(sequences_to_classify, candidate_labels, multi_label=False)
    for skill, result in zip(skills_in_sequence, results):
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        analysis_details.append({"skill": skill, "classification": top_label, "confidence": f"{top_score:.2f}", "context": result['sequence']})
        if top_label == "this is a required skill" and top_score > CONFIDENCE_THRESHOLD:
            mandatory_skills.append(skill)
    return mandatory_skills, analysis_details


# --- NEW: Function to extract experience using the QA model ---
def find_experience_with_llm(jd_text):
    """
    Uses a Question Answering LLM to find the required years of experience.
    """
    question = "How many years of experience are required?"
    
    try:
        result = qa_pipeline(question=question, context=jd_text)
        answer = result['answer']
        print(f"LLM found experience answer: '{answer}' with score {result['score']:.2f}")

        # If the model is not confident, don't return a misleading answer.
        if result['score'] < 0.3: # Confidence threshold
            return None

        # Use regex to find all numbers in the answer string.
        digits = re.findall(r'\d+', answer)
        
        # If numbers are found, return the first one as an integer.
        if digits:
            # This handles "5-7 years" by correctly grabbing the first number, "5".
            return int(digits[0])
        else:
            # The model might answer with text like "five years". We can add logic for this later.
            return None
    except Exception as e:
        print(f"Error during experience extraction: {e}")
        return None
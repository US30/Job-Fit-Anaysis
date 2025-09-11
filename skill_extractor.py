import spacy
from spacy.matcher import Matcher
import json

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def load_skills_from_db(filepath="skills_db.json"):
    """Loads skills from the JSON database."""
    with open(filepath, 'r') as f:
        skills_data = json.load(f)
    
    all_skills = []
    for category in skills_data:
        all_skills.extend(skills_data[category])
    
    return all_skills

# Load skills and initialize the Matcher
SKILLS_DB = load_skills_from_db()
matcher = Matcher(nlp.vocab)

for skill in SKILLS_DB:
    # Create a pattern for each skill. Case-insensitivity is handled by LOWER.
    pattern = [{"LOWER": word.lower()} for word in skill.split()]
    matcher.add(skill, [pattern])

def extract_skills_from_text(text):
    """
    Uses spaCy Matcher to extract skills from a given text.
    Returns a set of unique skills found.
    """
    doc = nlp(text)
    matches = matcher(doc)
    
    found_skills = set()
    for match_id, start, end in matches:
        # The 'match_id' is the skill name string itself
        skill_name = nlp.vocab.strings[match_id]
        found_skills.add(skill_name)
        
    return found_skills
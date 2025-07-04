import re

def extract_skills(text):
    skills_list = [
        'python', 'django', 'sql', 'machine learning',
        'teamwork', 'communication', 'java', 'html', 'css', 'javascript'
    ]
    text_lower = text.lower()
    found_skills = [
        skill for skill in skills_list
        if re.search(rf'\b{re.escape(skill)}\b', text_lower)
    ]
    return found_skills

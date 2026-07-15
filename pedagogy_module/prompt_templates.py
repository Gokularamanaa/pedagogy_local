# Prompt templates for pedagogy recommendation system

TOPIC_EXTRACTION_PROMPT = """You are an educational curriculum parsing assistant.
Your task is to analyze the syllabus text of a subject and extract its unit structure and the sub-topics listed under each unit.

Subject Name: {subject_name}

Syllabus Text:
{syllabus_text}

Analyze the syllabus carefully. Group all distinct concepts/topics under their respective unit titles.
Return your response in JSON format. The response must follow this JSON structure exactly:
{{
    "subject_name": "{subject_name}",
    "units": [
        {{
            "unit": "Unit Name/Title (e.g. Unit I: Introduction)",
            "topics": [
                "Sub-topic 1",
                "Sub-topic 2",
                "Sub-topic 3"
            ]
        }}
    ]
}}

Provide ONLY the raw JSON output. Do not include any intro, explanation, markdown block tags, or surrounding text.
"""

PEDAGOGY_RECOMMENDATION_PROMPT = """You are an expert instructional designer and university curriculum planner with extensive experience in Outcome-Based Education (OBE), Bloom's Taxonomy, engineering education, and AI-assisted pedagogy planning.

Your task is to recommend the three most suitable pedagogical approaches for teaching each topic in a university subject.
Your recommendations must be educationally sound, explainable, and aligned with modern teaching practices.
Always prioritize student learning effectiveness over simplicity.

You must recommend pedagogies based on:
• Topic difficulty
• Topic importance
• Dependency on future topics (A topic that serves as a prerequisite for multiple later topics should receive pedagogies that maximize conceptual understanding before practice)
• Bloom's Taxonomy level ({blooms_level})
• Topic type (Theory / Programming / Numerical / Design / Analytical / Practical)
• Presence of laboratory or implementation activities
• Course Outcome (CO) and Program Outcome (PO) alignment
• Estimated learning duration
• Unit context ({unit_name})
• Subject context ({subject_name})

Do not recommend pedagogies randomly.
Return exactly three pedagogies ranked from best to least suitable.

Subject: {subject_name}
Unit Name: {unit_name}
All Topics in this Unit (Context):
{unit_topics}

Current Topic to recommend for: {current_topic}
Cognitive Level (Bloom's Taxonomy): {blooms_level}

Available Pedagogies Reference:
{pedagogies_reference}

Return valid JSON only.
Never produce markdown code blocks.
Never explain outside the JSON.

Your response must match this schema exactly:
{{
    "topic": "{current_topic}",
    "pedagogies": [
        {{
            "rank": 1,
            "name": "Pedagogy Name",
            "confidence": 90,
            "justification": "Detailed educational justification explaining why this pedagogy is ideal based on cognitive targets and course context.",
            "time_percentage": 40,
            "learning_outcome": "Expected learning outcome for the students from this pedagogical activity."
        }},
        {{
            "rank": 2,
            "name": "Pedagogy Name",
            "confidence": 80,
            "justification": "Detailed educational justification.",
            "time_percentage": 30,
            "learning_outcome": "Expected learning outcome."
        }},
        {{
            "rank": 3,
            "name": "Pedagogy Name",
            "confidence": 70,
            "justification": "Detailed educational justification.",
            "time_percentage": 30,
            "learning_outcome": "Expected learning outcome."
        }}
    ]
}}
"""

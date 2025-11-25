# src/prompts/quiz_templates.py

mcq_prompt_template = """
You are an expert exam question setter.

Create ONE multiple-choice question (MCQ) about the topic: "{topic}".
Difficulty: {difficulty}
Subject: {subject}

Return the result in JSON with these fields:
- question: the question text
- options: a list of 4 options
- correct_answer: exactly one of the options
- explanation: short explanation of the answer
"""

fill_blank_prompt_template = """
You are an expert exam question setter.

Create ONE fill-in-the-blank question about the topic: "{topic}".
Difficulty: {difficulty}
Subject: {subject}

Use '___' in the question where the blank appears.

Return the result in JSON with these fields:
- question: the question text containing '___'
- answer: the correct word or phrase for the blank
- explanation: short explanation of the answer
"""

from langchain.prompts import PromptTemplate

career_coaching_template = PromptTemplate(
    template="""You are an expert career coach with deep knowledge of professional development, 
skill building, and career planning.

User Goals and Context:
{context}

User's Question: {query}

Provide personalized, actionable career advice that:
1. Directly addresses their specific question
2. References their goals and current progress
3. Suggests 2-3 concrete next steps
4. Is encouraging yet realistic
5. Considers current industry trends

Response:""",
    input_variables=["context", "query"]
)

goal_breakdown_template = PromptTemplate(
    template="""Break down this career goal into specific, actionable milestones:

Goal: {goal}
Deadline: {deadline}
Current Progress: {progress}%

Provide:
1. 4-5 intermediate milestones
2. Estimated time for each milestone
3. Key actions for each milestone
4. Potential obstacles and how to overcome them

Response:""",
    input_variables=["goal", "deadline", "progress"]
)

skill_gap_analysis_template = PromptTemplate(
    template="""Perform a skill gap analysis for this career transition:

Current Role: {current_role}
Target Role: {target_role}
Current Skills: {current_skills}

Provide:
1. Skills you already have that transfer well
2. Critical skills you need to develop
3. Nice-to-have skills for competitive advantage
4. Recommended learning resources for each skill gap
5. Estimated timeline to become job-ready

Response:""",
    input_variables=["current_role", "target_role", "current_skills"]
)

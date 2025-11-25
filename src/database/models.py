"""
Pydantic models for data validation
These work with both MongoDB and in-memory operations
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date

# Re-export from goal_schemas and question_schemas
from src.models.question_schemas import MCQQuestion, FillBlankQuestion, QuizResult
from src.models.goal_schemas import CareerGoal, PersonalGoal, DailyTask, ChatMessage

__all__ = [
    'MCQQuestion', 
    'FillBlankQuestion', 
    'QuizResult',
    'CareerGoal',
    'PersonalGoal',
    'DailyTask',
    'ChatMessage'
]

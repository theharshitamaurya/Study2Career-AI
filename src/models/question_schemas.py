from typing import List, Optional
from pydantic import BaseModel, Field, validator

class MCQQuestion(BaseModel):
    """Schema for Multiple Choice Questions"""
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")
    correct_answer: str = Field(description="The correct answer from options")
    difficulty: str = Field(default="medium")
    subject: Optional[str] = Field(default=None, description="Subject/topic")

    @validator('question', pre=True)
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)
    
    @validator('options')
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError("Must have exactly 4 options")
        return v

class FillBlankQuestion(BaseModel):
    """Schema for Fill-in-the-Blank Questions"""
    question: str = Field(description="Question text with '___' for blank")
    answer: str = Field(description="Correct word/phrase for the blank")
    difficulty: str = Field(default="medium")
    subject: Optional[str] = Field(default=None, description="Subject/topic")

    @validator('question', pre=True)
    def clean_question(cls, v):
        if isinstance(v, dict):
            return v.get('description', str(v))
        return str(v)
    
    @validator('question')
    def validate_blank(cls, v):
        if '___' not in v and '_____' not in v:
            raise ValueError("Question must contain '___' for the blank")
        return v

class QuizResult(BaseModel):
    """Schema for quiz result records"""
    question_number: int
    question_type: str
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    subject: str
    difficulty: str

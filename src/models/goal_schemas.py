from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

class CareerGoal(BaseModel):
    """Schema for career goals"""
    goal: str = Field(description="Career goal description")
    deadline: date = Field(description="Target completion date")
    priority: str = Field(description="Priority level: High/Medium/Low")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    notes: Optional[str] = Field(default=None)

class PersonalGoal(BaseModel):
    """Schema for personal development goals"""
    goal: str = Field(description="Personal goal description")
    category: str = Field(description="Category: Health/Skills/Relationships/Mindfulness")
    completed: bool = Field(default=False)
    notes: Optional[str] = Field(default=None)

class DailyTask(BaseModel):
    """Schema for daily tasks"""
    task: str = Field(description="Task description")
    category: str = Field(description="Category: Work/Learning/Health/Personal")
    completed: bool = Field(default=False)
    priority: Optional[str] = Field(default="Medium")

class ChatMessage(BaseModel):
    """Schema for chat messages"""
    role: str = Field(description="Role: user or assistant")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)

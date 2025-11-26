from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pandas as pd
from datetime import datetime
import os
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from src.config.settings import settings

logger = get_logger(__name__)

class DatabaseManager:
    # Class-level connection pool (shared across all instances)
    _client = None
    _db = None
    
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="growth_companion"):
        """Initialize MongoDB connection with connection pooling"""
        try:
            # Use existing connection if available
            if DatabaseManager._client is None:
                DatabaseManager._client = MongoClient(
                    mongo_uri,
                    maxPoolSize=50,  # Connection pooling
                    minPoolSize=10,
                    maxIdleTimeMS=45000,
                    serverSelectionTimeoutMS=5000
                )
                DatabaseManager._db = DatabaseManager._client[db_name]
                self._create_indexes()
                logger.info(f"Connected to MongoDB with connection pooling: {db_name}")
            else:
                logger.info("Reusing existing MongoDB connection pool")
            
            self.client = DatabaseManager._client
            self.db = DatabaseManager._db
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise CustomException("MongoDB connection failed", e)
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Compound indexes for better performance
            self.db.career_goals.create_index([("user_id", 1), ("created", -1)])
            self.db.personal_goals.create_index([("user_id", 1), ("created", -1)])
            self.db.daily_tasks.create_index([("user_id", 1), ("added", -1)])
            self.db.chat_history.create_index([("user_id", 1), ("timestamp", -1)])
            self.db.quiz_results.create_index([("user_id", 1), ("subject", 1), ("taken_at", -1)])
            self.db.quiz_sessions.create_index([("user_id", 1), ("created_at", -1)])
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    # ==================== CAREER GOALS ====================
    
    def add_career_goal(self, user_id, goal, deadline, priority, notes=None):
        """Add a new career goal"""
        try:
            goal_doc = {
                "user_id": user_id,
                "goal": goal,
                "deadline": deadline if isinstance(deadline, str) else deadline.isoformat(),
                "priority": priority,
                "progress": 0,
                "created": datetime.now(),
                "notes": notes
            }
            result = self.db.career_goals.insert_one(goal_doc)
            logger.info(f"Career goal added: {goal}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add career goal: {e}")
            raise CustomException("Failed to add career goal", e)

    def get_career_goals(self, user_id):
        """Get all career goals for a user - optimized with projection"""
        try:
            # Only fetch required fields
            goals = list(self.db.career_goals.find(
                {"user_id": user_id},
                {"_id": 1, "user_id": 1, "goal": 1, "deadline": 1, "priority": 1, "progress": 1, "created": 1, "notes": 1}
            ).sort("created", -1))
            
            # Convert ObjectId to string for DataFrame compatibility
            for goal in goals:
                goal['_id'] = str(goal['_id'])
                goal['id'] = goal['_id']  # Add id field for compatibility
            
            return pd.DataFrame(goals) if goals else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get career goals: {e}")
            return pd.DataFrame()
    
    def update_career_goal(self, goal_id, progress):
        """Update career goal progress"""
        try:
            from bson.objectid import ObjectId
            self.db.career_goals.update_one(
                {"_id": ObjectId(goal_id)},
                {"$set": {"progress": progress}}
            )
            logger.info(f"Career goal {goal_id} updated to {progress}%")
        except Exception as e:
            logger.error(f"Failed to update career goal: {e}")
            raise CustomException("Failed to update career goal", e)
    
    def delete_career_goal(self, goal_id):
        """Delete a career goal"""
        try:
            from bson.objectid import ObjectId
            self.db.career_goals.delete_one({"_id": ObjectId(goal_id)})
            logger.info(f"Career goal {goal_id} deleted")
        except Exception as e:
            logger.error(f"Failed to delete career goal: {e}")

    # ==================== PERSONAL GOALS ====================
    
    def add_personal_goal(self, user_id, goal, category, notes=None):
        """Add a personal development goal"""
        try:
            goal_doc = {
                "user_id": user_id,
                "goal": goal,
                "category": category,
                "completed": False,
                "created": datetime.now(),
                "notes": notes
            }
            result = self.db.personal_goals.insert_one(goal_doc)
            logger.info(f"Personal goal added: {goal}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add personal goal: {e}")
            raise CustomException("Failed to add personal goal", e)
    
    def get_personal_goals(self, user_id):
        """Get all personal goals for a user - optimized with projection"""
        try:
            goals = list(self.db.personal_goals.find(
                {"user_id": user_id},
                {"_id": 1, "user_id": 1, "goal": 1, "category": 1, "completed": 1, "created": 1, "notes": 1}
            ).sort("created", -1))
            
            for goal in goals:
                goal['_id'] = str(goal['_id'])
                goal['id'] = goal['_id']
            
            return pd.DataFrame(goals) if goals else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get personal goals: {e}")
            return pd.DataFrame()
    
    def update_personal_goal(self, goal_id, completed):
        """Update personal goal completion status"""
        try:
            from bson.objectid import ObjectId
            self.db.personal_goals.update_one(
                {"_id": ObjectId(goal_id)},
                {"$set": {"completed": completed}}
            )
        except Exception as e:
            logger.error(f"Failed to update personal goal: {e}")
    
    def delete_personal_goal(self, goal_id):
        """Delete a personal goal"""
        try:
            from bson.objectid import ObjectId
            self.db.personal_goals.delete_one({"_id": ObjectId(goal_id)})
        except Exception as e:
            logger.error(f"Failed to delete personal goal: {e}")

    # ==================== DAILY TASKS ====================
    
    def add_daily_task(self, user_id, task, category, priority="Medium"):
        """Add a daily task"""
        try:
            task_doc = {
                "user_id": user_id,
                "task": task,
                "category": category,
                "priority": priority,
                "completed": False,
                "added": datetime.now(),
                "completed_at": None
            }
            result = self.db.daily_tasks.insert_one(task_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            raise CustomException("Failed to add task", e)
    
    def get_daily_tasks(self, user_id):
        """Get all daily tasks for a user - optimized with projection"""
        try:
            tasks = list(self.db.daily_tasks.find(
                {"user_id": user_id},
                {"_id": 1, "user_id": 1, "task": 1, "category": 1, "priority": 1, "completed": 1, "added": 1, "completed_at": 1}
            ).sort("added", -1))
            
            for task in tasks:
                task['_id'] = str(task['_id'])
                task['id'] = task['_id']
            
            return pd.DataFrame(tasks) if tasks else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return pd.DataFrame()
    
    def update_daily_task(self, task_id, completed):
        """Update task completion status"""
        try:
            from bson.objectid import ObjectId
            completed_at = datetime.now() if completed else None
            self.db.daily_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"completed": completed, "completed_at": completed_at}}
            )
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
    
    def delete_daily_task(self, task_id):
        """Delete a task"""
        try:
            from bson.objectid import ObjectId
            self.db.daily_tasks.delete_one({"_id": ObjectId(task_id)})
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")

    # ==================== CHAT HISTORY ====================
    
    def add_chat_message(self, user_id, role, content):
        """Add a chat message"""
        try:
            message_doc = {
                "user_id": user_id,
                "role": role,
                "content": content,
                "timestamp": datetime.now()
            }
            self.db.chat_history.insert_one(message_doc)
        except Exception as e:
            logger.error(f"Failed to add chat message: {e}")
    
    def get_chat_history(self, user_id, limit=20):
        """Get chat history for a user - optimized with limit and projection"""
        try:
            messages = list(self.db.chat_history.find(
                {"user_id": user_id},
                {"_id": 1, "user_id": 1, "role": 1, "content": 1, "timestamp": 1}
            ).sort("timestamp", 1).limit(limit))
            
            for msg in messages:
                msg['_id'] = str(msg['_id'])
            
            return pd.DataFrame(messages) if messages else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            return pd.DataFrame()
    
    def clear_chat_history(self, user_id):
        """Clear all chat history for a user"""
        try:
            self.db.chat_history.delete_many({"user_id": user_id})
            logger.info(f"Chat history cleared for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")

    # ==================== QUIZ RESULTS ====================
    
    def save_quiz_result(self, user_id, subject, question_type, question, user_answer, correct_answer, is_correct, difficulty):
        """Save a single quiz question result"""
        try:
            result_doc = {
                "user_id": user_id,
                "subject": subject,
                "question_type": question_type,
                "question": question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "difficulty": difficulty,
                "taken_at": datetime.now()
            }
            self.db.quiz_results.insert_one(result_doc)
        except Exception as e:
            logger.error(f"Failed to save quiz result: {e}")
    
    def save_quiz_session(self, user_id, subject, total_questions, correct_answers, score_percentage, difficulty):
        """Save overall quiz session summary"""
        try:
            session_doc = {
                "user_id": user_id,
                "subject": subject,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score_percentage": score_percentage,
                "difficulty": difficulty,
                "created_at": datetime.now()
            }
            result = self.db.quiz_sessions.insert_one(session_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save quiz session: {e}")
            return None
    
    def get_quiz_history(self, user_id, subject=None):
        """Get quiz history for analytics - optimized with projection"""
        try:
            query = {"user_id": user_id}
            if subject:
                query["subject"] = subject
            
            results = list(self.db.quiz_results.find(
                query,
                {"_id": 1, "user_id": 1, "subject": 1, "question_type": 1, "question": 1, 
                 "user_answer": 1, "correct_answer": 1, "is_correct": 1, "difficulty": 1, "taken_at": 1}
            ).sort("taken_at", -1))
            
            for result in results:
                result['_id'] = str(result['_id'])
            
            return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get quiz history: {e}")
            return pd.DataFrame()
    
    def get_quiz_sessions(self, user_id):
        """Get all quiz session summaries - optimized with projection"""
        try:
            sessions = list(self.db.quiz_sessions.find(
                {"user_id": user_id},
                {"_id": 1, "user_id": 1, "subject": 1, "total_questions": 1, 
                 "correct_answers": 1, "score_percentage": 1, "difficulty": 1, "created_at": 1}
            ).sort("created_at", -1))
            
            for session in sessions:
                session['_id'] = str(session['_id'])
                session['id'] = session['_id']
            
            return pd.DataFrame(sessions) if sessions else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get quiz sessions: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close MongoDB connection"""
        try:
            if DatabaseManager._client:
                DatabaseManager._client.close()
                DatabaseManager._client = None
                DatabaseManager._db = None
                logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")

# import sqlite3
# import pandas as pd
# from datetime import datetime
# import os
# from src.common.logger import get_logger
# from src.common.custom_exception import CustomException

# logger = get_logger(__name__)

# class DatabaseManager:
#     def __init__(self, db_path="data/growth_companion.db"):
#         self.db_path = db_path
#         os.makedirs(os.path.dirname(db_path), exist_ok=True)
#         self.init_database()
#         logger.info(f"Database initialized at {db_path}")
        
#     def _get_connection(self):
#         """Get a new database connection"""
#         return sqlite3.connect(self.db_path)
            
#     def init_database(self):
#         """Initialize all database tables"""
#         conn = self._get_connection()
#         try:
#             self._create_tables(conn)
#         finally:
#             conn.close()
            
#     def _create_tables(self, conn):
#         """Create all necessary tables"""
#         cursor = conn.cursor()
        
#         # Career goals table
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS career_goals (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT DEFAULT 'default_user',
#             goal TEXT NOT NULL,
#             deadline DATE,
#             priority TEXT,
#             progress INTEGER DEFAULT 0,
#             created TIMESTAMP,
#             notes TEXT
#         )
#         ''')
        
#         # Personal goals table
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS personal_goals (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT DEFAULT 'default_user',
#             goal TEXT NOT NULL,
#             category TEXT,
#             completed BOOLEAN DEFAULT FALSE,
#             created TIMESTAMP,
#             notes TEXT
#         )
#         ''')
        
#         # Daily tasks table
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS daily_tasks (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT DEFAULT 'default_user',
#             task TEXT NOT NULL,
#             category TEXT,
#             priority TEXT DEFAULT 'Medium',
#             completed BOOLEAN DEFAULT FALSE,
#             added TIMESTAMP,
#             completed_at TIMESTAMP
#         )
#         ''')
        
#         # Chat history table
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS chat_history (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT DEFAULT 'default_user',
#             role TEXT,
#             content TEXT,
#             timestamp TIMESTAMP
#         )
#         ''')
        
#         # Quiz results table (NEW - combines both projects)
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS quiz_results (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT DEFAULT 'default_user',
#             subject TEXT,
#             question_type TEXT,
#             question TEXT,
#             user_answer TEXT,
#             correct_answer TEXT,
#             is_correct BOOLEAN,
#             difficulty TEXT,
#             taken_at TIMESTAMP
#         )
#         ''')
        
#         # Quiz sessions table (NEW - track overall quiz attempts)
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS quiz_sessions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT DEFAULT 'default_user',
#             subject TEXT,
#             total_questions INTEGER,
#             correct_answers INTEGER,
#             score_percentage REAL,
#             difficulty TEXT,
#             created_at TIMESTAMP
#         )
#         ''')
        
#         # Goal-Task linkage table (NEW - link tasks to goals)
#         cursor.execute('''
#         CREATE TABLE IF NOT EXISTS goal_task_links (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             goal_id INTEGER,
#             task_id INTEGER,
#             goal_type TEXT,
#             FOREIGN KEY (goal_id) REFERENCES career_goals(id),
#             FOREIGN KEY (task_id) REFERENCES daily_tasks(id)
#         )
#         ''')
        
#         conn.commit()
#         logger.info("All database tables created successfully")

#     # ==================== CAREER GOALS ====================
    
#     def add_career_goal(self, user_id, goal, deadline, priority, notes=None):
#         """Add a new career goal"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO career_goals (user_id, goal, deadline, priority, progress, created, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                 (user_id, goal, deadline, priority, 0, datetime.now(), notes)
#             )
#             conn.commit()
#             logger.info(f"Career goal added: {goal}")
#             return cursor.lastrowid
#         except Exception as e:
#             logger.error(f"Failed to add career goal: {e}")
#             raise CustomException("Failed to add career goal", e)
#         finally:
#             conn.close()

#     def get_career_goals(self, user_id):
#         """Get all career goals for a user"""
#         conn = self._get_connection()
#         try:
#             query = "SELECT * FROM career_goals WHERE user_id = ? ORDER BY created DESC"
#             return pd.read_sql(query, conn, params=(user_id,))
#         finally:
#             conn.close()
    
#     def update_career_goal(self, goal_id, progress):
#         """Update career goal progress"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute("UPDATE career_goals SET progress = ? WHERE id = ?", (progress, goal_id))
#             conn.commit()
#             logger.info(f"Career goal {goal_id} updated to {progress}%")
#         finally:
#             conn.close()
    
#     def delete_career_goal(self, goal_id):
#         """Delete a career goal"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute("DELETE FROM career_goals WHERE id = ?", (goal_id,))
#             conn.commit()
#             logger.info(f"Career goal {goal_id} deleted")
#         finally:
#             conn.close()

#     # ==================== PERSONAL GOALS ====================
    
#     def add_personal_goal(self, user_id, goal, category, notes=None):
#         """Add a personal development goal"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO personal_goals (user_id, goal, category, completed, created, notes) VALUES (?, ?, ?, ?, ?, ?)",
#                 (user_id, goal, category, False, datetime.now(), notes)
#             )
#             conn.commit()
#             logger.info(f"Personal goal added: {goal}")
#             return cursor.lastrowid
#         finally:
#             conn.close()
    
#     def get_personal_goals(self, user_id):
#         """Get all personal goals for a user"""
#         conn = self._get_connection()
#         try:
#             query = "SELECT * FROM personal_goals WHERE user_id = ? ORDER BY created DESC"
#             return pd.read_sql(query, conn, params=(user_id,))
#         finally:
#             conn.close()
    
#     def update_personal_goal(self, goal_id, completed):
#         """Update personal goal completion status"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute("UPDATE personal_goals SET completed = ? WHERE id = ?", (completed, goal_id))
#             conn.commit()
#         finally:
#             conn.close()
    
#     def delete_personal_goal(self, goal_id):
#         """Delete a personal goal"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute("DELETE FROM personal_goals WHERE id = ?", (goal_id,))
#             conn.commit()
#         finally:
#             conn.close()

#     # ==================== DAILY TASKS ====================
    
#     def add_daily_task(self, user_id, task, category, priority="Medium"):
#         """Add a daily task"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO daily_tasks (user_id, task, category, priority, completed, added) VALUES (?, ?, ?, ?, ?, ?)",
#                 (user_id, task, category, priority, False, datetime.now())
#             )
#             conn.commit()
#             return cursor.lastrowid
#         finally:
#             conn.close()
    
#     def get_daily_tasks(self, user_id):
#         """Get all daily tasks for a user"""
#         conn = self._get_connection()
#         try:
#             query = "SELECT * FROM daily_tasks WHERE user_id = ? ORDER BY added DESC"
#             return pd.read_sql(query, conn, params=(user_id,))
#         finally:
#             conn.close()
    
#     def update_daily_task(self, task_id, completed):
#         """Update task completion status"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             completed_at = datetime.now() if completed else None
#             cursor.execute(
#                 "UPDATE daily_tasks SET completed = ?, completed_at = ? WHERE id = ?", 
#                 (completed, completed_at, task_id)
#             )
#             conn.commit()
#         finally:
#             conn.close()
    
#     def delete_daily_task(self, task_id):
#         """Delete a task"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute("DELETE FROM daily_tasks WHERE id = ?", (task_id,))
#             conn.commit()
#         finally:
#             conn.close()

#     # ==================== CHAT HISTORY ====================
    
#     def add_chat_message(self, user_id, role, content):
#         """Add a chat message"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO chat_history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
#                 (user_id, role, content, datetime.now())
#             )
#             conn.commit()
#         finally:
#             conn.close()
    
#     def get_chat_history(self, user_id, limit=20):
#         """Get chat history for a user"""
#         conn = self._get_connection()
#         try:
#             query = "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC LIMIT ?"
#             return pd.read_sql(query, conn, params=(user_id, limit))
#         finally:
#             conn.close()
    
#     def clear_chat_history(self, user_id):
#         """Clear all chat history for a user"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
#             conn.commit()
#             logger.info(f"Chat history cleared for user {user_id}")
#         finally:
#             conn.close()

#     # ==================== QUIZ RESULTS (NEW) ====================
    
#     def save_quiz_result(self, user_id, subject, question_type, question, user_answer, correct_answer, is_correct, difficulty):
#         """Save a single quiz question result"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO quiz_results (user_id, subject, question_type, question, user_answer, correct_answer, is_correct, difficulty, taken_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
#                 (user_id, subject, question_type, question, user_answer, correct_answer, is_correct, difficulty, datetime.now())
#             )
#             conn.commit()
#         finally:
#             conn.close()
    
#     def save_quiz_session(self, user_id, subject, total_questions, correct_answers, score_percentage, difficulty):
#         """Save overall quiz session summary"""
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "INSERT INTO quiz_sessions (user_id, subject, total_questions, correct_answers, score_percentage, difficulty, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                 (user_id, subject, total_questions, correct_answers, score_percentage, difficulty, datetime.now())
#             )
#             conn.commit()
#             return cursor.lastrowid
#         finally:
#             conn.close()
    
#     def get_quiz_history(self, user_id, subject=None):
#         """Get quiz history for analytics"""
#         conn = self._get_connection()
#         try:
#             if subject:
#                 query = "SELECT * FROM quiz_results WHERE user_id = ? AND subject = ? ORDER BY taken_at DESC"
#                 return pd.read_sql(query, conn, params=(user_id, subject))
#             else:
#                 query = "SELECT * FROM quiz_results WHERE user_id = ? ORDER BY taken_at DESC"
#                 return pd.read_sql(query, conn, params=(user_id,))
#         finally:
#             conn.close()
    
#     def get_quiz_sessions(self, user_id):
#         """Get all quiz session summaries"""
#         conn = self._get_connection()
#         try:
#             query = "SELECT * FROM quiz_sessions WHERE user_id = ? ORDER BY created_at DESC"
#             return pd.read_sql(query, conn, params=(user_id,))
#         finally:
#             conn.close()
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import os
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from src.config.settings import settings

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="growth_companion"):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self._create_indexes()
            logger.info(f"Connected to MongoDB: {db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise CustomException("MongoDB connection failed", e)
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Index on user_id for all collections
            self.db.career_goals.create_index("user_id")
            self.db.personal_goals.create_index("user_id")
            self.db.daily_tasks.create_index("user_id")
            self.db.chat_history.create_index([("user_id", 1), ("timestamp", -1)])
            self.db.quiz_results.create_index([("user_id", 1), ("subject", 1)])
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
        """Get all career goals for a user"""
        try:
            goals = list(self.db.career_goals.find(
                {"user_id": user_id}
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
        """Get all personal goals for a user"""
        try:
            goals = list(self.db.personal_goals.find(
                {"user_id": user_id}
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
        """Get all daily tasks for a user"""
        try:
            tasks = list(self.db.daily_tasks.find(
                {"user_id": user_id}
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
        """Get chat history for a user"""
        try:
            messages = list(self.db.chat_history.find(
                {"user_id": user_id}
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
        """Get quiz history for analytics"""
        try:
            query = {"user_id": user_id}
            if subject:
                query["subject"] = subject
            
            results = list(self.db.quiz_results.find(query).sort("taken_at", -1))
            
            for result in results:
                result['_id'] = str(result['_id'])
            
            return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get quiz history: {e}")
            return pd.DataFrame()
    
    def get_quiz_sessions(self, user_id):
        """Get all quiz session summaries"""
        try:
            sessions = list(self.db.quiz_sessions.find(
                {"user_id": user_id}
            ).sort("created_at", -1))
            
            for session in sessions:
                session['_id'] = str(session['_id'])
            
            return pd.DataFrame(sessions) if sessions else pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to get quiz sessions: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")

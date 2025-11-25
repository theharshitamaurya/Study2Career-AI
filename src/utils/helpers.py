import os
import pandas as pd
from datetime import datetime
from src.models.question_schemas import QuizResult

class QuizManager:
    """Manager for quiz generation, attempt, and evaluation"""
    
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.results = []
        self.subject = None
        self.difficulty = None

    def generate_questions(self, generator, subject: str, topic: str, question_type: str, difficulty: str, num_questions: int):
        """Generate quiz questions using the question generator"""
        self.questions = []
        self.user_answers = []
        self.results = []
        self.subject = subject
        self.difficulty = difficulty

        try:
            for _ in range(num_questions):
                if question_type == "Multiple Choice":
                    question = generator.generate_mcq(topic, difficulty.lower(), subject)

                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_answer': question.correct_answer,
                        'subject': subject,
                        'difficulty': difficulty
                    })

                else:  # Fill in the blank
                    question = generator.generate_fill_blank(topic, difficulty.lower(), subject)

                    self.questions.append({
                        'type': 'Fill in the blank',
                        'question': question.question,
                        'correct_answer': question.answer,
                        'subject': subject,
                        'difficulty': difficulty
                    })
            
            return True
        
        except Exception as e:
            print(f"Error generating questions: {e}")
            return False

    def collect_answer(self, question_index: int, user_answer: str):
        """Collect a single answer"""
        # Ensure user_answers list is long enough
        while len(self.user_answers) <= question_index:
            self.user_answers.append(None)
        
        self.user_answers[question_index] = user_answer

    def evaluate_quiz(self):
        """Evaluate all quiz answers"""
        self.results = []

        for i, q in enumerate(self.questions):
            user_ans = self.user_answers[i] if i < len(self.user_answers) else ""
            
            result_dict = {
                'question_number': i + 1,
                'question': q['question'],
                'question_type': q['type'],
                'user_answer': user_ans,
                'correct_answer': q['correct_answer'],
                'is_correct': False,
                'subject': q['subject'],
                'difficulty': q['difficulty']
            }

            if q['type'] == 'MCQ':
                result_dict['options'] = q['options']
                result_dict['is_correct'] = user_ans == q['correct_answer']
            else:
                result_dict['options'] = []
                result_dict['is_correct'] = user_ans.strip().lower() == q['correct_answer'].strip().lower()

            self.results.append(result_dict)

    def get_score(self):
        """Calculate quiz score"""
        if not self.results:
            return 0, 0, 0
        
        correct_count = sum(1 for r in self.results if r['is_correct'])
        total_questions = len(self.results)
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return correct_count, total_questions, score_percentage

    def generate_result_dataframe(self):
        """Generate pandas DataFrame from results"""
        if not self.results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.results)
    
    def save_to_csv(self, filename_prefix="quiz_results"):
        """Save quiz results to CSV file"""
        if not self.results:
            return None
        
        df = self.generate_result_dataframe()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{filename_prefix}_{self.subject}_{timestamp}.csv"

        os.makedirs('data/quiz_results', exist_ok=True)
        full_path = os.path.join('data/quiz_results', unique_filename)

        try:
            df.to_csv(full_path, index=False)
            return full_path
        except Exception as e:
            print(f"Failed to save results: {e}")
            return None

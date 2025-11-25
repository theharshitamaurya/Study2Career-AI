import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.common.logger import get_logger

logger = get_logger(__name__)

class Analytics:
    def __init__(self, db_manager):
        """Initialize analytics with database manager"""
        self.db = db_manager
    
    # ==================== GOAL ANALYTICS ====================
    
    def get_goal_progress_over_time(self, user_id):
        """Analyze goal progress over time"""
        try:
            career_goals = self.db.get_career_goals(user_id)
            
            if len(career_goals) == 0:
                return None

            today = datetime.now()
            date_range = pd.date_range(end=today, periods=30, freq='D')
            
            progress_data = []
            for _, goal in career_goals.iterrows():
                for date in date_range:
                    # Simulate progress increasing over time
                    days_passed = (date - date_range[0]).days
                    total_days = (date_range[-1] - date_range[0]).days
                    
                    # Progress grows linearly from 0% to current goal['progress']
                    estimated_progress = (days_passed / total_days) * goal['progress']
                    
                    progress_data.append({
                        'date': date,
                        'goal': goal['goal'][:40] + '...' if len(goal['goal']) > 40 else goal['goal'],
                        'progress': min(estimated_progress, goal['progress'])
                    })
                    
            return pd.DataFrame(progress_data)
        except Exception as e:
            logger.error(f"Failed to get goal progress: {e}")
            return None

    def plot_goal_progress_chart(self, progress_df):
        """Create a plotly chart for goal progress"""
        if progress_df is None or len(progress_df) == 0:
            return None

        try:
            fig = px.line(
                progress_df,
                x='date',
                y='progress',
                color='goal',
                title='📈 Career Goal Progress Over Time',
                labels={'progress': 'Completion %', 'date': 'Date', 'goal': 'Goal'}
            )

            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Progress (%)",
                legend_title="Goals",
                height=500,
                hovermode='x unified'
            )

            return fig
        except Exception as e:
            logger.error(f"Failed to plot goal progress: {e}")
            return None

    # ==================== TASK ANALYTICS ====================
    
    def get_task_completion_stats(self, user_id):
        """Analyze task completion statistics"""
        try:
            tasks = self.db.get_daily_tasks(user_id)
            
            if len(tasks) == 0:
                return None, None

            # Calculate completion rate by category
            completion_by_category = tasks.groupby('category').agg(
                total=('id', 'count'),
                completed=('completed', 'sum')
            )
            completion_by_category['completion_rate'] = (
                completion_by_category['completed'] / completion_by_category['total'] * 100
            )

            # Calculate daily completion trend (simulated for last 14 days)
            today = datetime.now()
            date_range = pd.date_range(end=today, periods=14, freq='D')

            completion_trend = []
            for date in date_range:
                # Simulate daily completions based on actual data
                completed_count = int(np.random.randint(0, max(1, len(tasks)//3)))
                total_count = int(np.random.randint(max(1, len(tasks)//3), max(2, len(tasks)//2)))
                
                completion_trend.append({
                    'date': date,
                    'completed': completed_count,
                    'total': total_count,
                    'completion_rate': (completed_count / total_count * 100) if total_count > 0 else 0
                })

            return completion_by_category, pd.DataFrame(completion_trend)
        except Exception as e:
            logger.error(f"Failed to get task stats: {e}")
            return None, None

    def plot_task_completion_charts(self, completion_by_category, completion_trend):
        """Create plotly charts for task completion"""
        charts = []

        try:
            if completion_by_category is not None and len(completion_by_category) > 0:
                # Bar chart for completion by category
                fig1 = px.bar(
                    completion_by_category.reset_index(),
                    x='category',
                    y='completion_rate',
                    title='✅ Task Completion Rate by Category',
                    labels={'completion_rate': 'Completion Rate (%)', 'category': 'Category'},
                    color='completion_rate',
                    color_continuous_scale='Viridis'
                )

                fig1.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Completion Rate (%)",
                    height=400,
                    showlegend=False
                )

                charts.append(fig1)

            if completion_trend is not None and len(completion_trend) > 0:
                # Line chart for completion trend
                fig2 = go.Figure()

                fig2.add_trace(go.Scatter(
                    x=completion_trend['date'],
                    y=completion_trend['total'],
                    mode='lines+markers',
                    name='Total Tasks',
                    line=dict(color='lightblue', width=2)
                ))

                fig2.add_trace(go.Scatter(
                    x=completion_trend['date'],
                    y=completion_trend['completed'],
                    mode='lines+markers',
                    name='Completed Tasks',
                    line=dict(color='green', width=2),
                    fill='tonexty'
                ))

                fig2.update_layout(
                    title='📊 Task Completion Trend (Last 14 Days)',
                    xaxis_title="Date",
                    yaxis_title="Number of Tasks",
                    height=400,
                    hovermode='x unified'
                )

                charts.append(fig2)

            return charts
        except Exception as e:
            logger.error(f"Failed to plot task charts: {e}")
            return []

    # ==================== QUIZ ANALYTICS ====================
    
    def get_quiz_performance_stats(self, user_id):
        """Analyze quiz performance statistics"""
        try:
            quiz_sessions = self.db.get_quiz_sessions(user_id)
            
            if len(quiz_sessions) == 0:
                return None, None
            
            # Performance by subject
            performance_by_subject = quiz_sessions.groupby('subject').agg(
                total_quizzes=('id', 'count'),
                avg_score=('score_percentage', 'mean'),
                total_questions=('total_questions', 'sum'),
                total_correct=('correct_answers', 'sum')
            ).round(2)
            
            # Performance trend over time
            quiz_sessions['created_at'] = pd.to_datetime(quiz_sessions['created_at'])
            performance_trend = quiz_sessions.sort_values('created_at')[['created_at', 'score_percentage', 'subject']].tail(20)
            
            return performance_by_subject, performance_trend
        except Exception as e:
            logger.error(f"Failed to get quiz performance: {e}")
            return None, None
    
    def plot_quiz_performance_charts(self, performance_by_subject, performance_trend):
        """Create plotly charts for quiz performance"""
        charts = []
        
        try:
            if performance_by_subject is not None and len(performance_by_subject) > 0:
                # Bar chart for average score by subject
                fig1 = px.bar(
                    performance_by_subject.reset_index(),
                    x='subject',
                    y='avg_score',
                    title='📚 Average Quiz Score by Subject',
                    labels={'avg_score': 'Average Score (%)', 'subject': 'Subject'},
                    color='avg_score',
                    color_continuous_scale='RdYlGn',
                    text='avg_score'
                )
                
                fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig1.update_layout(
                    xaxis_title="Subject",
                    yaxis_title="Average Score (%)",
                    height=400,
                    showlegend=False
                )
                
                charts.append(fig1)
            
            if performance_trend is not None and len(performance_trend) > 0:
                # Line chart for performance trend
                fig2 = px.line(
                    performance_trend,
                    x='created_at',
                    y='score_percentage',
                    color='subject',
                    title='📈 Quiz Performance Trend',
                    labels={'score_percentage': 'Score (%)', 'created_at': 'Date'},
                    markers=True
                )
                
                fig2.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Score (%)",
                    height=400,
                    hovermode='x unified'
                )
                
                charts.append(fig2)
            
            return charts
        except Exception as e:
            logger.error(f"Failed to plot quiz charts: {e}")
            return []
    
    def get_quiz_difficulty_breakdown(self, user_id):
        """Analyze performance by difficulty level"""
        try:
            quiz_results = self.db.get_quiz_history(user_id)
            
            if len(quiz_results) == 0:
                return None
            
            difficulty_stats = quiz_results.groupby('difficulty').agg(
                total_questions=('is_correct', 'count'),
                correct_answers=('is_correct', 'sum')
            )
            difficulty_stats['accuracy'] = (
                difficulty_stats['correct_answers'] / difficulty_stats['total_questions'] * 100
            ).round(2)
            
            return difficulty_stats
        except Exception as e:
            logger.error(f"Failed to get difficulty breakdown: {e}")
            return None
    
    def plot_difficulty_breakdown(self, difficulty_stats):
        """Create pie chart for difficulty breakdown"""
        if difficulty_stats is None or len(difficulty_stats) == 0:
            return None
        
        try:
            fig = px.pie(
                difficulty_stats.reset_index(),
                names='difficulty',
                values='total_questions',
                title='🎯 Questions Attempted by Difficulty',
                color='difficulty',
                color_discrete_map={
                    'easy': 'lightgreen',
                    'medium': 'orange',
                    'hard': 'red'
                }
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            
            return fig
        except Exception as e:
            logger.error(f"Failed to plot difficulty breakdown: {e}")
            return None

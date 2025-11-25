import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# Import all components
from src.config.settings import settings
from src.database.db_manager import DatabaseManager
from src.generators.question_generator import QuestionGenerator
from src.generators.career_advisor import CareerAdvisor
from src.analytics.visualizations import Analytics
from src.utils.helpers import QuizManager
from src.common.logger import get_logger

logger = get_logger(__name__)

# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title="AI Growth Companion",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION INITIALIZATION ====================

# Anonymous user ID (persistent across session)
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"

USER_ID = st.session_state.user_id

# Initialize managers
if "setup_complete" not in st.session_state:
    try:
        settings.validate()
        st.session_state.db_manager = DatabaseManager()
        st.session_state.question_generator = QuestionGenerator()
        st.session_state.career_advisor = CareerAdvisor()
        st.session_state.analytics = Analytics(st.session_state.db_manager)
        st.session_state.quiz_manager = QuizManager()
        st.session_state.setup_complete = True
        logger.info("Application initialized successfully")
    except Exception as e:
        st.error(f"⚠️ Initialization Error: {e}")
        st.stop()

# Quiz state management
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False

if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

# ==================== SIDEBAR ====================

with st.sidebar:
    st.title("🚀 AI Growth Companion")
    st.markdown("---")
    
    st.markdown("### 👤 User Profile")
    st.info(f"**User ID:** `{USER_ID[:12]}...`")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Stats")
    
    # Get quick stats
    career_goals = st.session_state.db_manager.get_career_goals(USER_ID)
    personal_goals = st.session_state.db_manager.get_personal_goals(USER_ID)
    tasks = st.session_state.db_manager.get_daily_tasks(USER_ID)
    quiz_sessions = st.session_state.db_manager.get_quiz_sessions(USER_ID)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Career Goals", len(career_goals))
        st.metric("Tasks", len(tasks))
    with col2:
        st.metric("Personal Goals", len(personal_goals))
        st.metric("Quizzes Taken", len(quiz_sessions))
    
    st.markdown("---")
    st.markdown("### 🤖 AI Models Used")
    st.markdown(f"""
    - **LLM**: Groq (Llama 3.1)
    - **Embeddings**: HuggingFace  
      `{settings.HF_EMBEDDING_MODEL.split('/')[-1][:20]}`
    - **Sentiment**: HuggingFace  
      `{settings.HF_SENTIMENT_MODEL.split('/')[-1][:20]}`
    """)
    
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit, Groq & HuggingFace")

# ==================== MAIN APP ====================

st.title("🌟 AI Growth Companion")
st.markdown("*Your personal AI-powered learning and career development assistant*")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 Study Coach", 
    "💼 Career Coach", 
    "🎯 Goals & Tasks", 
    "📊 Analytics",
    "⚙️ Settings"
])

# ==================== TAB 1: STUDY COACH ====================

with tab1:
    st.header("📚 AI Study Coach - Quiz Generator")
    st.markdown("Generate personalized quizzes on any topic using AI")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Quiz Settings")
        
        subject = st.text_input(
            "📖 Subject/Course",
            placeholder="e.g., Machine Learning, Biology, History",
            help="The overall subject area"
        )
        
        topic = st.text_input(
            "🎯 Specific Topic",
            placeholder="e.g., Neural Networks, Photosynthesis",
            help="Specific topic within the subject"
        )
        
        question_type = st.selectbox(
            "❓ Question Type",
            ["Multiple Choice", "Fill in the Blank"],
            index=0
        )
        
        difficulty = st.selectbox(
            "⚡ Difficulty Level",
            ["Easy", "Medium", "Hard"],
            index=1
        )
        
        num_questions = st.number_input(
            "🔢 Number of Questions",
            min_value=1,
            max_value=10,
            value=5
        )
        
        st.markdown("---")
        
        if st.button("🎲 Generate Quiz", type="primary", use_container_width=True):
            if not subject or not topic:
                st.error("Please enter both subject and topic")
            else:
                with st.spinner("🤖 Generating quiz using AI..."):
                    success = st.session_state.quiz_manager.generate_questions(
                        st.session_state.question_generator,
                        subject,
                        topic,
                        question_type,
                        difficulty,
                        num_questions
                    )
                    
                    if success:
                        st.session_state.quiz_generated = True
                        st.session_state.quiz_submitted = False
                        st.success("✅ Quiz generated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate quiz")
    
    with col2:
        if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
            st.subheader("📝 Take Your Quiz")
            
            # Display questions
            for i, q in enumerate(st.session_state.quiz_manager.questions):
                st.markdown(f"### Question {i+1}")
                st.markdown(f"**{q['question']}**")
                
                if q['type'] == 'MCQ':
                    user_answer = st.radio(
                        f"Select your answer for Question {i+1}",
                        q['options'],
                        key=f"mcq_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.quiz_manager.collect_answer(i, user_answer)
                
                else:  # Fill in the blank
                    user_answer = st.text_input(
                        f"Fill in the blank for Question {i+1}",
                        key=f"fill_blank_{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.quiz_manager.collect_answer(i, user_answer)
                
                st.markdown("---")
            
            # Submit button
            if st.button("📤 Submit Quiz", type="primary", use_container_width=True):
                st.session_state.quiz_manager.evaluate_quiz()
                
                # Save to database
                correct, total, score_pct = st.session_state.quiz_manager.get_score()
                
                # Save session summary
                st.session_state.db_manager.save_quiz_session(
                    USER_ID,
                    st.session_state.quiz_manager.subject,
                    total,
                    correct,
                    score_pct,
                    st.session_state.quiz_manager.difficulty
                )
                
                # Save individual results
                for result in st.session_state.quiz_manager.results:
                    st.session_state.db_manager.save_quiz_result(
                        USER_ID,
                        result['subject'],
                        result['question_type'],
                        result['question'],
                        result['user_answer'],
                        result['correct_answer'],
                        result['is_correct'],
                        result['difficulty']
                    )
                
                st.session_state.quiz_submitted = True
                st.rerun()
        
        elif not st.session_state.quiz_generated:
            st.info("👈 Configure your quiz settings and click 'Generate Quiz' to start")
    
    # Show results
    if st.session_state.quiz_submitted:
        st.markdown("---")
        st.subheader("🎯 Quiz Results")
        
        correct, total, score_pct = st.session_state.quiz_manager.get_score()
        
        # Score display
        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Correct", correct)
        col2.metric("📊 Total", total)
        col3.metric("🎯 Score", f"{score_pct:.1f}%")
        
        # Detailed results
        st.markdown("### Detailed Results")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()
        
        for _, result in results_df.iterrows():
            question_num = result['question_number']
            
            if result['is_correct']:
                st.success(f"✅ **Question {question_num}**: {result['question']}")
            else:
                st.error(f"❌ **Question {question_num}**: {result['question']}")
                st.markdown(f"**Your answer:** {result['user_answer']}")
                st.markdown(f"**Correct answer:** {result['correct_answer']}")
            
            st.markdown("---")
        
        # Download results
        if st.button("💾 Save Results to CSV"):
            saved_file = st.session_state.quiz_manager.save_to_csv()
            if saved_file:
                st.success(f"Results saved to: {saved_file}")
        
        # Reset button
        if st.button("🔄 Take New Quiz"):
            st.session_state.quiz_generated = False
            st.session_state.quiz_submitted = False
            st.session_state.quiz_manager = QuizManager()
            st.rerun()

# ==================== TAB 2: CAREER COACH ====================

with tab2:
    st.header("💼 AI Career Coach")
    st.markdown("Get personalized career advice powered by AI")
    
    # Chat history
    chat_history = st.session_state.db_manager.get_chat_history(USER_ID)
    
    # Clear chat button
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.db_manager.clear_chat_history(USER_ID)
            st.success("Chat cleared!")
            st.rerun()
    
    # Display chat history
    if not chat_history.empty:
        for _, msg in chat_history.iterrows():
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
    
    # Chat input
    if prompt := st.chat_input("Ask about career growth, skill development, job search..."):
        # Add user message to database
        st.session_state.db_manager.add_chat_message(USER_ID, "user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get context
        career_goals_list = st.session_state.db_manager.get_career_goals(USER_ID).to_dict('records')
        personal_goals_list = st.session_state.db_manager.get_personal_goals(USER_ID).to_dict('records')
        tasks_list = st.session_state.db_manager.get_daily_tasks(USER_ID).to_dict('records')
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.career_advisor.generate_career_advice(
                    prompt,
                    career_goals_list,
                    personal_goals_list,
                    tasks_list
                )
                st.markdown(response)
        
        # Save assistant response
        st.session_state.db_manager.add_chat_message(USER_ID, "assistant", response)

# ==================== TAB 3: GOALS & TASKS ====================

with tab3:
    st.header("🎯 Goals & Tasks Manager")
    
    subtab1, subtab2, subtab3 = st.tabs(["📈 Career Goals", "🌱 Personal Goals", "✅ Daily Tasks"])
    
    # Career Goals
    with subtab1:
        st.subheader("📈 Career Goals")
        
        with st.expander("➕ Add New Career Goal", expanded=False):
            with st.form("career_goal_form"):
                goal = st.text_input("Goal Description")
                col1, col2 = st.columns(2)
                deadline = col1.date_input("Target Date")
                priority = col2.selectbox("Priority", ["🚀 High", "🔄 Medium", "📅 Low"])
                notes = st.text_area("Notes (Optional)")
                
                if st.form_submit_button("Add Goal", use_container_width=True):
                    if goal:
                        st.session_state.db_manager.add_career_goal(
                            USER_ID, goal, deadline, priority, notes
                        )
                        st.success("Career goal added!")
                        st.rerun()
                    else:
                        st.error("Please enter a goal")
        
        # Display career goals
        career_goals = st.session_state.db_manager.get_career_goals(USER_ID)
        
        if len(career_goals) == 0:
            st.info("No career goals yet. Add your first goal above!")
        else:
            for _, goal in career_goals.iterrows():
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    col1.markdown(f"**{goal['goal']}**")
                    col2.write(f"📅 {goal['deadline']}")
                    col3.write(f"{goal['priority']}")
                    
                    # Progress slider
                    progress = st.slider(
                        "Progress",
                        0, 100,
                        int(goal['progress']),
                        key=f"career_{goal['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if progress != goal['progress']:
                        st.session_state.db_manager.update_career_goal(goal['id'], progress)
                        st.rerun()
                    
                    if col4.button("🗑️", key=f"del_career_{goal['id']}"):
                        st.session_state.db_manager.delete_career_goal(goal['id'])
                        st.rerun()
    
    # Personal Goals
    with subtab2:
        st.subheader("🌱 Personal Development Goals")
        
        with st.expander("➕ Add Personal Goal", expanded=False):
            with st.form("personal_goal_form"):
                goal = st.text_input("Goal Description")
                category = st.selectbox("Category", [
                    "❤️ Health", "🧠 Skills", "🤝 Relationships", "🧘 Mindfulness"
                ])
                notes = st.text_area("Notes (Optional)")
                
                if st.form_submit_button("Add Goal", use_container_width=True):
                    if goal:
                        st.session_state.db_manager.add_personal_goal(
                            USER_ID, goal, category, notes
                        )
                        st.success("Personal goal added!")
                        st.rerun()
                    else:
                        st.error("Please enter a goal")
        
        # Display personal goals
        personal_goals = st.session_state.db_manager.get_personal_goals(USER_ID)
        
        if len(personal_goals) == 0:
            st.info("No personal goals yet. Add your first goal above!")
        else:
            for _, goal in personal_goals.iterrows():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                
                completed = col1.checkbox(
                    "",
                    bool(goal['completed']),
                    key=f"personal_{goal['id']}"
                )
                
                if completed != bool(goal['completed']):
                    st.session_state.db_manager.update_personal_goal(goal['id'], completed)
                    st.rerun()
                
                col2.write(f"**{goal['goal']}**")
                col3.write(goal['category'])
                
                if col4.button("🗑️", key=f"del_personal_{goal['id']}"):
                    st.session_state.db_manager.delete_personal_goal(goal['id'])
                    st.rerun()
    
    # Daily Tasks
    with subtab3:
        st.subheader("✅ Daily Task Manager")
        
        with st.expander("➕ Add New Task", expanded=False):
            with st.form("task_form"):
                task = st.text_input("Task Description")
                col1, col2 = st.columns(2)
                category = col1.selectbox("Category", ["💼 Work", "📚 Learning", "🏋️ Health", "🏠 Personal"])
                priority = col2.selectbox("Priority", ["High", "Medium", "Low"])
                
                if st.form_submit_button("Add Task", use_container_width=True):
                    if task:
                        st.session_state.db_manager.add_daily_task(
                            USER_ID, task, category, priority
                        )
                        st.success("Task added!")
                        st.rerun()
                    else:
                        st.error("Please enter a task")
        
        # Display tasks
        tasks = st.session_state.db_manager.get_daily_tasks(USER_ID)
        
        if len(tasks) == 0:
            st.info("No tasks yet. Add your first task above!")
        else:
            for _, task in tasks.iterrows():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                
                completed = col1.checkbox(
                    "",
                    bool(task['completed']),
                    key=f"task_{task['id']}"
                )
                
                if completed != bool(task['completed']):
                    st.session_state.db_manager.update_daily_task(task['id'], completed)
                    st.rerun()
                
                col2.write(task['task'])
                col3.write(f"{task['category']} | {task['priority']}")
                
                if col4.button("🗑️", key=f"del_task_{task['id']}"):
                    st.session_state.db_manager.delete_daily_task(task['id'])
                    st.rerun()

# ==================== TAB 4: ANALYTICS ====================

with tab4:
    st.header("📊 Progress Analytics")
    
    # Goal Progress
    st.subheader("📈 Career Goal Progress")
    progress_df = st.session_state.analytics.get_goal_progress_over_time(USER_ID)
    if progress_df is not None and len(progress_df) > 0:
        chart = st.session_state.analytics.plot_goal_progress_chart(progress_df)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("Add career goals to see progress analytics")
    
    st.markdown("---")
    
    # Task Analytics
    st.subheader("✅ Task Completion Analytics")
    completion_by_category, completion_trend = st.session_state.analytics.get_task_completion_stats(USER_ID)
    
    if completion_by_category is not None:
        charts = st.session_state.analytics.plot_task_completion_charts(
            completion_by_category, completion_trend
        )
        
        if len(charts) > 0:
            col1, col2 = st.columns(2)
            if len(charts) > 0:
                col1.plotly_chart(charts[0], use_container_width=True)
            if len(charts) > 1:
                col2.plotly_chart(charts[1], use_container_width=True)
    else:
        st.info("Complete tasks to see analytics")
    
    st.markdown("---")
    
    # Quiz Analytics
    st.subheader("📚 Quiz Performance Analytics")
    performance_by_subject, performance_trend = st.session_state.analytics.get_quiz_performance_stats(USER_ID)
    
    if performance_by_subject is not None:
        charts = st.session_state.analytics.plot_quiz_performance_charts(
            performance_by_subject, performance_trend
        )
        
        if len(charts) > 0:
            col1, col2 = st.columns(2)
            if len(charts) > 0:
                col1.plotly_chart(charts[0], use_container_width=True)
            if len(charts) > 1:
                col2.plotly_chart(charts[1], use_container_width=True)
        
        # Difficulty breakdown
        difficulty_stats = st.session_state.analytics.get_quiz_difficulty_breakdown(USER_ID)
        if difficulty_stats is not None:
            difficulty_chart = st.session_state.analytics.plot_difficulty_breakdown(difficulty_stats)
            if difficulty_chart:
                st.plotly_chart(difficulty_chart, use_container_width=True)
    else:
        st.info("Take quizzes to see performance analytics")

# ==================== TAB 5: SETTINGS ====================

with tab5:
    st.header("⚙️ Settings & Information")
    
    st.subheader("🤖 AI Configuration")
    st.markdown(f"""
    - **LLM Provider**: Groq
    - **Model**: {settings.GROQ_MODEL}
    - **Temperature**: {settings.GROQ_TEMPERATURE}
    - **HuggingFace Embeddings**: {settings.HF_EMBEDDING_MODEL}
    - **HuggingFace Sentiment**: {settings.HF_SENTIMENT_MODEL}
    """)
    
    st.markdown("---")
    
    st.subheader("💾 Data Export")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("📥 Export Goals"):
        career_goals = st.session_state.db_manager.get_career_goals(USER_ID)
        personal_goals = st.session_state.db_manager.get_personal_goals(USER_ID)
        
        if len(career_goals) > 0 or len(personal_goals) > 0:
            combined = pd.concat([
                career_goals.assign(type="career"),
                personal_goals.assign(type="personal")
            ])
            
            st.download_button(
                label="Download Goals CSV",
                data=combined.to_csv(index=False).encode('utf-8'),
                file_name=f"goals_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    if col2.button("📥 Export Tasks"):
        tasks = st.session_state.db_manager.get_daily_tasks(USER_ID)
        
        if len(tasks) > 0:
            st.download_button(
                label="Download Tasks CSV",
                data=tasks.to_csv(index=False).encode('utf-8'),
                file_name=f"tasks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    if col3.button("📥 Export Quiz Results"):
        quiz_history = st.session_state.db_manager.get_quiz_history(USER_ID)
        
        if len(quiz_history) > 0:
            st.download_button(
                label="Download Quiz History CSV",
                data=quiz_history.to_csv(index=False).encode('utf-8'),
                file_name=f"quiz_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    st.markdown("---")
    
    st.subheader("ℹ️ About")
    st.markdown("""
    **AI Growth Companion** combines intelligent study coaching with career development planning.
    
    **Features:**
    - 📚 AI-powered quiz generation with HuggingFace embeddings for question diversity
    - 💼 Career coaching with sentiment-aware responses
    - 🎯 Goal and task management with progress tracking
    - 📊 Comprehensive analytics and visualizations
    
    **Technologies:**
    - Streamlit (UI)
    - MongoDB (Database)
    - Groq (LLM Generation)
    - HuggingFace (Embeddings & Sentiment Analysis)
    - Plotly (Visualizations)
    """)

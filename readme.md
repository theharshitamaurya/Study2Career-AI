# 🚀 AI Growth Companion

A comprehensive AI-powered platform combining intelligent study coaching with career development planning. Built with Streamlit, Groq, HuggingFace, and MongoDB.

## ✨ Features

### 📚 AI Study Coach

- Generate personalized quizzes (MCQ & Fill-in-blank) on any topic
- HuggingFace embeddings ensure question diversity
- Quiz history tracking and performance analytics
- Export results to CSV

### 💼 AI Career Coach

- Sentiment-aware career advice using HuggingFace models
- Context-aware responses based on your goals
- Personalized recommendations and action plans

### 🎯 Goals & Tasks Management

- Career goal tracking with progress visualization
- Personal development goals across multiple categories
- Daily task manager with priority levels
- Goal-task linkage

### 📊 Advanced Analytics

- Goal progress visualization over time
- Task completion rates by category
- Quiz performance trends by subject
- Difficulty-level breakdown

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Database**: MongoDB
- **LLM**: Groq (Llama 3.1)
- **Embeddings**: HuggingFace Sentence Transformers
- **Sentiment Analysis**: HuggingFace RoBERTa
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Framework**: LangChain

## 📋 Prerequisites

- Python 3.9+
- MongoDB (local or cloud instance)
- Groq API key
- HuggingFace account (optional, for API access)

## 🚀 Installation

1. **Clone the repository**
   git clone [Study2Career-AI](https://github.com/theharshitamaurya/Study2Career-AI.git)
   cd ai-growth-companion

2. **Create virtual environment**
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate

3. **Install dependencies**
   pip install -r requirements.txt

4. **Set up environment variables**
   cp .env.example .env

Edit `.env` and add your API keys:

- Get Groq API key from: https://console.groq.com
- HuggingFace token (optional): https://huggingface.co/settings/tokens

5. **Start MongoDB**
   mongod

## 🎯 Usage

1. **Run the application**
   streamlit run app.py

2. **Access the app**
   Open your browser and navigate to `http://localhost:8501`

3. **Start using features**

- Generate quizzes in the Study Coach tab
- Chat with AI career advisor
- Set goals and manage tasks
- View analytics and progress

## 📁 Project Structure

```
ai-growth-companion/
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── .env.example # Environment variables template
├── README.md # Project documentation
│
├── src/
│ ├── config/
│ │ └── settings.py # Configuration management
│ │
│ ├── common/
│ │ ├── logger.py # Logging setup
│ │ └── custom_exception.py # Exception handling
│ │
│ ├── database/
│ │ ├── db_manager.py # MongoDB operations
│ │ └── models.py # Pydantic models
│ │
│ ├── generators/
│ │ ├── question_generator.py # Quiz generation with HF
│ │ └── career_advisor.py # Career advice with HF
│ │
│ ├── models/
│ │ ├── question_schemas.py # Quiz data models
│ │ └── goal_schemas.py # Goal/task data models
│ │
│ ├── prompts/
│ │ ├── quiz_templates.py # Quiz generation prompts
│ │ └── career_templates.py # Career advice prompts
│ │
│ ├── analytics/
│ │ └── visualizations.py # Plotly charts
│ │
│ └── utils/
│ └── helpers.py # Utility functions
│
├── data/ # Created automatically
│ └── quiz_results/ # Exported quiz results
│
└── logs/ # Application logs
```

## 🎓 HuggingFace Integration Highlights

### 1. **Sentence Embeddings**

Uses `sentence-transformers/all-MiniLM-L6-v2` for:

- Question similarity detection (prevents duplicate questions)
- Semantic context retrieval
- Goal and task similarity analysis

### 2. **Sentiment Analysis**

Uses `cardiffnlp/twitter-roberta-base-sentiment-latest` for:

- User emotion detection in career coaching
- Adaptive response tone
- Conversation context awareness

### 3. **Model Features**

- Automatic model caching
- GPU acceleration when available
- Fallback to CPU for compatibility

## 📊 Data Storage

All data is stored in MongoDB with the following collections:

- `career_goals` - Career objectives with progress tracking
- `personal_goals` - Personal development goals
- `daily_tasks` - Task management
- `chat_history` - Career coaching conversations
- `quiz_results` - Individual question results
- `quiz_sessions` - Quiz attempt summaries

## 🔧 Configuration

Key settings in `.env`:

API Keys
GROQ_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here # Optional

Models
GROQ_MODEL=llama-3.1-8b-instant
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HF_SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest

Database
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=growth_companion

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- Additional quiz question types
- More HuggingFace model integrations
- Advanced analytics features
- Mobile responsive design improvements

## 📝 License

MIT License - feel free to use for personal or commercial projects

## 👤 Author

**Harshita Maurya**

- GitHub: [@theharshitamaurya](https://github.com/theharshitamaurya)
- Project: AI Growth Companion

## 🙏 Acknowledgments

- Groq for fast LLM inference
- HuggingFace for open-source models
- Streamlit for the amazing framework
- MongoDB for flexible data storage

---

⭐ Star this repo if it helped you!

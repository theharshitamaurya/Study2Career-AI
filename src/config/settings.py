import os
from dotenv import load_dotenv

# Try to import Streamlit for secrets support (safe if not on cloud)
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

class Settings:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    
    # Groq Configuration
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    
    # HuggingFace Models
    HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    HF_SENTIMENT_MODEL = os.getenv("HF_SENTIMENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest")
    HF_TEXT_MODEL = os.getenv("HF_TEXT_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    
    # MongoDB Connection (Atlas/Cloud)
    # Try to get URI from Streamlit secrets if running online, fallback to ENV for local dev
    MONGO_URI = (
        st.secrets["MONGO_URI"] if st is not None and "MONGO_URI" in st.secrets
        else os.getenv("MONGO_URI")
    )
    
    # Application
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "20"))
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        if not cls.MONGO_URI:
            raise ValueError("MONGO_URI not found in environment variables or Streamlit secrets!")
        return True

settings = Settings()

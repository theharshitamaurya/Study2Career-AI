from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

# HuggingFace imports
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import torch

logger = get_logger(__name__)

class CareerAdvisor:
    def __init__(self):
        """Initialize Career Advisor with Groq LLM and HuggingFace models"""
        # Groq for main generation
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE
        )
        
        # HuggingFace embeddings for context retrieval
        try:
            self.embedding_model = SentenceTransformer(settings.HF_EMBEDDING_MODEL)
            logger.info(f"Loaded HuggingFace embedding model: {settings.HF_EMBEDDING_MODEL}")
        except Exception as e:
            logger.warning(f"Failed to load embeddings: {e}")
            self.embedding_model = None
        
        # HuggingFace sentiment analysis for user emotion detection
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=settings.HF_SENTIMENT_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Loaded HuggingFace sentiment model: {settings.HF_SENTIMENT_MODEL}")
        except Exception as e:
            logger.warning(f"Failed to load sentiment analyzer: {e}")
            self.sentiment_analyzer = None
        
        self.logger = get_logger(self.__class__.__name__)
    
    def analyze_user_sentiment(self, user_message: str) -> dict:
        """
        Analyze sentiment of user message using HuggingFace
        Returns: {'label': 'positive/negative/neutral', 'score': float}
        """
        if not self.sentiment_analyzer:
            return {"label": "neutral", "score": 0.5}
        
        try:
            result = self.sentiment_analyzer(user_message[:512])[0]  # Limit to 512 chars
            logger.info(f"Sentiment: {result['label']} ({result['score']:.2f})")
            return result
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {"label": "neutral", "score": 0.5}
    
    def get_context_embedding(self, context: str):
        """Get embedding for context using HuggingFace"""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(context)
            return embedding
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None
    
    def generate_career_advice(self, user_query: str, career_goals: list, personal_goals: list, tasks: list) -> str:
        """
        Generate personalized career advice based on user goals and current state
        Uses HuggingFace for sentiment analysis and Groq for generation
        """
        try:
            # Analyze user sentiment
            sentiment = self.analyze_user_sentiment(user_query)
            
            # Build context from user data
            context = self._build_context(career_goals, personal_goals, tasks)
            
            # Adjust tone based on sentiment
            tone_instruction = self._get_tone_instruction(sentiment)
            
            # Create prompt
            prompt = PromptTemplate(
                template="""You are an expert career coach and life advisor. 
                
{tone_instruction}

User Context:
{context}

User Question: {query}

Provide personalized, actionable advice that:
1. Directly addresses their question
2. References their specific goals and tasks
3. Suggests concrete next steps
4. Is encouraging and supportive

Response:""",
                input_variables=["tone_instruction", "context", "query"]
            )
            
            formatted_prompt = prompt.format(
                tone_instruction=tone_instruction,
                context=context,
                query=user_query
            )
            
            # Generate response with Groq
            response = self.llm.invoke(formatted_prompt)
            
            self.logger.info("Career advice generated successfully")
            return response.content
        
        except Exception as e:
            self.logger.error(f"Failed to generate career advice: {e}")
            raise CustomException("Career advice generation failed", e)
    
    def _build_context(self, career_goals: list, personal_goals: list, tasks: list) -> str:
        """Build context string from user data"""
        context_parts = []
        
        if career_goals:
            career_str = "\n".join([f"- {g['goal']} (Progress: {g['progress']}%)" for g in career_goals[:5]])
            context_parts.append(f"Career Goals:\n{career_str}")
        
        if personal_goals:
            personal_str = "\n".join([f"- {g['goal']} ({g['category']})" for g in personal_goals[:5]])
            context_parts.append(f"Personal Goals:\n{personal_str}")
        
        if tasks:
            task_str = "\n".join([f"- {t['task']} ({t['category']})" for t in tasks[:5]])
            context_parts.append(f"Recent Tasks:\n{task_str}")
        
        return "\n\n".join(context_parts) if context_parts else "No goals or tasks set yet."
    
    def _get_tone_instruction(self, sentiment: dict) -> str:
        """Get tone instruction based on sentiment analysis"""
        label = sentiment.get('label', 'neutral').lower()
        score = sentiment.get('score', 0.5)
        
        if 'negative' in label or 'neg' in label:
            return "The user seems frustrated or discouraged. Be extra supportive, empathetic, and focus on small achievable wins."
        elif 'positive' in label or 'pos' in label:
            return "The user seems motivated and positive. Match their energy with encouraging, ambitious advice."
        else:
            return "Maintain a balanced, professional yet warm tone."
    
    def generate_goal_suggestions(self, user_profile: dict, goal_type: str = "career") -> list:
        """
        Generate personalized goal suggestions based on user profile
        
        Args:
            user_profile: Dict with keys like 'interests', 'skills', 'experience_level'
            goal_type: 'career' or 'personal'
        
        Returns:
            List of suggested goals
        """
        try:
            prompt = PromptTemplate(
                template="""Based on this user profile, suggest 5 specific, achievable {goal_type} goals.

User Profile:
{profile}

Provide goals as a numbered list. Each goal should be:
- Specific and measurable
- Achievable within 3-6 months
- Relevant to their background

Goals:""",
                input_variables=["goal_type", "profile"]
            )
            
            profile_str = "\n".join([f"{k}: {v}" for k, v in user_profile.items()])
            
            response = self.llm.invoke(prompt.format(
                goal_type=goal_type,
                profile=profile_str
            ))
            
            # Parse numbered list
            goals = [line.strip() for line in response.content.split('\n') if line.strip() and line[0].isdigit()]
            
            self.logger.info(f"Generated {len(goals)} {goal_type} goal suggestions")
            return goals[:5]
        
        except Exception as e:
            self.logger.error(f"Failed to generate goal suggestions: {e}")
            return []

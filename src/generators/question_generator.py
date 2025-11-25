from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.quiz_templates import (
    mcq_prompt_template,
    fill_blank_prompt_template,
)
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

from sentence_transformers import SentenceTransformer
import numpy as np


logger = get_logger(__name__)


class QuestionGenerator:
    def __init__(self) -> None:
        """Initialize question generator with Groq LLM and HuggingFace embeddings."""
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
        )

        # Try to load HuggingFace embedding model for similarity checks
        try:
            self.embedding_model = SentenceTransformer(settings.HF_EMBEDDING_MODEL)
            logger.info(
                f"Loaded HuggingFace embedding model: {settings.HF_EMBEDDING_MODEL}"
            )
        except Exception as e:
            logger.warning(f"Failed to load HuggingFace embeddings: {e}")
            self.embedding_model = None

        self.logger = get_logger(self.__class__.__name__)
        self.generated_questions: list[str] = []

    def _check_question_similarity(
        self, new_question: str, threshold: float = 0.85
    ) -> bool:
        """Return True if new_question is too similar to previous ones."""
        if not self.embedding_model or not self.generated_questions:
            return False

        try:
            new_embedding = self.embedding_model.encode(new_question)

            for prev_question in self.generated_questions:
                prev_embedding = self.embedding_model.encode(prev_question)

                similarity = np.dot(new_embedding, prev_embedding) / (
                    np.linalg.norm(new_embedding) * np.linalg.norm(prev_embedding)
                )

                if similarity > threshold:
                    logger.info(
                        f"Question too similar (similarity: {similarity:.2f}), regenerating..."
                    )
                    return True

            return False
        except Exception as e:
            logger.warning(f"Similarity check failed: {e}")
            return False

    def _retry_and_parse(self, prompt, parser, topic, difficulty, subject=None):
        """Generic retry loop with parsing and similarity checking."""
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(
                    f"Generating question for topic '{topic}' "
                    f"with difficulty '{difficulty}' (attempt {attempt + 1})"
                )

                response = self.llm.invoke(
                    prompt.format(
                        topic=topic,
                        difficulty=difficulty,
                        subject=subject or topic,
                    )
                )

                parsed = parser.parse(response.content)

                # Similarity check
                if self._check_question_similarity(parsed.question):
                    if attempt < settings.MAX_RETRIES - 1:
                        continue
                    logger.warning(
                        "Max retries reached, using potentially similar question"
                    )

                self.generated_questions.append(parsed.question)

                self.logger.info("Successfully parsed and validated question")
                return parsed

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(
                        f"Generation failed after {settings.MAX_RETRIES} attempts", e
                    )

    def generate_mcq(
        self, topic: str, difficulty: str = "medium", subject: str | None = None
    ) -> MCQQuestion:
        """Generate a multiple-choice question."""
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)

            question: MCQQuestion = self._retry_and_parse(
                mcq_prompt_template,
                parser,
                topic,
                difficulty,
                subject,
            )

            if len(question.options) != 4:
                raise ValueError("Invalid MCQ: must have exactly 4 options")

            if question.correct_answer not in question.options:
                raise ValueError("Invalid MCQ: correct answer not in options")

            question.difficulty = difficulty
            question.subject = subject or topic

            self.logger.info(f"Generated valid MCQ for {subject or topic}")
            return question

        except Exception as e:
            self.logger.error(f"Failed to generate MCQ: {str(e)}")
            raise CustomException("MCQ generation failed", e)

    def generate_fill_blank(
        self, topic: str, difficulty: str = "medium", subject: str | None = None
    ) -> FillBlankQuestion:
        """Generate a fill-in-the-blank question."""
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question: FillBlankQuestion = self._retry_and_parse(
                fill_blank_prompt_template,
                parser,
                topic,
                difficulty,
                subject,
            )

            if "___" not in question.question and "_____" not in question.question:
                raise ValueError("Fill-in-blank must contain '___'")

            question.difficulty = difficulty
            question.subject = subject or topic

            self.logger.info(f"Generated valid fill-in-blank for {subject or topic}")
            return question

        except Exception as e:
            self.logger.error(f"Failed to generate fill-in-blank: {str(e)}")
            raise CustomException("Fill-in-blank generation failed", e)

    def clear_question_history(self) -> None:
        """Clear the history of generated questions."""
        self.generated_questions = []
        logger.info("Question generation history cleared")

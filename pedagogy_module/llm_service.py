import logging
from langchain_ollama import ChatOllama
from pedagogy_module.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model_name = settings.LLM_MODEL
        logger.info(f"Initializing ChatOllama with host={self.host}, model={self.model_name}")
        
        self.llm = ChatOllama(
            base_url=self.host,
            model=self.model_name,
            temperature=0.1,
        )
        
    def get_llm(self) -> ChatOllama:
        return self.llm

llm_service = LLMService()

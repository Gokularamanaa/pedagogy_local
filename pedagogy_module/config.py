import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    OLLAMA_HOST: str = "http://localhost:11434"
    LLM_MODEL: str = "qwen2.5:3b"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    
    @property
    def KB_DIR(self) -> str:
        return os.path.join(self.BASE_DIR, "knowledge_base")
        
    @property
    def OUTPUT_DIR(self) -> str:
        return os.path.join(self.BASE_DIR, "output")
        
    # FastAPI Server
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

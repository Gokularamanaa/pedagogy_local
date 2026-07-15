import json
import logging
from langchain_core.prompts import PromptTemplate
from pedagogy_module.llm_service import llm_service
from pedagogy_module.prompt_templates import TOPIC_EXTRACTION_PROMPT
from pedagogy_module.models import ExtractedSyllabus
from pedagogy_module.utils import clean_json_string

logger = logging.getLogger(__name__)

class TopicExtractor:
    def __init__(self):
        self.llm = llm_service.get_llm()
        self.prompt = PromptTemplate.from_template(TOPIC_EXTRACTION_PROMPT)
        self.chain = self.prompt | self.llm

    def extract(self, subject_name: str, syllabus_text: str) -> ExtractedSyllabus:
        """
        Invokes the Ollama LLM to extract units and sub-topics from the raw syllabus text.
        Validates output using the ExtractedSyllabus Pydantic schema.
        """
        logger.info(f"Invoking LLM for topic extraction on subject: {subject_name}")
        
        try:
            response = self.chain.invoke({
                "subject_name": subject_name,
                "syllabus_text": syllabus_text
            })
            
            raw_content = response.content
            logger.debug(f"Raw LLM Extraction output: {raw_content}")
            
            cleaned_json = clean_json_string(raw_content)
            data = json.loads(cleaned_json)
            
            # Normalize schema differences if any
            if "subject_name" not in data and "subject" in data:
                data["subject_name"] = data["subject"]
            elif "subject_name" not in data:
                data["subject_name"] = subject_name
                
            return ExtractedSyllabus(**data)
            
        except Exception as e:
            logger.error(f"Error during topic extraction: {e}")
            raise ValueError(f"Failed to parse topic extraction response into expected schema: {str(e)}")

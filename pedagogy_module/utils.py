import os
import json
import logging
import re
from typing import Any
from pedagogy_module.config import settings

logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Any:
    """
    Load a JSON file securely.
    """
    if not os.path.exists(file_path):
        logger.error(f"JSON file not found at path: {file_path}")
        raise FileNotFoundError(f"JSON file not found at {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        raise

def clean_json_string(text: str) -> str:
    """
    Cleans raw LLM outputs to extract valid JSON string.
    Removes markdown code blocks (e.g. ```json ... ```) and leading/trailing whitespace.
    """
    text = text.strip()
    
    # 1. Regex to extract code block content
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        text = match.group(1).strip()
        
    # 2. Find first and last valid JSON characters to clip any trailing preambles
    first_brace = text.find('{')
    first_bracket = text.find('[')
    
    start_idx = -1
    end_tag = ''
    
    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        start_idx = first_brace
        end_tag = '}'
    elif first_bracket != -1:
        start_idx = first_bracket
        end_tag = ']'
        
    if start_idx != -1:
        last_idx = text.rfind(end_tag)
        if last_idx != -1:
            text = text[start_idx:last_idx+1]
            
    return text.strip()

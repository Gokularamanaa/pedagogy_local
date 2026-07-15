import os
import json
import re
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from langchain_core.prompts import PromptTemplate
from pedagogy_module.config import settings
from pedagogy_module.llm_service import llm_service
from pedagogy_module.prompt_templates import PEDAGOGY_RECOMMENDATION_PROMPT
from pedagogy_module.models import TopicRecommendation, PedagogyRecommendation, ExtractedSyllabus
from pedagogy_module.utils import load_json_file, clean_json_string

logger = logging.getLogger(__name__)

class PedagogyEngine:
    def __init__(self):
        self.llm = llm_service.get_llm()
        self.prompt = PromptTemplate.from_template(PEDAGOGY_RECOMMENDATION_PROMPT)
        self.chain = self.prompt | self.llm
        
        # Load Knowledge Base
        pedagogies_path = os.path.join(settings.KB_DIR, "pedagogy.json")
        bloom_path = os.path.join(settings.KB_DIR, "bloom_mapping.json")
        
        self.pedagogies_data = load_json_file(pedagogies_path)
        self.bloom_mapping = load_json_file(bloom_path)
        
        # Format pedagogies reference text for the prompt
        self.pedagogies_reference = ""
        for p in self.pedagogies_data.get("pedagogies", []):
            self.pedagogies_reference += f"- {p['name']}: {p['description']} (Bloom's levels: {', '.join(p.get('blooms_levels', []))})\n"

    def classify_blooms_level(self, topic: str) -> str:
        """
        Classifies the Bloom's Taxonomy cognitive level based on keywords in the topic.
        """
        topic_lower = topic.lower()
        scores = {level: 0 for level in self.bloom_mapping.keys()}
        
        for level, keywords in self.bloom_mapping.items():
            for kw in keywords:
                # Match whole words to avoid partial match bugs (e.g. "search" matching "research")
                pattern = r'\b' + re.escape(kw.lower()) + r'\b'
                if re.search(pattern, topic_lower):
                    scores[level] += 2
                elif kw.lower() in topic_lower:
                    scores[level] += 1
                    
        best_level = max(scores, key=scores.get)
        if scores[best_level] > 0:
            return best_level
            
        return "Understand"  # Default fallback if no keywords match

    def recommend_for_topic(self, subject_name: str, unit_name: str, unit_topics: List[str], current_topic: str) -> TopicRecommendation:
        """
        Runs the pedagogy recommendation LLM prompt for a single topic using the unit topics as context.
        """
        logger.info(f"Recommending pedagogies for topic: '{current_topic}' (Unit: '{unit_name}')")
        blooms_level = self.classify_blooms_level(current_topic)
        
        topics_context = "\n".join([f"- {t}" for t in unit_topics])
        
        try:
            response = self.chain.invoke({
                "subject_name": subject_name,
                "unit_name": unit_name,
                "unit_topics": topics_context,
                "current_topic": current_topic,
                "blooms_level": blooms_level,
                "pedagogies_reference": self.pedagogies_reference
            })
            
            raw_content = response.content
            logger.debug(f"Raw LLM pedagogy output for '{current_topic}': {raw_content}")
            
            cleaned_json = clean_json_string(raw_content)
            data = json.loads(cleaned_json)
            
            pedagogies = []
            for item in data.get("pedagogies", []):
                conf = item.get("confidence", 70)
                try:
                    conf = int(conf)
                except (ValueError, TypeError):
                    conf = 70
                    
                time_pct = item.get("time_percentage", 30)
                try:
                    time_pct = int(time_pct)
                except (ValueError, TypeError):
                    time_pct = 30
                    
                pedagogies.append(PedagogyRecommendation(
                    rank=int(item.get("rank", 1)),
                    name=str(item.get("name", "Interactive Lecture")),
                    confidence=conf,
                    justification=str(item.get("justification", item.get("reason", "Highly suitable pedagogy for explaining core topics."))),
                    time_percentage=time_pct,
                    learning_outcome=str(item.get("learning_outcome", "Students will demonstrate conceptual understanding."))
                ))
            
            # Sort recommendations by rank
            pedagogies = sorted(pedagogies, key=lambda x: x.rank)
            
            return TopicRecommendation(
                topic=current_topic,
                pedagogies=pedagogies[:3]  # Ensure only top 3 are returned
            )
            
        except Exception as e:
            logger.error(f"Error recommending pedagogies for topic '{current_topic}': {e}")
            # Fallback values
            return TopicRecommendation(
                topic=current_topic,
                pedagogies=[
                    PedagogyRecommendation(rank=1, name="Interactive Lecture", confidence=85, justification="Explains core theoretical concepts and lays down foundations for subsequent topics.", time_percentage=40, learning_outcome="Explain the conceptual foundation of the topic."),
                    PedagogyRecommendation(rank=2, name="Visualization", confidence=75, justification="Uses graphical trace of execution or animation to map dynamic concepts visually.", time_percentage=30, learning_outcome="Describe the flow of the algorithm or concept visually."),
                    PedagogyRecommendation(rank=3, name="Problem-Based Learning", confidence=70, justification="Solves structured tasks to apply concepts in practice.", time_percentage=30, learning_outcome="Apply concepts to solve basic test problems.")
                ]
            )

    def recommend_all(self, syllabus: ExtractedSyllabus) -> List[TopicRecommendation]:
        """
        Executes recommendations for all topics across all units concurrently using a thread pool.
        """
        results = []
        tasks = []
        
        # Concurrently process topics to optimize performance on local Ollama server
        with ThreadPoolExecutor(max_workers=3) as executor:
            for unit_data in syllabus.units:
                unit_name = unit_data.unit
                topics = unit_data.topics
                for topic in topics:
                    tasks.append(
                        executor.submit(
                            self.recommend_for_topic,
                            syllabus.subject_name,
                            unit_name,
                            topics,
                            topic
                        )
                    )
            
            for task in tasks:
                results.append(task.result())
                
        return results

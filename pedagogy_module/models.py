from pydantic import BaseModel, Field
from typing import List, Optional

class UnitTopics(BaseModel):
    unit: str = Field(description="Name or title of the unit, e.g., 'Unit I: Introduction' or 'Search Techniques'")
    topics: List[str] = Field(description="List of core sub-topics or concepts listed under this unit")

class ExtractedSyllabus(BaseModel):
    subject_name: str = Field(description="Name of the subject, e.g., 'Artificial Intelligence'")
    units: List[UnitTopics] = Field(description="List of units in this syllabus")

class PedagogyRecommendation(BaseModel):
    rank: int = Field(description="The priority rank from 1 to 3 (1 being the absolute best)")
    name: str = Field(description="Name of the pedagogy (e.g., 'Visualization', 'Interactive Lecture')")
    confidence: int = Field(description="Confidence score from 0 to 100 representing suitability")
    justification: str = Field(description="Educational justification explaining why this pedagogy is ideal based on cognitive targets and course context")
    time_percentage: int = Field(description="Recommended percentage of the total topic teaching duration allocated to this pedagogy (e.g. 40)")
    learning_outcome: str = Field(description="The expected learning outcome for the students from this pedagogical activity")

class TopicRecommendation(BaseModel):
    topic: str = Field(description="The name of the topic")
    pedagogies: List[PedagogyRecommendation] = Field(description="List of top 3 recommended pedagogies")

class SyllabusRequest(BaseModel):
    subject: str = Field(description="Name of the subject, e.g., 'Artificial Intelligence'")
    syllabus: str = Field(description="Raw text content of the syllabus")

class SyllabusResponse(BaseModel):
    subject: str = Field(description="Name of the subject")
    topics: List[TopicRecommendation] = Field(description="List of topics with their recommended pedagogies")

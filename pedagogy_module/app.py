import logging
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pedagogy_module.models import SyllabusRequest, SyllabusResponse
from pedagogy_module.parser import extract_text_from_pdf
from pedagogy_module.topic_extractor import TopicExtractor
from pedagogy_module.pedagogy_engine import PedagogyEngine
from pedagogy_module.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pedagogy Recommendation Microservice",
    description="Extracts topics from a syllabus and recommends the top 3 pedagogy techniques.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines eagerly
topic_extractor = TopicExtractor()
pedagogy_engine = PedagogyEngine()

@app.get("/health")
def health_check():
    """
    Service health check and Ollama connectivity status.
    """
    import httpx
    ollama_status = "unknown"
    try:
        response = httpx.get(settings.OLLAMA_HOST, timeout=2.0)
        if response.status_code == 200:
            ollama_status = "connected"
        else:
            ollama_status = f"unhealthy (status {response.status_code})"
    except Exception as e:
        ollama_status = f"disconnected ({str(e)})"
        
    return {
        "status": "healthy" if ollama_status == "connected" else "degraded",
        "ollama_connection": ollama_status,
        "model": settings.LLM_MODEL
    }

@app.post("/api/pedagogy/generate", response_model=SyllabusResponse)
def generate_pedagogy(request: SyllabusRequest):
    """
    Extract topics from raw text syllabus and recommend top 3 pedagogies for each topic.
    """
    if not request.syllabus.strip():
        raise HTTPException(status_code=400, detail="Syllabus text content cannot be empty.")
        
    try:
        logger.info(f"Received JSON request for subject: '{request.subject}'")
        
        # 1. Extract structure
        extracted_syllabus = topic_extractor.extract(request.subject, request.syllabus)
        
        # 2. Recommend pedagogies
        recommendations = pedagogy_engine.recommend_all(extracted_syllabus)
        
        return SyllabusResponse(
            subject=extracted_syllabus.subject_name,
            topics=recommendations
        )
    except ValueError as val_err:
        logger.error(f"Value error in generation: {val_err}")
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as e:
        logger.error(f"Unexpected error in generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal service error: {str(e)}")

@app.post("/api/pedagogy/generate/file", response_model=SyllabusResponse)
async def generate_pedagogy_file(
    subject: str = Form(..., description="Subject name"),
    file: UploadFile = File(..., description="Syllabus PDF file")
):
    """
    Upload a syllabus PDF, extract text and topics, and recommend top 3 pedagogies.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF syllabus documents are supported.")
        
    try:
        logger.info(f"Received file upload '{file.filename}' for subject: '{subject}'")
        
        # Read file bytes and parse PDF text
        file_bytes = await file.read()
        syllabus_text = extract_text_from_pdf(file_bytes)
        
        if not syllabus_text.strip():
            raise ValueError("No text could be extracted from the provided PDF file.")
            
        # Extract structure and topics
        extracted_syllabus = topic_extractor.extract(subject, syllabus_text)
        
        # Recommend pedagogies
        recommendations = pedagogy_engine.recommend_all(extracted_syllabus)
        
        return SyllabusResponse(
            subject=extracted_syllabus.subject_name,
            topics=recommendations
        )
    except ValueError as val_err:
        logger.error(f"Value error in PDF generation: {val_err}")
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as e:
        logger.error(f"Unexpected error in PDF generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal service error: {str(e)}")

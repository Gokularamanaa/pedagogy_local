import json
import sys
from fastapi.testclient import TestClient

# Add workspace directory to path to ensure imports work correctly
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pedagogy_module.app import app
from pedagogy_module.config import settings

client = TestClient(app)

def test_health():
    """
    Test the microservice health status and Ollama connectivity.
    """
    print("\n[TEST] Querying health check endpoint...")
    response = client.get("/health")
    print(f"Response status: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama_connection" in data
    print("Health check validation: PASSED")

def test_pedagogy_generation():
    """
    Test topic extraction and pedagogy recommendations on a mock syllabus block.
    """
    print("\n[TEST] Querying /api/pedagogy/generate endpoint with sample syllabus...")
    mock_request = {
        "subject": "Artificial Intelligence",
        "syllabus": (
            "Unit II: Search Techniques\n"
            "Topics:\n"
            "1. State Space Search\n"
            "2. Breadth First Search\n"
            "3. Depth First Search\n"
            "4. Heuristic Search\n"
        )
    }
    
    # Invoke FastAPI endpoint via TestClient
    response = client.post("/api/pedagogy/generate", json=mock_request)
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error payload: {response.text}")
        raise ValueError(f"Generation endpoint failed with status {response.status_code}")
        
    res_data = response.json()
    print("\nGeneration output payload:")
    print(json.dumps(res_data, indent=2))
    
    # Assertions
    assert "subject" in res_data
    assert res_data["subject"] == "Artificial Intelligence"
    assert "topics" in res_data
    assert isinstance(res_data["topics"], list)
    assert len(res_data["topics"]) > 0
    
    for topic_rec in res_data["topics"]:
        assert "topic" in topic_rec
        assert "pedagogies" in topic_rec
        assert isinstance(topic_rec["pedagogies"], list)
        assert len(topic_rec["pedagogies"]) == 3
        
        # Verify pedagogy sorting and attributes
        ranks = []
        for ped in topic_rec["pedagogies"]:
            assert "rank" in ped
            assert "name" in ped
            assert "confidence" in ped
            assert "justification" in ped
            assert "time_percentage" in ped
            assert "learning_outcome" in ped
            ranks.append(ped["rank"])
        assert ranks == [1, 2, 3], f"Ranks should be [1, 2, 3] but got {ranks}"
        
    print("\nPedagogy recommendation structure validation: PASSED")

if __name__ == "__main__":
    print("====================================================")
    print("Starting Standalone Pedagogy Microservice Verification")
    print("====================================================")
    try:
        test_health()
        test_pedagogy_generation()
        print("\n====================================================")
        print("VERIFICATION COMPLETED: ALL TESTS PASSED SUCCESSFULLY")
        print("====================================================")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {str(e)}")
        sys.exit(1)

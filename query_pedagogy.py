import os
import sys

# Add workspace directory to python path to resolve imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pedagogy_module.pedagogy_engine import PedagogyEngine

def main():
    print("==================================================")
    print("🎓 Interactive Pedagogy Recommendation CLI")
    print("==================================================")
    
    print("Loading pedagogy engine and knowledge base...")
    try:
        engine = PedagogyEngine()
        print("Initialization complete! Ready.\n")
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return
        
    subject = input("Subject Name [Artificial Intelligence]: ").strip()
    if not subject:
        subject = "Artificial Intelligence"
        
    unit = input("Unit Name/Title [Unit II: Search Techniques]: ").strip()
    if not unit:
        unit = "Unit II: Search Techniques"
        
    other_topics_raw = input("Other topics in this Unit for context (comma separated):\n> ").strip()
    if other_topics_raw:
        unit_topics = [t.strip() for t in other_topics_raw.split(",") if t.strip()]
    else:
        unit_topics = ["State Space Search", "Depth First Search", "Breadth First Search", "Heuristic Search"]
        print(f"Using default unit context: {', '.join(unit_topics)}")
        
    topic = input("\nTarget Topic to get pedagogies for:\n> ").strip()
    if not topic:
        print("Error: Target topic cannot be empty.")
        return
        
    # Ensure target topic is included in the context list
    if topic not in unit_topics:
        unit_topics.append(topic)
        
    print(f"\nRunning analysis with qwen2.5:3b for topic '{topic}'...")
    try:
        rec = engine.recommend_for_topic(subject, unit, unit_topics, topic)
        
        print("\n==================================================")
        print(f"Recommendations for: {rec.topic}")
        print("==================================================")
        for p in rec.pedagogies:
            print(f"\nRank {p.rank}: {p.name}")
            print(f"Confidence: {p.confidence}%")
            print(f"Time Allocation: {p.time_percentage}% of topic time")
            print(f"Educational Justification:\n  {p.justification}")
            print(f"Expected Student Outcome:\n  {p.learning_outcome}")
        print("==================================================")
    except Exception as e:
        print(f"Error during recommendation query: {e}")

if __name__ == "__main__":
    main()

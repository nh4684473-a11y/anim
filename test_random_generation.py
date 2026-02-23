
import sys
import os
import json

# Add the backend directory to sys.path so 'app' module can be found
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.main import generate_chords, ChordRequest

def test_random_generation():
    print("Testing Random Generation (Surprise Me Mode)...")
    
    # Create a request with "Random" parameters
    request = ChordRequest(
        key="Random",
        scale="Random",
        mood="Random",
        length=4,
        complexity=0.5,
        melody=True,
        tempo=140
    )
    
    try:
        # Call the endpoint function directly
        result = generate_chords(request)
        
        # Verify we got something back
        print(f"Result Source: {result.get('source', 'Unknown')}")
        if 'filename' in result:
            print(f"Filename: {result['filename']}")
        
        assert "chords" in result, "Missing chords"
        assert len(result["chords"]) > 0, "No chords returned"
        
        print("✅ Random generation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_random_generation()

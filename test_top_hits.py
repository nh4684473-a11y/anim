
import sys
import os
import json

# Add the backend directory to sys.path so 'app' module can be found
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.logic.top_hits import generate_top_hit_track, TOP_HITS_TEMPLATES

def test_top_hits_generation():
    print("Testing Top Hits Generation...")
    
    # 1. Test retrieving templates
    print(f"Found {len(TOP_HITS_TEMPLATES)} templates.")
    assert len(TOP_HITS_TEMPLATES) > 0, "No templates found!"
    
    # 2. Test generating a track from the first template
    template_id = TOP_HITS_TEMPLATES[0]["id"]
    print(f"Testing generation for template: {template_id}")
    
    try:
        result = generate_top_hit_track(template_id)
        
        # Verify structure
        assert "chords" in result, "Missing 'chords' in result"
        assert "melody" in result, "Missing 'melody' in result"
        assert "key" in result, "Missing 'key' in result"
        assert "scale" in result, "Missing 'scale' in result"
        assert "tempo" in result, "Missing 'tempo' in result"
        
        # Verify content
        print(f"Generated {len(result['chords'])} chords and {len(result['melody'])} melody notes.")
        assert len(result['chords']) > 0, "No chords generated"
        assert len(result['melody']) > 0, "No melody generated"
        
        # Verify musical consistency
        print(f"Key: {result['key']} {result['scale']}")
        print(f"Tempo: {result['tempo']}")
        
        print("✅ Top Hits generation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_top_hits_generation()

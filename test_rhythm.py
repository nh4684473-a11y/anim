
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.logic.patterns import apply_rhythm

def test_rhythm():
    notes = [42, 54, 61, 69]
    rhythm_type = "walker_piano"
    length = 4.0
    
    print(f"Testing apply_rhythm with notes={notes}, type={rhythm_type}, length={length}")
    
    events = apply_rhythm(notes, rhythm_type=rhythm_type, length=length)
    
    print(f"Generated {len(events)} events")
    for e in events:
        print(e)

if __name__ == "__main__":
    test_rhythm()

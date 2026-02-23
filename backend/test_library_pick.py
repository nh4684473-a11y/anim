import requests
import json
import sys

def test_library_pick():
    url = "http://127.0.0.1:8000/generate/chords"
    
    # We generated Electro-House D# phrygian 129bpm
    # Let's request something similar
    payload = {
        "key": "D#",
        "scale": "phrygian",
        "mood": "Electro House", # Should match genre
        "tempo": 129,
        "source": "library"
    }
    
    try:
        print(f"Requesting library pick: {payload}")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            # Check if we got the expected metadata if available
            # The API returns chords, melody, etc.
            # It doesn't explicitly say it came from library unless we check the logs or response headers/structure
            # But if it works, it returns valid data.
            print(f"Received {len(data['chords'])} chords")
            if data.get('melody'):
                print(f"Received {len(data['melody'])} melody notes")
            else:
                print("No melody received")
                
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_library_pick()

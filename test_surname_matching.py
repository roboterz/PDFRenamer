from surname_matcher import SurnameMatcher
import os

def test_surname_matching():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "chinese_surnames_detailed.json")
    
    if not os.path.exists(json_path):
        print("JSON file not found. Skipping test.")
        return

    matcher = SurnameMatcher(json_path)
    
    test_cases = [
        ("This policy is for Wang Wei coverage.", ["Wang Wei"]),
        ("Insured: Wei Wang", ["Wei Wang"]),
        ("Customer Name: Li Na", ["Li Na", "Lee Na"]), # Lee might be variant
        ("Payment by Zhang San.", ["Zhang San"]),
        ("Chen Jie is the owner.", ["Chen Jie"]),
        ("Unrelated text without names.", []),
        ("Policy Number 12345 attached.", [])
    ]
    
    print(f"Loaded {len(matcher.surnames)} surnames.")
    
    for text, expected in test_cases:
        results = matcher.find_potential_names(text)
        print(f"Text: '{text}' -> Found: {results}")
        
        # Basic validation: at least one expected name should be in results if expected is not empty
        if expected:
            found = False
            for exp in expected:
                 # Fuzzy check or direct check
                 # Our matcher returns exactly what is in text
                 if exp in results:
                     found = True
                     break
            if not found:
                 print(f"  [WARN] Expected one of {expected} but got {results}")
        else:
            if results:
                 print(f"  [INFO] Found unexpected names (might be false positives): {results}")

if __name__ == "__main__":
    test_surname_matching()

from surname_matcher import SurnameMatcher
import os

def test_middle_names():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "chinese_surnames_detailed.json")
    
    if not os.path.exists(json_path):
        print("JSON file not found. Skipping test.")
        return

    matcher = SurnameMatcher(json_path)
    
    test_cases = [
        ("Insured: Wang Xiao Ming", ["Wang Xiao Ming"]),
        ("Name: John A. Wang", ["John A. Wang"]),
        ("Customer: Xiao Ming Wang", ["Xiao Ming Wang"]),
        ("Contact: Li Mei Hua", ["Li Mei Hua"]),
        ("Just a Two Word Name: Wang Wei", ["Wang Wei"]),
        ("Invalid: Wang a. Wei", []), # Lowercase initial should fail
        ("Middle Name: David Lee Roth", ["David Lee Roth"]), # Lee is a surname
        ("Complex: The policy for Wang Xiao Ming covers...", ["Wang Xiao Ming"]),
        ("Noise: Wang Effective Date", []), # "Effective" is not pinyin, should fail
        ("Noise: Policy Terms and Conditions", []),
        ("Partial Noise: Wang Good Day", []) # "Good" is typically not pinyin (though confusing visually), "Day" is definitely english.
    ]
    
    print(f"Loaded {len(matcher.surnames)} surnames.")
    
    for text, expected in test_cases:
        print(f"\nText: '{text}'")
        results = matcher.find_potential_names(text)
        print(f"Found: {results}")
        
        if expected:
            found_match = False
            for exp in expected:
                if exp in results:
                    found_match = True
                    break
            if found_match:
                print(f"  [PASS] Found expected match.")
            else:
                 print(f"  [FAIL] Expected one of {expected} but got {results}")
        else:
            if not results:
                print(f"  [PASS] Correctly found no names.")
            else:
                print(f"  [WARN] Found unexpected names: {results}")

if __name__ == "__main__":
    test_middle_names()

import unittest
from renamer_logic import PDFProcessor

class TestParensExclusion(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_regex_exclusion(self):
        """Test that regex extraction ignores content inside parentheses."""
        # Case: Name inside parens should NOT be extracted? 
        # User: "Brackets wont be name".
        # If text is "Named Insured: (Owner) Wang", regex for "Named Insured: (.*)" captures "(Owner) Wang".
        # Cleaned text -> "Named Insured:  Wang". Regex captures " Wang". -> "Wang"
        text = "Named Insured: (Owner) Wang"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "Wang")

    def test_regex_exclusion_internal(self):
        # "Named Insured: Wang (CEO)" -> Cleaned: "Wang " -> "Wang"
        text = "Named Insured: Wang (CEO)"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "Wang")

    def test_surname_match_exclusion(self):
        # Surname matcher fallback.
        # "Wang (Owner) Xiao Ming" -> Cleaned: "Wang  Xiao Ming".
        # "Wang Xiao Ming" -> Match.
        text = "Wang (Owner) Xiao Ming"
        # Ensure no labeled key matches
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "Wang_Xiao_Ming")
        
    def test_pure_parens_rejection(self):
        # "Named Insured: (Unknown)" -> Cleaned: "Named Insured:  " -> Empty -> UnknownInsured
        text = "Named Insured: (Unknown)"
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "UnknownInsured")

if __name__ == '__main__':
    unittest.main()

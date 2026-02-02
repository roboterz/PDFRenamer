import unittest
from renamer_logic import PDFProcessor

class TestMissedNames(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_typo_in_label(self):
        """Test finding name when label has OCR typos."""
        # "Namcd Insured" instead of "Named Insured"
        words = [
            {"text": "Namcd", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 55, "x1": 100, "top": 100, "bottom": 112, "size": 12},
            {"text": "John", "x0": 110, "x1": 140, "top": 100, "bottom": 112, "size": 12},
            {"text": "Doe", "x0": 145, "x1": 170, "top": 100, "bottom": 112, "size": 12},
        ]
        data = {
            "full_text": "Namcd Insured: John Doe",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        
        # Currently expected to FAIL (return UnknownInsured)
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Typo Case: {extracted}")
        # We want this to eventually pass:
        # self.assertEqual(extracted, "John_Doe")

    def test_new_keyword_policyholder(self):
        """Test finding name with 'Policyholder' label."""
        words = [
            {"text": "Policyholder:", "x0": 10, "x1": 80, "top": 100, "bottom": 112, "size": 12},
            {"text": "Jane", "x0": 90, "x1": 120, "top": 100, "bottom": 112, "size": 12},
            {"text": "Doe", "x0": 125, "x1": 150, "top": 100, "bottom": 112, "size": 12},
        ]
        data = {
            "full_text": "Policyholder: Jane Doe",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Policyholder Case: {extracted}")
        
    def test_first_named_insured(self):
        """Test 'First Named Insured'."""
        words = [
            {"text": "First", "x0": 10, "x1": 40, "top": 100, "bottom": 112, "size": 12},
            {"text": "Named", "x0": 45, "x1": 80, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 85, "x1": 120, "top": 100, "bottom": 112, "size": 12},
            {"text": "Acme", "x0": 130, "x1": 160, "top": 100, "bottom": 112, "size": 12},
            {"text": "Corp", "x0": 165, "x1": 190, "top": 100, "bottom": 112, "size": 12},
        ]
        data = {
            "full_text": "First Named Insured: Acme Corp",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"First Named Case: {extracted}")

if __name__ == '__main__':
    unittest.main()

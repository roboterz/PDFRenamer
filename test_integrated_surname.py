import unittest
from renamer_logic import PDFProcessor

class TestIntegratedSurname(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_surname_fallback(self):
        """Test that surname matching works as a fallback when standard keys fail."""
        # Text with NO colon keys for "Named Insured"
        text = """
        INSURANCE POLICY
        Policy No: 123456
        Wang Xiao Ming
        Effective Date: 01/01/2026
        """
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        
        # Analyze
        _, metadata = self.processor.analyze_content(data)
        
        # Should find "Wang Xiao Ming" via fallback
        self.assertEqual(metadata["insured_name"], "Wang_Xiao_Ming")
        
    def test_surname_fallback_initial(self):
        """Test with middle initial."""
        text = """
        Policy Document
        John A. Wang
        Date: 10/10/2025
        """
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "John_A._Wang")

if __name__ == '__main__':
    unittest.main()

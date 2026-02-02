import unittest
from renamer_logic import PDFProcessor, DocumentType
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TestSpatialExtraction(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_spatial_right(self):
        """Test finding value to the right of a label."""
        words = [
            {"text": "Effective", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Date:", "x0": 55, "x1": 85, "top": 100, "bottom": 112, "size": 12},
            {"text": "01/01/2024", "x0": 95, "x1": 150, "top": 100, "bottom": 112, "size": 12},
        ]
        
        data = {
            "full_text": "Effective Date: 01/01/2024",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "Effective Date: 01/01/2024"}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "01-01-2024")

    def test_spatial_below(self):
        """Test finding value below a label."""
        words = [
            {"text": "Named", "x0": 10, "x1": 40, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured", "x0": 45, "x1": 90, "top": 100, "bottom": 112, "size": 12},
            {"text": "John", "x0": 10, "x1": 40, "top": 120, "bottom": 132, "size": 12},
            {"text": "Wick", "x0": 45, "x1": 80, "top": 120, "bottom": 132, "size": 12},
        ]
        
        data = {
            "full_text": "Named Insured\nJohn Wick",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "Named Insured\nJohn Wick"}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["insured_name"], "John_Wick")

    def test_multipage_extraction(self):
        """Test finding data on the second page."""
        # Page 1: Junk
        words_p1 = [{"text": "Nothing", "x0":10, "x1":50, "top":10, "bottom":20, "size":10}]
        
        # Page 2: The info
        words_p2 = [
            {"text": "Effective", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Date:", "x0": 55, "x1": 85, "top": 100, "bottom": 112, "size": 12},
            {"text": "12/25/2025", "x0": 95, "x1": 150, "top": 100, "bottom": 112, "size": 12},
        ]
        
        data = {
            "full_text": "Nothing\nEffective Date: 12/25/2025",
            "pages": [
                {"words": words_p1, "width": 600, "height": 800, "text": "Nothing"},
                {"words": words_p2, "width": 600, "height": 800, "text": "Effective Date: 12/25/2025"}
            ]
        }
        
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "12-25-2025")


    def test_text_month_date(self):
        """Test parsing textual month date."""
        text = "Effective Date: Jan 25, 2026"
        data = {
            "full_text": text,
            "pages": [{"words": [], "width": 600, "height": 800, "text": text}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["date"], "Jan-25-2026")

    def test_company_underwritten_by(self):
        """Test fallback company extraction."""
        text = "Some Policy\nUnderwritten by: The Super Insurance Co."
        data = {
            "full_text": text,
            "pages": [{"words": [], "width": 600, "height": 800, "text": text}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        self.assertEqual(metadata["company_name"], "The_Super_Insurance_Co")

if __name__ == '__main__':
    unittest.main()

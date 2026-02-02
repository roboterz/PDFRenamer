import unittest
from renamer_logic import PDFProcessor

class TestMultilineSpatial(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_multiline_right(self):
        """Test finding multi-line value to the right of a label."""
        # Key: "Named Insured:"
        # Value Line 1: "The Big"
        # Value Line 2: "Company Inc" -> aligned x with "The Big"
        
        words = [
            {"text": "Named", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 55, "x1": 100, "top": 100, "bottom": 112, "size": 12},
            
            # Line 1
            {"text": "The", "x0": 110, "x1": 140, "top": 100, "bottom": 112, "size": 12},
            {"text": "Big", "x0": 145, "x1": 170, "top": 100, "bottom": 112, "size": 12},
            
            # Line 2 (Strictly below, gap < 20)
            {"text": "Company", "x0": 110, "x1": 160, "top": 115, "bottom": 127, "size": 12},
            {"text": "Inc", "x0": 165, "x1": 190, "top": 115, "bottom": 127, "size": 12},
            
            # Junk below that (should not be picked)
            {"text": "Address:", "x0": 10, "x1": 60, "top": 140, "bottom": 152, "size": 12},
        ]
        
        data = {
            "full_text": "Named Insured: The Big\nCompany Inc\nAddress:",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}] # Text irrelevant for spatial
        }
        
        # We test _find_text_spatially directly
        result = self.processor._find_text_spatially(data, ["named insured:"], 'right', x_tolerance=200)
        
        print(f"Found: {result}")
        self.assertEqual(result, "The Big Company Inc")

if __name__ == '__main__':
    unittest.main()

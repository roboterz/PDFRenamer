import unittest
from renamer_logic import PDFProcessor

class TestFallbackName(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_large_header_name(self):
        """Test finding name based on big font at top left (common invoice style)."""
        words = [
            # Company Name (Usually top, maybe logo) - ignored if we know it? or maybe we assume company is filtered
            {"text": "State", "x0": 10, "x1": 50, "top": 10, "bottom": 20, "size": 10},
            {"text": "Farm", "x0": 55, "x1": 90, "top": 10, "bottom": 20, "size": 10},
            
            # The Name - Large Font, Top Left-ish
            {"text": "ALICE", "x0": 50, "x1": 100, "top": 80, "bottom": 100, "size": 16},
            {"text": "WONDERLAND", "x0": 105, "x1": 200, "top": 80, "bottom": 100, "size": 16},
            
            # Some address below
            {"text": "123", "x0": 50, "x1": 70, "top": 105, "bottom": 115, "size": 10},
            {"text": "Rabbit", "x0": 75, "x1": 100, "top": 105, "bottom": 115, "size": 10},
            {"text": "Hole", "x0": 105, "x1": 130, "top": 105, "bottom": 115, "size": 10},
        ]
        data = {
            "full_text": "State Farm\nALICE WONDERLAND\n123 Rabbit Hole",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Fallback Header: {extracted}")
        # Expect: UnknownInsured (Guessing removed)
        self.assertEqual(extracted, "UnknownInsured")

    def test_address_block_prediction(self):
        """Test finding name because it sits above an address block."""
        words = [
            # Standard Font
            {"text": "Bob", "x0": 50, "x1": 80, "top": 150, "bottom": 162, "size": 12},
            {"text": "Builder", "x0": 85, "x1": 130, "top": 150, "bottom": 162, "size": 12},
            
            # Address line
            {"text": "456", "x0": 50, "x1": 70, "top": 165, "bottom": 177, "size": 12},
            {"text": "Construction", "x0": 75, "x1": 150, "top": 165, "bottom": 177, "size": 12},
            {"text": "Ln", "x0": 155, "x1": 170, "top": 165, "bottom": 177, "size": 12},
            
            # City State Zip (Strong signal)
            {"text": "New", "x0": 50, "x1": 70, "top": 180, "bottom": 192, "size": 12},
            {"text": "York,", "x0": 75, "x1": 100, "top": 180, "bottom": 192, "size": 12},
            {"text": "NY", "x0": 105, "x1": 120, "top": 180, "bottom": 192, "size": 12},
            {"text": "10001", "x0": 125, "x1": 160, "top": 180, "bottom": 192, "size": 12},
        ]
        data = {
            "full_text": "Bob Builder\n456 Construction Ln\nNew York, NY 10001",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Fallback Address: {extracted}")

if __name__ == '__main__':
    unittest.main()

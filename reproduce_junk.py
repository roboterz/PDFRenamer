import unittest
from renamer_logic import PDFProcessor

class TestJunkName(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_junk_in_spatial_name(self):
        """Test that garbage on the second line is NOT merged into the name."""
        # Key: "Named Insured:"
        # Value Line 1: "John Doe"
        # Value Line 2: "_:_0635201924_:_$1,491.00" -> This should be rejected!
        
        words = [
            {"text": "Named", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 55, "x1": 100, "top": 100, "bottom": 112, "size": 12},
            
            # Line 1 (Valid Name)
            {"text": "John", "x0": 110, "x1": 140, "top": 100, "bottom": 112, "size": 12},
            {"text": "Doe", "x0": 145, "x1": 170, "top": 100, "bottom": 112, "size": 12},
            
            # Line 2 (Junk - strictly below, aligned)
            {"text": "_:_", "x0": 110, "x1": 130, "top": 115, "bottom": 127, "size": 12},
            {"text": "0635201924", "x0": 135, "x1": 180, "top": 115, "bottom": 127, "size": 12},
            {"text": "_:_", "x0": 185, "x1": 200, "top": 115, "bottom": 127, "size": 12},
            {"text": "$1,491.00", "x0": 205, "x1": 250, "top": 115, "bottom": 127, "size": 12},
        ]
        
        data = {
            "full_text": "Named Insured: John Doe\n_:_0635201924_:_$1,491.00",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        
        # We expect "John Doe" ONLY, or at least the junk cleaned out.
        # Currently the logic might return "John Doe _ _0635201924 _ $1,491.00"
        
        _, metadata = self.processor.analyze_content(data)
        extracted_name = metadata.get("insured_name")
        print(f"Extracted: {extracted_name}")
        
        # Assertions
        self.assertNotIn("$", extracted_name)
        self.assertNotIn("0635", extracted_name)
        self.assertEqual(extracted_name, "John_Doe")

    def test_junk_same_line(self):
        """Test junk on the same line."""
        words = [
            {"text": "Named", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 55, "x1": 100, "top": 100, "bottom": 112, "size": 12},
            {"text": "John", "x0": 110, "x1": 140, "top": 100, "bottom": 112, "size": 12},
            # Junk further right? Or immediate?
            {"text": "_:_0635...$1,491.00", "x0": 150, "x1": 250, "top": 100, "bottom": 112, "size": 12}, 
        ]
        data = {
            "full_text": "Named Insured: John _:_0635...$1,491.00",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"SameLine: {extracted}")
        # We want to ensure we don't get the junk
        self.assertNotIn("$", extracted)

    def test_junk_is_primary_candidate(self):
        """Test if the ONLY thing found is junk (e.g. empty name)."""
        words = [
            {"text": "Named", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 55, "x1": 100, "top": 100, "bottom": 112, "size": 12},
            # No name here.
            # Junk below.
            {"text": "_:_0635...$1,491.00", "x0": 10, "x1": 100, "top": 120, "bottom": 130, "size": 12}
        ]
        data = {
            "full_text": "Named Insured:\n_:_0635...$1,491.00",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"PrimaryCandidate: {extracted}")
        # Should be UnknownInsured (default) or at least filtered
        self.assertEqual(extracted, "UnknownInsured")
        
    def test_sanitize_chars(self):
        """Test that invalid filename characters are removed via spatial path."""
        # Spatial path grabs whatever text is there, so we can inject invalid chars
        words = [
            {"text": "Named", "x0": 10, "x1": 50, "top": 100, "bottom": 112, "size": 12},
            {"text": "Insured:", "x0": 55, "x1": 100, "top": 100, "bottom": 112, "size": 12},
            {"text": "John|Doe", "x0": 110, "x1": 160, "top": 100, "bottom": 112, "size": 12},
        ]
        data = {
            "full_text": "Random content without the keywords in text form",
            "pages": [{"words": words, "width": 600, "height": 800, "text": "..."}]
        }
        _, metadata = self.processor.analyze_content(data)
        extracted = metadata.get("insured_name")
        print(f"Sanitized: {extracted}")
        # | should be removed. Result: "JohnDoe"
        self.assertEqual(extracted, "JohnDoe")

if __name__ == '__main__':
    unittest.main()

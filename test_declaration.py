import unittest
from renamer_logic import PDFProcessor, DocumentType

class TestDeclaration(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()

    def test_declaration_keyword(self):
        """Test that 'declaration' keyword implies POLICY type."""
        text = "This is a Commercial Insurance Declaration."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        doc_type, _ = self.processor.analyze_content(data)
        self.assertEqual(doc_type, DocumentType.POLICY)

    def test_declarations_plural(self):
        """Test that 'declarations' (plural) keyword implies POLICY type."""
        text = "These are Policy Declarations."
        data = {"full_text": text, "pages": [{"words": [], "width": 100, "height": 100, "text": text}]}
        doc_type, _ = self.processor.analyze_content(data)
        self.assertEqual(doc_type, DocumentType.POLICY)

    def test_naming_convention(self):
        """Test that POLICY type generates filename with DEC."""
        metadata = {
            "insured_name": "John_Doe",
            "company_name": "Geico",
            "date": "01-01-2025"
        }
        # DocumentType.POLICY should result in ...DEC_EFF...
        name = self.processor.generate_new_name("test.pdf", DocumentType.POLICY, metadata)
        self.assertIn("DEC_EFF", name)

if __name__ == '__main__':
    unittest.main()

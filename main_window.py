import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from renamer_logic import PDFProcessor, DocumentType

class DropZone(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("\n\nDrag and Drop PDF Files Here\n\n")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                font-size: 20px;
                color: #555;
            }
            QLabel:hover {
                border-color: #5c6bc0;
                background-color: #f0f4ff;
            }
        """)
        self.setAcceptDrops(True)
        self.processor = PDFProcessor()
        self.main_window = parent

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.main_window.process_files(files)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Smart Renamer")
        self.resize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.drop_zone = DropZone(self)
        layout.addWidget(self.drop_zone, stretch=2)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Log output will appear here...")
        layout.addWidget(self.log_area, stretch=1)

        self.processor = PDFProcessor()

    def log(self, message):
        self.log_area.append(message)

    def process_files(self, files):
        for filepath in files:
            if not filepath.lower().endswith(".pdf"):
                self.log(f"Skipping non-PDF file: {filepath}")
                continue
            
            self.log(f"Processing: {filepath}")
            data = self.processor.extract_data(filepath)
            
            if not data.get("full_text"):
                self.log(f"Warning: No text extracted from {os.path.basename(filepath)}. Is it scanned?")
                continue

            doc_type, metadata = self.processor.analyze_content(data, filepath)
            self.log(f"  Detected Type: {doc_type.name}")
            self.log(f"  Metadata: {metadata}")

            new_name = self.processor.generate_new_name(filepath, doc_type, metadata)
            if new_name != os.path.basename(filepath):
                new_path = self.processor.rename_file(filepath, new_name)
                if "Error" in str(new_path): # Basic error checking
                    self.log(f"  Error renaming: {new_path}")
                else:
                    self.log(f"  Renamed to: {os.path.basename(new_path)}")
                    self.log(f"  Full path: {new_path}")
            else:
                self.log("  Filename structure already appears correct (or unknown type).")
            self.log("-" * 20)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

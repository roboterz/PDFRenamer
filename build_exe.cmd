@echo off
echo Cleaning previous builds...
rmdir /s /q build
rmdir /s /q dist
del *.spec

echo Building EXE...
pyinstaller --noconsole --onefile ^
    --name "PDFRenamer" ^
    --add-data "chinese_surnames_detailed.json;." ^
    --hidden-import="pdfplumber" ^
    --hidden-import="thefuzz" ^
    --hidden-import="Levenshtein" ^
    --hidden-import="pytesseract" ^
    --hidden-import="PIL" ^
    main_window.py

echo Build complete. Executable should be in dist\PDFRenamer.exe
pause

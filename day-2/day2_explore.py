import pdfplumber

PDF_PATH = r"D:\PROJECT\1\AI AUTOMATION\day-2\tutorial_groups.pdf"  # change to your actual pdf name

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    for i, page in enumerate(pdf.pages):
        print(f"\n--- Page {i+1} ---")
        text = page.extract_text()
        print(text)
        
        tables = page.extract_tables()
        if tables:
            print(f"\nFound {len(tables)} table(s) on page {i+1}")
            for t in tables:
                print(t)
                
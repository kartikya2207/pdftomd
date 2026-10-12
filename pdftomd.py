import fitz  # PyMuPDF

def clean_slide_deck(pdf_path, output_txt):
    doc = fitz.open(pdf_path)
    clean_content = []

    for page_num, page in enumerate(doc):
        # Extract text only
        text = page.get_text("text")
        
        # Simple cleaning: Remove common slide junk (like page numbers or dates)
        lines = text.split('\n')
        filtered_lines = [line for line in lines if len(line.strip()) > 2] 
        
        clean_content.append(f"--- Slide {page_num + 1} ---\n")
        clean_content.append("\n".join(filtered_lines))
        clean_content.append("\n\n")

    with open(output_txt, "w", encoding="utf-8") as f:
        f.writelines(clean_content)

# Run the function
clean_slide_deck("lecture_slides.pdf", "slides_as_text.txt")
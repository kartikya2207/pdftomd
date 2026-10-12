import argparse
import os

import easyocr
from pdf2image import convert_from_path


def pdf_to_markdown(pdf_path, output_file):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = easyocr.Reader(["en"])

    print(f"Starting conversion for: {pdf_path}")

    # Convert PDF pages to images using 300 DPI for better OCR accuracy.
    pages = convert_from_path(pdf_path, 300)

    full_text = []

    for i, page in enumerate(pages):
        print(f"Processing Page {i + 1}/{len(pages)}...")

        temp_image = f"temp_page_{i}.jpg"
        page.save(temp_image, "JPEG")

        try:
            result = reader.readtext(temp_image, detail=0)
        finally:
            if os.path.exists(temp_image):
                os.remove(temp_image)

        full_text.append(f"## Page {i + 1}\n\n")
        full_text.append(" ".join(result))
        full_text.append("\n\n---\n\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(full_text)

    print(f"Done! Created: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a PDF to markdown using OCR.")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument(
        "-o",
        "--output",
        default="Final_Notes.md",
        help="Path to the output markdown file",
    )
    args = parser.parse_args()

    pdf_to_markdown(args.pdf_path, args.output)
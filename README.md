# pdftomd

Two small Python scripts I wrote to turn PDF lecture material (typed slides and scanned handwritten notes) into plain text / Markdown that I can search, skim and paste into other tools while studying.

## What it is

Before exams I usually end up with a pile of PDFs: the instructor's slide decks, plus scanned handwritten notes borrowed from friends. None of these are easy to search or quote. This repo holds my two attempts at fixing that:

- **`pdftomd.py`** works on PDFs that already contain a text layer (e.g. exported slide decks). It uses PyMuPDF (`fitz`) to pull the text out page by page, drops very short lines (page numbers, stray characters), and writes everything to a `.txt` file with a `--- Slide N ---` header per page.
- **`htomd.py`** works on scanned / handwritten PDFs that have *no* text layer. It renders every page to an image with `pdf2image` at 300 DPI, runs EasyOCR (English) on each page, and writes a Markdown file with a `## Page N` heading per page and `---` separators between pages.

## What I did

- Wrote the PyMuPDF extractor first, since slides with real text are the easy case.
- Found out it was useless for scanned notes: those PDFs are just images, so `page.get_text()` returns an empty string. That's why the OCR version exists.
- Wrote `htomd.py` around EasyOCR + pdf2image, with:
  - a command-line interface (`argparse`) for the input PDF and output path,
  - a check that the input file exists,
  - a temporary JPEG per page that is always deleted afterwards (`try/finally`), so a crash mid-run doesn't leave image files lying around,
  - simple progress printing (`Processing Page i/N...`).
- Set up a virtual environment and a `requirements.txt` for the OCR script.
- Tried using [aider](https://aider.chat) with a local Ollama model (`qwen2.5-coder`) to review `htomd.py`. Honestly it didn't get far: the 14B model wasn't pulled locally, and the 7B one kept asking me to paste the file instead of reading it because I never added the file to its chat context. The fixes in the script ended up being done by hand.

## What I learnt

- **"PDF" says nothing about whether there is text inside.** A PDF can be real text (easy to extract with PyMuPDF) or just a stack of images (needs OCR). Checking `page.get_text()` on the first page is a quick way to tell which case you're in.
- **OCR on handwriting is rough.** `reader.readtext(..., detail=0)` returns text fragments, and I join them with spaces, so the output loses line breaks, equations and diagrams. It's fine for "which page talks about X?" searches, not for a clean copy of the notes.
- **DPI is a trade-off.** 300 DPI gives EasyOCR more to work with, but rendering big scanned PDFs at that resolution is slow and memory-heavy.
- **pdf2image needs Poppler.** It's not a pure-Python dependency, which is easy to miss on Windows.
- **Local LLM tooling needs setup.** Getting aider to actually help means the model must be pulled in Ollama and the files must be added to the chat (`/add htomd.py`); otherwise it can't see your code.

Known rough edges I haven't fixed yet:

- `pdftomd.py` has hard-coded input/output names (`lecture_slides.pdf` → `slides_as_text.txt`) and runs on import; it should get the same `argparse` treatment as `htomd.py`.
- `pymupdf` (needed by `pdftomd.py`) isn't in `requirements.txt` yet, which only covers the OCR script.
- The "cleaning" step in `pdftomd.py` is just "drop lines of 2 characters or fewer".

## Repo structure

```
pdftomd/
├── pdftomd.py         # text-layer PDFs -> .txt using PyMuPDF
├── htomd.py           # scanned/handwritten PDFs -> Markdown using pdf2image + EasyOCR
├── requirements.txt   # dependencies for htomd.py
└── .gitignore         # ignores venv, caches, aider files and all PDFs
```

The PDFs I actually ran this on (classmates' handwritten notes and a merged course slide deck) are deliberately **not** in this repo: they aren't mine to publish.

## How to run

Requirements: Python 3.10+ (I used 3.11). For `htomd.py` you also need [Poppler](https://poppler.freedesktop.org/) installed and on your `PATH` (on Windows, download a Poppler build and add its `bin` folder to `PATH`).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install pymupdf        # only needed for pdftomd.py
```

OCR a scanned / handwritten PDF into Markdown:

```bash
python htomd.py path/to/notes.pdf -o notes.md
```

The first run downloads EasyOCR's English model, so it needs internet and takes a bit longer.

Extract text from a PDF that already has a text layer: put the file next to the script as `lecture_slides.pdf` (or edit the last line of `pdftomd.py`), then

```bash
python pdftomd.py
```

which writes `slides_as_text.txt`.

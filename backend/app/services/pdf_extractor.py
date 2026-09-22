import fitz


def extract_text_from_pdf(file_path: str) -> str:
    document = fitz.open(file_path)

    try:
        pages_text = []

        for page in document:
            text = page.get_text("text")
            pages_text.append(text)

        return "\n".join(pages_text).strip()

    finally:
        document.close()
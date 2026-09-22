from pathlib import Path

from fastapi import HTTPException, status

from app.services.docx_extractor import extract_text_from_docx
from app.services.pdf_extractor import extract_text_from_pdf


def extract_resume_text(
    file_path: str,
    content_type: str,
) -> str:

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf" and content_type == "application/pdf":
        text = extract_text_from_pdf(file_path)

    elif (
        extension == ".docx"
        and content_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        text = extract_text_from_docx(file_path)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported resume file type.",
        )

    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No readable text was found in the resume. "
                "The file may contain only images or scanned content."
            ),
        )

    return text
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML


BASE_DIR = Path(__file__).resolve().parents[3]

TEMPLATE_DIR = BASE_DIR / "resume_templates"

GENERATED_RESUMES_DIR = BASE_DIR / "generated_resumes"

GENERATED_RESUMES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


jinja_environment = Environment(
    loader=FileSystemLoader(
        TEMPLATE_DIR
    ),
    autoescape=select_autoescape(
        ["html", "xml"]
    ),
)


def generate_resume_pdf(
    *,
    content: dict,
    output_filename: str,
) -> Path:

    template = jinja_environment.get_template(
        "resume.html"
    )

    html_content = template.render(
        **content
    )

    output_path = (
        GENERATED_RESUMES_DIR
        / output_filename
    )

    HTML(
        string=html_content,
        base_url=str(TEMPLATE_DIR),
    ).write_pdf(
        output_path
    )

    return output_path
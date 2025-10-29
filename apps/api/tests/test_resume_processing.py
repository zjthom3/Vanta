from __future__ import annotations

import io
import zipfile

from sqlalchemy.orm import Session

from apps.api.config import settings
from apps.api.models import Profile, ResumeVersion, User
from apps.api.models.enums import PlanTierEnum, StatusEnum
from apps.api.services import storage
from apps.workers.tasks import resume as resume_tasks


def _build_docx_resume(summary: str, skills_line: str, bullet: str) -> bytes:
    document_xml = f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">
  <w:body>
    <w:p><w:r><w:t>{summary}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{skills_line}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{bullet}</w:t></w:r></w:p>
  </w:body>
</w:document>
""".strip()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>
</Types>
""".strip(),
        )
        archive.writestr(
            "_rels/.rels",
            """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>
</Relationships>
""".strip(),
        )
        archive.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def test_process_resume_populates_sections(monkeypatch, db_session: Session):
    user = User(email="resume-test@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    profile = Profile(user=user)
    resume = ResumeVersion(user=user, base_flag=True, doc_url=None)

    db_session.add_all([user, profile, resume])
    db_session.commit()

    resume_key = f"resumes/{resume.id}/sample.docx"
    resume.doc_url = f"{settings.s3_endpoint}/{settings.s3_bucket}/{resume_key}"
    resume.original_filename = "sample.docx"
    resume.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    db_session.commit()

    docx_bytes = _build_docx_resume(
        "Ada Lovelace",
        "Skills: Python, Machine Learning, Analytics",
        "• Delivered automation playbooks used by 200+ teams.",
    )

    monkeypatch.setattr(storage, "download_bytes", lambda key: docx_bytes)

    resume_tasks.process_resume(str(resume.id))

    db_session.refresh(resume)
    db_session.refresh(profile)

    assert resume.sections_json is not None
    assert resume.sections_json["skills"] == ["Analytics", "Machine Learning", "Python"]
    assert resume.ats_score and resume.ats_score > 50
    assert resume.keywords == ["Analytics", "Machine Learning", "Python"]
    assert profile.skills == ["Analytics", "Machine Learning", "Python"]

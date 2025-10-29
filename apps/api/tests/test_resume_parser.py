from __future__ import annotations

import io
import zipfile

from apps.api.services import resume_parser


def test_parse_resume_text_extracts_summary_skills_and_experience():
    text = """
    Ada Lovelace
    Visionary technologist and product strategist.
    Skills: Python, Distributed Systems, Analytics
    • Designed data platform increasing retention by 20%.
    - Led cross-functional team to ship onboarding flow.
    """

    parsed = resume_parser.parse_resume_text(text)

    assert "Ada Lovelace" in parsed.summary
    assert parsed.skills == ["Analytics", "Distributed Systems", "Python"]
    assert parsed.experience == [
        "Designed data platform increasing retention by 20%.",
        "Led cross-functional team to ship onboarding flow.",
    ]
    score = resume_parser.estimate_ats_score(parsed)
    assert 50 < score <= 100


def _make_docx_bytes(paragraphs: list[str]) -> bytes:
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

        safe_paragraphs = []
        for paragraph in paragraphs:
            safe_paragraphs.append(paragraph.replace("&", "&amp;"))

        document_xml = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>",
            "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">",
            "  <w:body>",
        ]
        for para in safe_paragraphs:
            document_xml.append(f"    <w:p><w:r><w:t>{para}</w:t></w:r></w:p>")
        document_xml.extend(["  </w:body>", "</w:document>"])

        archive.writestr("word/document.xml", "\n".join(document_xml))
    return buffer.getvalue()


def test_parse_resume_bytes_docx_extracts_content():
    docx_bytes = _make_docx_bytes(
        [
            "Grace Hopper",
            "Skills: COBOL, Leadership, Systems",
            "• Led compiler innovations",
        ]
    )

    parsed = resume_parser.parse_resume_bytes(
        docx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="resume.docx",
    )

    assert "Grace Hopper" in parsed.summary
    assert parsed.skills == ["COBOL", "Leadership", "Systems"]
    assert parsed.experience == ["Led compiler innovations"]

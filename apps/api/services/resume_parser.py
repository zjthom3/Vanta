from __future__ import annotations

import re
import io
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from xml.etree import ElementTree as ET

MIN_SKILL_LENGTH = 2


@dataclass
class ParsedResume:
    summary: str
    experience: list[str]
    skills: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "experience": self.experience,
            "skills": self.skills,
        }


def _tokenize_skills(lines: Iterable[str]) -> list[str]:
    skills: set[str] = set()
    for line in lines:
        lower = line.lower()
        if lower.startswith(("skills", "technologies", "toolkit", "strengths")):
            _, _, payload = line.partition(":")
            tokens = re.split(r"[,\u2022•|-]", payload or line)
            for token in tokens:
                cleaned = token.strip()
                if len(cleaned) >= MIN_SKILL_LENGTH:
                    skills.add(cleaned)
    return sorted(skills)


def _collect_experience(lines: Iterable[str]) -> list[str]:
    experience: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("-", "*", "•")):
            experience.append(stripped.lstrip("-*• ").strip())
    return experience


def parse_resume_text(text: str) -> ParsedResume:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    summary = " ".join(lines[:2]) if lines else ""
    skills = _tokenize_skills(lines)
    experience = _collect_experience(lines)
    return ParsedResume(summary=summary, skills=skills, experience=experience)


def estimate_ats_score(parsed: ParsedResume) -> int:
    base_score = 50
    skill_bonus = min(len(parsed.skills) * 5, 30)
    experience_bonus = min(len(parsed.experience) * 3, 20)
    return min(base_score + skill_bonus + experience_bonus, 100)


def _guess_format(content_type: str | None, filename: str | None, data: bytes) -> str:
    lowered_type = (content_type or "").lower()
    lowered_name = (filename or "").lower()

    if "pdf" in lowered_type or lowered_name.endswith(".pdf"):
        return "pdf"
    if (
        "wordprocessingml" in lowered_type
        or lowered_name.endswith(".docx")
        or data.startswith(b"PK\x03\x04")
    ):
        return "docx"
    return "text"


def _extract_docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            with archive.open("word/document.xml") as document:
                xml_bytes = document.read()
    except Exception:
        return ""

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", ns):
        texts = [node.text for node in paragraph.findall(".//w:t", ns) if node.text]
        if texts:
            paragraphs.append(" ".join(texts))
    return "\n".join(paragraphs)


def _extract_pdf_text(data: bytes) -> str:
    # Basic fallback: decode binary content and keep printable characters.
    decoded = data.decode("latin-1", errors="ignore")
    lines = []
    for raw_line in decoded.splitlines():
        stripped = raw_line.strip()
        if stripped:
            # Remove common PDF artifacts.
            cleaned = re.sub(r"[\\r\\n\\t]+", " ", stripped)
            lines.append(cleaned)
    return "\n".join(lines)


def parse_resume_bytes(data: bytes, *, content_type: str | None, filename: str | None) -> ParsedResume:
    format_hint = _guess_format(content_type, filename, data)

    if format_hint == "docx":
        text = _extract_docx_text(data)
    elif format_hint == "pdf":
        text = _extract_pdf_text(data)
    else:
        text = data.decode("utf-8", errors="ignore")

    if not text.strip():
        text = ""

    parsed = parse_resume_text(text)
    return parsed

# ice_devtools/generation/generate_cv.py

from pathlib import Path
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    HRFlowable,
    KeepTogether,
)

# ============================================================================
# STYLES & COLORS (BASE, OVERRIDABLE)
# ============================================================================

PRIMARY = HexColor("#6D597A")
ACCENT = HexColor("#E6CFE3")
TEXT = HexColor("#2C2C2C")
MUTED = HexColor("#6E6E6E")

# ============================================================================
# CV GENERATOR
# ============================================================================

class CVGenerator:
    """
    Generatore PDF di Curriculum Vitae.

    Input:
        data: dict strutturato (profile, experience, education, skills, ecc.)

    Output:
        PDF A4 professionale
    """

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.styles = self._build_styles()

    # ---------------------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------------------

    def build_pdf(self, output_path: str | Path) -> None:
        output_path = Path(output_path)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=60,
            bottomMargin=40,
        )

        story: List[Any] = []

        self._section_header(story)
        self._section_summary(story)
        self._section_experience(story)
        self._section_education(story)
        self._section_skills(story)
        self._section_languages(story)
        self._section_extra(story)

        doc.build(story)

    # ---------------------------------------------------------------------
    # SECTIONS
    # ---------------------------------------------------------------------

    def _section_header(self, story: list) -> None:
        profile = self.data.get("profile", {})

        story.append(Paragraph(profile.get("full_name", ""), self.styles["name"]))
        story.append(Paragraph(profile.get("title", ""), self.styles["title"]))

        meta = " • ".join(
            filter(None, [
                profile.get("location"),
                profile.get("phone"),
                profile.get("email"),
            ])
        )
        if meta:
            story.append(Paragraph(meta, self.styles["meta"]))

        story.append(Spacer(1, 18))

    def _section_summary(self, story: list) -> None:
        summary = self.data.get("summary")
        if not summary:
            return

        self._section_title(story, "Profilo professionale")
        story.append(Paragraph(summary, self.styles["body"]))
        story.append(Spacer(1, 16))

    def _section_experience(self, story: list) -> None:
        experiences = self.data.get("experience", [])
        if not experiences:
            return

        self._section_title(story, "Esperienze lavorative")

        for exp in experiences:
            block = []

            role = exp.get("role", "")
            company = exp.get("company", "")
            period = self._format_period(exp.get("start"), exp.get("end"))

            block.append(Paragraph(role, self.styles["role"]))
            block.append(Paragraph(f"{company} · {period}", self.styles["company"]))

            if exp.get("location"):
                block.append(Paragraph(exp["location"], self.styles["location"]))

            tasks = exp.get("tasks", [])
            if tasks:
                items = [
                    ListItem(Paragraph(self._clean_bullet(t), self.styles["bullet"]))
                    for t in tasks
                ]
                block.append(ListFlowable(items, leftIndent=14))

            story.append(KeepTogether(block))
            story.append(Spacer(1, 12))

    def _section_education(self, story: list) -> None:
        education = self.data.get("education", [])
        if not education:
            return

        self._section_title(story, "Formazione")

        for edu in education:
            title = edu.get("title", "")
            school = edu.get("school", "")
            year = edu.get("year", "")

            story.append(Paragraph(
                f"{title} – {school} ({year})",
                self.styles["edu"]
            ))

            if edu.get("location"):
                story.append(Paragraph(edu["location"], self.styles["location"]))

            story.append(Spacer(1, 6))

    def _section_skills(self, story: list) -> None:
        skills = self.data.get("skills")
        if not skills:
            return

        self._section_title(story, "Competenze")

        if skills.get("core"):
            story.append(Paragraph(
                "<b>Professionali:</b> " + ", ".join(skills["core"]),
                self.styles["body"]
            ))

        if skills.get("soft"):
            story.append(Paragraph(
                "<b>Trasversali:</b> " + ", ".join(skills["soft"]),
                self.styles["body"]
            ))

        story.append(Spacer(1, 12))

    def _section_languages(self, story: list) -> None:
        languages = self.data.get("languages", [])
        if not languages:
            return

        self._section_title(story, "Lingue")

        for lang in languages:
            story.append(Paragraph(
                f'{lang.get("name")}: {lang.get("level")}',
                self.styles["body"]
            ))

        story.append(Spacer(1, 12))

    def _section_extra(self, story: list) -> None:
        extra = self.data.get("extra")
        if not extra:
            return

        self._section_title(story, "Informazioni aggiuntive")

        for key, value in extra.items():
            story.append(Paragraph(
                f"<b>{key.capitalize()}:</b> {value}",
                self.styles["body"]
            ))

    # ---------------------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------------------

    def _section_title(self, story: list, title: str) -> None:
        story.append(Paragraph(title, self.styles["section"]))
        story.append(HRFlowable(width="100%", thickness=0.6, color=ACCENT, spaceAfter=8))

    def _format_period(self, start: Optional[str], end: Optional[str]) -> str:
        if start and end:
            return f"{start} – {end}"
        if start and not end:
            return f"{start} – In corso"
        return ""

    def _clean_bullet(self, text: str) -> str:
        return text.rstrip(".;, ")

    def _build_styles(self) -> dict:
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name="name",
            fontSize=22,
            textColor=PRIMARY,
            spaceAfter=2,
            leading=26,
            fontName="Helvetica-Bold"
        ))

        styles.add(ParagraphStyle(
            name="title",
            fontSize=12,
            textColor=MUTED,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            name="meta",
            fontSize=9,
            textColor=MUTED,
            spaceAfter=12
        ))

        styles.add(ParagraphStyle(
            name="section",
            fontSize=14,
            textColor=PRIMARY,
            spaceBefore=18,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            name="body",
            fontSize=10.5,
            textColor=TEXT,
            leading=14
        ))

        styles.add(ParagraphStyle(
            name="role",
            fontSize=11.5,
            fontName="Helvetica-Bold",
            spaceAfter=2
        ))

        styles.add(ParagraphStyle(
            name="company",
            fontSize=10,
            textColor=MUTED,
            spaceAfter=2
        ))

        styles.add(ParagraphStyle(
            name="location",
            fontSize=9.5,
            textColor=MUTED,
            spaceAfter=4
        ))

        styles.add(ParagraphStyle(
            name="bullet",
            fontSize=10,
            leading=13
        ))

        styles.add(ParagraphStyle(
            name="edu",
            fontSize=11,
            spaceAfter=2
        ))

        return styles

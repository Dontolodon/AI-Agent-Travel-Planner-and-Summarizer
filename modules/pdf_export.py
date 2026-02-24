import os
import re
from typing import List, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image as RLImage,
    KeepTogether,
)
from reportlab.lib.utils import ImageReader


BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /app
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
PDF_DIR = os.path.join(EXPORTS_DIR, "itineraries")


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def _clean_attribution_line(line: str) -> str:
    line = (line or "").strip()
    if not line:
        return ""
    line = line.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    line = _strip_html(line)
    line = re.sub(r"\s+", " ", line)
    return line


def _draw_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def export_itinerary_pdf(
    filename: str,
    title: str,
    itinerary_text: str,
    images: List[Tuple[str, str]],  # (place_name, image_path)
    attributions: List[str],
) -> str:
    os.makedirs(PDF_DIR, exist_ok=True)
    out_path = os.path.join(PDF_DIR, filename)

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="AI Travel Operations Agent",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        spaceAfter=10,
        alignment=TA_LEFT,
    )

    h_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceAfter=4,
    )

    mono_style = ParagraphStyle(
        "Mono",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=9.5,
        leading=12,
        spaceAfter=3,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        spaceAfter=3,
    )

    story = []

    # --- Title ---
    story.append(Paragraph(title, title_style))
    story.append(Paragraph("Generated itinerary + photos (Google Places API).", small_style))
    story.append(Spacer(1, 8))

    # --- Itinerary section ---
    story.append(Paragraph("Itinerary", h_style))

    for raw_line in itinerary_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            story.append(Spacer(1, 4))
            continue

        lower = line.lower().strip()
        if lower.startswith("day "):
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>{line}</b>", body_style))
            continue

        if lower.startswith("places used"):
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>{line}</b>", body_style))
            continue

        if line.strip().startswith("- "):
            story.append(Paragraph(f"&nbsp;&nbsp;• {line.strip()[2:]}", body_style))
        else:
            story.append(Paragraph(line, body_style))

    # --- Photos section ---
    if images:
        story.append(PageBreak())
        story.append(Paragraph("Place Photos", h_style))
        story.append(Paragraph("Photos are selected from Google Places (photo_reference).", small_style))
        story.append(Spacer(1, 8))

        max_img_w = A4[0] - doc.leftMargin - doc.rightMargin
        max_img_h = 85 * mm

        for place_name, img_path in images:
            if not img_path or not os.path.exists(img_path):
                continue

            try:
                ir = ImageReader(img_path)
                iw, ih = ir.getSize()
                scale = min(max_img_w / iw, max_img_h / ih)
                w = iw * scale
                h = ih * scale
            except Exception:
                w = max_img_w
                h = max_img_h

            story.append(
                KeepTogether(
                    [
                        Paragraph(f"<b>{place_name}</b>", body_style),
                        Spacer(1, 4),
                        RLImage(img_path, width=w, height=h),
                        Spacer(1, 10),
                    ]
                )
            )

    # --- Attributions ---
    if attributions:
        story.append(PageBreak())
        story.append(Paragraph("Photo Attributions", h_style))
        story.append(Paragraph("From Google Places API (html cleaned).", small_style))
        story.append(Spacer(1, 8))

        for a in attributions:
            cleaned = _clean_attribution_line(a)
            if cleaned:
                story.append(Paragraph(cleaned, mono_style))

    doc.build(story, onFirstPage=_draw_page_number, onLaterPages=_draw_page_number)
    return out_path

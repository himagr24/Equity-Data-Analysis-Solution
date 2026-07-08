import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=16)
sub_style = ParagraphStyle("SubX", parent=styles["Normal"], textColor=colors.grey, fontSize=9)
note_style = ParagraphStyle("NoteX", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
section_style = ParagraphStyle("SectionX", parent=styles["Heading2"], spaceAfter=8)

os.makedirs("output", exist_ok=True)

top5_naive = pd.read_csv("top5_naive.csv")
top5_clean = pd.read_csv("top5_clean.csv")

doc = SimpleDocTemplate(
    "output/equity_analysis_himanshi_agrawal.pdf",
    pagesize=letter,
    topMargin=0.7 * inch,
    bottomMargin=0.7 * inch,
    leftMargin=0.7 * inch,
    rightMargin=0.7 * inch,
)

story = []

story.append(Paragraph("Equity Data Analysis — Top 5 Performers", title_style))
story.append(Paragraph(
    "Window: 2021-06-01 to 2021-10-13 &nbsp;|&nbsp; Prepared by Himanshi Agrawal",
    sub_style
))
story.append(Spacer(1, 14))


def build_table(df: pd.DataFrame) -> Table:
    data = [["Company", "ISIN", "Performance", "30-Day Avg. Volume (to Y)", "Flag"]]
    for _, r in df.iterrows():
        flag = ""
        if "flag" in df.columns and pd.notna(r.get("flag", "")):
            flag = str(r["flag"])

        data.append([
            r["name"],
            r["isin"],
            f"{r['perf_pct']:.1f}%",
            f"{r['avg_vol_30d']:,.0f}",
            flag,
        ])

    table = Table(
        data,
        colWidths=[1.55 * inch, 1.35 * inch, 1.0 * inch, 1.55 * inch, 1.45 * inch],
        repeatRows=0,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (2, 1), (3, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


story.append(Paragraph("Top 5 Performers (Literal Ranking)", section_style))
story.append(build_table(top5_naive))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "This table is the direct answer to the prompt: the top 5 names ranked by "
    "simple close-to-close return from X to Y.",
    note_style
))
story.append(Spacer(1, 14))

story.append(Paragraph("Top 5 Performers (Review-Adjusted Ranking)", section_style))
story.append(build_table(top5_clean))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "This second table excludes tickers flagged by a simple anomaly screen for "
    "unusually large one-day price moves. These flags are intended for review, "
    "not as definitive proof of bad data.",
    note_style
))
story.append(Spacer(1, 16))

story.append(Paragraph("Price History", section_style))
story.append(Paragraph(
    "The chart below is based on the review-adjusted top 5 so that flagged extreme "
    "moves do not compress the scale and reduce readability.",
    note_style
))
story.append(Spacer(1, 6))
story.append(Image(
    "top5_price_history.png",
    width=6.5 * inch,
    height=6.5 * inch * 5.5 / 9
))

doc.build(story)
print("PDF written to output/equity_analysis_himanshi_agrawal.pdf")
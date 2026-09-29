import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import time

CSV_FILE = "mht_cet_all_india_clean.csv"
OUTPUT_PDF = "JEE_Percentile_1.pdf"


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' and footer to every page automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))

        # Footer text
        footer_text = (
            "MHT-CET 2026[JEE] Ranks v/s percentile | Created by Malhar Kshirsagar"
        )
        page_str = f"Page {self._pageNumber} of {page_count}"

        self.drawString(54, 36, footer_text)
        self.drawRightString(612 - 54, 36, page_str)

        # Subtle horizontal divider line above footer
        self.setStrokeColor(colors.HexColor("#D3D3D3"))
        self.setLineWidth(0.5)
        self.line(54, 48, 612 - 54, 48)
        self.restoreState()


def generate_pdf():
    start_time = time.time()
    print(f"[*] Reading '{CSV_FILE}'...")

    df = pd.read_csv(CSV_FILE, dtype=str)

    # Filter candidates who have a JEE score
    # Primary exam score is in 'Percentile /Mark', and JEE Total is in 'Percentile /Mark' for Merit Exam == 'JEE'
    # Ensure Merit No is numeric for correct sorting
    df["Merit_No_Int"] = pd.to_numeric(df["Merit No"], errors="coerce")
    df = df.dropna(subset=["Merit_No_Int"])
    df["Merit_No_Int"] = df["Merit_No_Int"].astype(int)

    # Sort strictly by Merit Rank ascending
    df = df.sort_values(by="Merit_No_Int", ascending=True)

    # Standardize the exact percentile text representation
    df["Percentile_Exact"] = df["Percentile /Mark"].astype(str).str.strip()

    print("[*] Grouping percentiles and computing rank ranges...")

    # Group by exact percentile while preserving rank order
    # Using groupby with sort=False keeps the first-seen rank ordering
    records = []
    for percentile, group in df.groupby("Percentile_Exact", sort=False):
        min_rank = group["Merit_No_Int"].min()
        max_rank = group["Merit_No_Int"].max()
        count = len(group)

        if min_rank == max_rank:
            rank_range = str(min_rank)
        else:
            rank_range = f"{min_rank} - {max_rank}"

        records.append([percentile, rank_range, str(count)])

    print(f"[*] Total unique percentile buckets: {len(records):,}")
    print(f"[*] Building PDF report '{OUTPUT_PDF}'...")

    # Document setup: standard letter size with 0.75-inch (54 pt) margins
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=14,
    )

    story = [
        Paragraph(
            "MHT-CET (PCM) All India Merit List - Rank Distribution", title_style
        ),
        Paragraph(
            f"Consolidated analysis of <b>{len(df):,}</b> candidates grouped by exact percentile.",
            subtitle_style,
        ),
        Spacer(1, 4),
    ]

    # Table Data Construction
    table_data = [["Percentile (Exact)", "Merit Rank Range", "Candidates"]]
    table_data.extend(records)

    # Table styling for high-density, crisp reporting
    col_widths = [160, 204, 140]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                # Header row styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                # Content styling
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
                # Alternating subtle row colors
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F8FAFC")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ]
        )
    )

    story.append(t)

    # Build PDF with dynamic page numbering
    doc.build(story, canvasmaker=NumberedCanvas)

    elapsed = time.time() - start_time
    print(f"[✓] PDF created successfully in {elapsed:.2f}s -> '{OUTPUT_PDF}'")


if __name__ == "__main__":
    generate_pdf()

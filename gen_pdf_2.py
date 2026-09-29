import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

CSV_PATH = "mht_cet_all_india_clean.csv"
OUTPUT_PDF = "All_India_Percentile_Distribution.pdf"

HEADER_TEXT = "MHT-CET 2026: CANDIDATE DISTRIBUTION BY PERCENTILE TIER"
FOOTER_TEXT = "MHT-CET 2026[JEE] Ranks v/s percentile | Created by Malhar Kshirsagar"


class CustomCanvas(canvas.Canvas):
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Bottom divider line
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 40, 612 - 54, 40)

        # Left footer and Right page indicator
        self.drawString(54, 28, FOOTER_TEXT)
        self.drawRightString(612 - 54, 28, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


# 1. Load and sort
df = pd.read_csv(CSV_PATH, dtype=str)
df["Merit_Rank"] = pd.to_numeric(df["Merit No"], errors="coerce")
df["Score"] = pd.to_numeric(df["Percentile /Mark"], errors="coerce")
df = df.dropna(subset=["Merit_Rank", "Score"]).sort_values("Merit_Rank")

# 2. Granular Tiers
TIERS = [
    (99.75, 100.0, "99.75 — 100.00"),
    (99.50, 99.75, "99.50 — 99.75"),
    (99.25, 99.50, "99.25 — 99.50"),
    (99.00, 99.25, "99.00 — 99.25"),
    (98.00, 99.00, "98.00 — 99.00"),
    (97.00, 98.00, "97.00 — 98.00"),
    (96.00, 97.00, "96.00 — 97.00"),
    (95.00, 96.00, "95.00 — 96.00"),
    (92.50, 95.00, "92.50 — 95.00"),
    (90.00, 92.50, "90.00 — 92.50"),
    (85.00, 90.00, "85.00 — 90.00"),
    (80.00, 85.00, "80.00 — 85.00"),
    (75.00, 80.00, "75.00 — 80.00"),
    (70.00, 75.00, "70.00 — 75.00"),
    (60.00, 70.00, "60.00 — 70.00"),
    (50.00, 60.00, "50.00 — 60.00"),
    (40.00, 50.00, "40.00 — 50.00"),
    (0.00, 40.00, "Below 40.00"),
]

# 3. Calculate rows
data = [["Percentile Tier", "Merit Rank Range", "Candidates"]]

for lower, upper, label in TIERS:
    if upper == 100.0:
        subset = df[(df["Score"] >= lower) & (df["Score"] <= upper)]
    else:
        subset = df[(df["Score"] >= lower) & (df["Score"] < upper)]

    count = len(subset)
    if count == 0:
        continue

    min_rank = int(subset["Merit_Rank"].min())
    max_rank = int(subset["Merit_Rank"].max())
    span = f"{min_rank:,} — {max_rank:,}" if min_rank != max_rank else f"{min_rank:,}"

    data.append([label, span, f"{count:,}"])

# 4. Build Document
doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=letter,
    leftMargin=54,
    rightMargin=54,
    topMargin=54,
    bottomMargin=54,
)

styles = getSampleStyleSheet()
header_style = ParagraphStyle(
    name="CleanHeader",
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=15,
    alignment=1,  # Centered
    textColor=colors.HexColor("#1A202C"),
)

elements = [Paragraph(HEADER_TEXT, header_style), Spacer(1, 14)]

table = Table(data, colWidths=[150, 204, 150], repeatRows=1)
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A202C")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9.5),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8.5),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#F7FAFC")],
            ),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]
    )
)

elements.append(table)

doc.build(elements, canvasmaker=CustomCanvas)
print(f"[✓] Created: {OUTPUT_PDF}")

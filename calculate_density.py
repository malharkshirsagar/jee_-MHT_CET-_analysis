import csv
import re
import time
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# --- CONFIGURATION ---
INPUT_TXT = "2026A.txt"
CLEAN_CSV = "mht_cet_all_india_clean.csv"
OUTPUT_PDF = "MHT_CET_Category_Percentile_Distribution.pdf"

CATEGORIES = ["OPEN", "OBC", "SEBC", "SC", "NT-C", "VJ/DT", "NT-D", "NT-B", "SBC", "ST"]

TIER_BINS = [
    (99.0, 100.0, "99.0 — 100.0"),
    (95.0, 99.0, "95.0 — 99.0"),
    (90.0, 95.0, "90.0 — 95.0"),
    (85.0, 90.0, "85.0 — 90.0"),
    (80.0, 85.0, "80.0 — 85.0"),
    (75.0, 80.0, "75.0 — 80.0"),
    (70.0, 75.0, "70.0 — 75.0"),
    (60.0, 70.0, "60.0 — 70.0"),
    (50.0, 60.0, "50.0 — 60.0"),
    (40.0, 50.0, "40.0 — 50.0"),
    (0.0, 40.0, "Below 40.0"),
]

CSV_HEADERS = [
    "Merit No",
    "Application ID",
    "Candidate's Full Name",
    "Merit Exam",
    "Percentile /Mark",
    "JEE Math Percentile",
    "JEE Physics Percentile",
    "JEE Chemistry Percentile",
    "MHT-CET PCM Total Percentile",
    "MHT-CET Math Percentile",
    "MHT-CET Physics Percentile",
    "MHT-CET Chemistry Percentile",
    "HSC PCM %",
    "HSC Math %",
    "HSC Physics %",
    "HSC / Diploma / D. Voc. Total %",
    "SSC Total %",
    "SSC Math %",
    "SSC Science %",
    "SSC English %",
]

CANDIDATE_REGEX = re.compile(
    r"^(\d+)\s+(EN26\d+)\s+(.+?)\s+(JEE|MHT-CET)\s+([\d\.\s]+)$"
)


# --- STEP 1: PARSE AND ALIGN DATA ---
def extract_and_clean_data(in_file: str, out_csv: str) -> pd.DataFrame:
    print(f"[*] Step 1: Parsing raw candidate rows from '{in_file}'...")
    parsed_rows = []

    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if "EN26" not in stripped:
                continue

            match = CANDIDATE_REGEX.match(stripped)
            if match:
                merit_no = match.group(1)
                app_id = match.group(2)
                candidate_name = match.group(3).strip()
                exam_type = match.group(4)
                scores = match.group(5).split()

                if len(scores) == 12:
                    jee_scores = scores[:4]
                    cet_scores = ["", "", "", ""]
                    academic_scores = scores[4:]
                    aligned_scores = jee_scores + cet_scores + academic_scores
                elif len(scores) == 16:
                    aligned_scores = scores
                else:
                    aligned_scores = scores + [""] * (16 - len(scores))

                row = [merit_no, app_id, candidate_name, exam_type] + aligned_scores
                parsed_rows.append(row)

    print(f"[*] Parsed {len(parsed_rows):,} valid rows. Writing to '{out_csv}'...")
    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(CSV_HEADERS)
        for r in parsed_rows:
            writer.writerow(r)

    df = pd.DataFrame(parsed_rows, columns=CSV_HEADERS)
    return df


# --- STEP 2: CANVAS FOR DYNAMIC PAGE NUMBERING ---
class LandscapeNumberedCanvas(canvas.Canvas):
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
        self.setFillColor(colors.HexColor("#4A5568"))

        footer_text = (
            "MHT-CET 2026[JEE] Ranks v/s percentile | Created by Malhar Kshirsagar"
        )
        page_str = f"Page {self._pageNumber} of {page_count}"

        self.drawString(36, 26, footer_text)
        self.drawRightString(792 - 36, 26, page_str)

        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 36, 792 - 36, 36)
        self.restoreState()


# --- STEP 3: STATISTICAL DENSITY & PDF GENERATION ---
def generate_pdf_report(df: pd.DataFrame, out_pdf: str):
    print(f"[*] Step 2: Calculating statistical density & rank spans...")

    df["Merit_Rank"] = pd.to_numeric(df["Merit No"], errors="coerce")
    df["Percentile_Val"] = pd.to_numeric(df["Percentile /Mark"], errors="coerce")
    df = df.dropna(subset=["Merit_Rank", "Percentile_Val"]).sort_values("Merit_Rank")

    cat_col = None
    for possible in ["Category", "Seat_Type", "Candidate Category"]:
        if possible in df.columns:
            cat_col = possible
            break

    headers = ["Percentile Tier", "State Rank Span"] + CATEGORIES + ["Total Count"]
    table_rows = [headers]

    for lower, upper, label in TIER_BINS:
        if upper == 100.0:
            subset = df[
                (df["Percentile_Val"] >= lower) & (df["Percentile_Val"] <= upper)
            ]
        else:
            subset = df[
                (df["Percentile_Val"] >= lower) & (df["Percentile_Val"] < upper)
            ]

        total_count = len(subset)
        if total_count == 0:
            continue

        min_rank = int(subset["Merit_Rank"].min())
        max_rank = int(subset["Merit_Rank"].max())
        rank_span = f"{min_rank:,} — {max_rank:,}"

        cat_counts = []
        if cat_col:
            val_counts = subset[cat_col].value_counts().to_dict()
            for cat in CATEGORIES:
                cat_counts.append(f"{val_counts.get(cat, 0):,}")
        else:
            cat_counts = ["0"] * len(CATEGORIES)

        table_rows.append([label, rank_span] + cat_counts + [f"{total_count:,}"])

    print(f"[*] Step 3: Compiling PDF document '{out_pdf}'...")
    doc = SimpleDocTemplate(
        out_pdf,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="RepTitle",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
    )
    sub_style = ParagraphStyle(
        name="RepSub",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=8,
    )

    story = [
        Paragraph(
            "MHT-CET / JEE Merit List — Category-Wise Distribution Breakdown",
            title_style,
        ),
        Paragraph(
            f"Evaluated across {len(df):,} records. Ranks and tier spans are derived from exact data boundaries.",
            sub_style,
        ),
        Spacer(1, 4),
    ]

    col_widths = [85, 105] + [46] * len(CATEGORIES) + [70]
    report_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
    report_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F8FAFC")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (-1, 1), (-1, -1), colors.HexColor("#F1F5F9")),
            ]
        )
    )

    story.append(report_table)
    doc.build(story, canvasmaker=LandscapeNumberedCanvas)


def main():
    start_total = time.time()
    df = extract_and_clean_data(INPUT_TXT, CLEAN_CSV)
    generate_pdf_report(df, OUTPUT_PDF)
    print(f"\n[✓] Pipeline finished successfully in {time.time() - start_total:.2f}s!")
    print(f"[✓] Generated Files:\n    - CSV: '{CLEAN_CSV}'\n    - PDF: '{OUTPUT_PDF}'")


if __name__ == "__main__":
    main()

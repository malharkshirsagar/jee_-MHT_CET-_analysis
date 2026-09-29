import csv
import re
import time

INPUT_TXT = "2026A3.txt"
OUTPUT_CSV = "mht_cet_all_india_clean.csv"

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


def parse_merit_list(in_file: str, out_csv: str):
    start = time.time()
    print(f"[*] Reading and parsing '{in_file}'...")

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

                # Case 1: Appeared ONLY for JEE (missing 4 MHT-CET columns)
                if len(scores) == 12:
                    jee_scores = scores[:4]  # Total, Math, Physics, Chem
                    cet_scores = ["", "", "", ""]  # Blank MHT-CET columns
                    academic_scores = scores[4:]  # HSC (4) + SSC (4)
                    aligned_scores = jee_scores + cet_scores + academic_scores

                # Case 2: Appeared for BOTH JEE & MHT-CET (all 16 scores present)
                elif len(scores) == 16:
                    aligned_scores = scores

                # Fallback for unexpected token counts
                else:
                    aligned_scores = scores + [""] * (16 - len(scores))

                row = [merit_no, app_id, candidate_name, exam_type] + aligned_scores
                parsed_rows.append(row)

    print(f"[*] Writing {len(parsed_rows):,} records to '{out_csv}'...")

    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(CSV_HEADERS)
        for row in parsed_rows:
            writer.writerow(row)

    elapsed = time.time() - start
    print(f"[✓] Completed in {elapsed:.2f}s!")
    print(f"[✓] Extracted {len(parsed_rows):,} candidates perfectly into CSV.")


if __name__ == "__main__":
    parse_merit_list(INPUT_TXT, OUTPUT_CSV)

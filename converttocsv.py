import csv
import re
import time

INPUT_TXT = "2026A3.txt"  # or your merged/raw file containing the text
OUTPUT_CSV = "mht_cet_all_india_clean.csv"

# Exactly 20 columns matching your initial header block
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

# Regex pattern that anchors directly on the candidate line
# Group 1: Merit No
# Group 2: App ID
# Group 3: Full Name (everything until JEE or MHT-CET)
# Group 4: Exam Type
# Group 5: All 16 trailing numbers
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

            # Ignore everything that isn't a candidate row (headers, footers, notes)
            if "EN26" not in stripped:
                continue

            match = CANDIDATE_REGEX.match(stripped)
            if match:
                merit_no = match.group(1)
                app_id = match.group(2)
                candidate_name = match.group(3).strip()
                exam_type = match.group(4)

                # Split trailing score string into individual columns
                scores = match.group(5).split()

                # Build row: 1 + 1 + 1 + 1 + 16 = 20 total columns
                row = [merit_no, app_id, candidate_name, exam_type] + scores
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

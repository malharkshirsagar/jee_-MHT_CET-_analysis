import csv

CSV_PATH = "mht_cet_all_india_clean.csv"

with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    expected_cols = len(header)

    mismatched = []
    total = 0
    for idx, row in enumerate(reader, start=2):
        total += 1
        if len(row) != expected_cols:
            mismatched.append((idx, len(row), row[:2]))

print(f"Total candidate records checked: {total:,}")
if not mismatched:
    print(f"Perfect! All rows have exactly {expected_cols} columns.")
else:
    print(f"Found {len(mismatched)} rows with column count issues:")
    for line_no, count, preview in mismatched[:5]:
        print(f"  Line {line_no}: expected {expected_cols}, got {count} -> {preview}")

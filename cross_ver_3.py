import csv

with open("mht_cet_all_india_clean.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    bad_rows = [
        idx for idx, row in enumerate(reader, start=2) if len(row) != len(header)
    ]

print(f"Validation complete: {len(bad_rows)} mismatched rows found.")

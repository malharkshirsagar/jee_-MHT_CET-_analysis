import re
import time

INPUT_TXT = "2026A.txt"
OUTPUT_TXT = "2026A1.txt"
PAGE_DELIMITER = "--- PAGE"


def clean_pdf_dump(in_file: str, out_file: str):
    start = time.time()
    print(f"[*] Reading '{in_file}'...")

    with open(in_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by each page block
    pages = content.split(PAGE_DELIMITER)
    print(f"[*] Total page blocks found: {len(pages) - 1}")

    cleaned_records = []
    skipped_headers = 0

    for idx, page in enumerate(pages):
        if not page.strip():
            continue

        # Look for the very first candidate ID (e.g., EN26123456)
        match = re.search(r"\bEN26\d+", page)

        if match:
            # Drop everything before the first candidate ID on this page
            # Backtrack to the start of the line where EN26 was found
            start_pos = match.start()
            line_start = page.rfind("\n", 0, start_pos)
            line_start = 0 if line_start == -1 else line_start + 1

            # Keep only candidate data
            valid_content = page[line_start:].strip()
            if valid_content:
                cleaned_records.append(valid_content)
                skipped_headers += 1
        else:
            # Page without candidates (cover page, instructions, etc.)
            continue

    print(f"[*] Writing clean data to '{out_file}'...")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_records))

    elapsed = time.time() - start
    print(f"[✓] Completed in {elapsed:.2f}s!")
    print(f"[✓] Stripped headers from {skipped_headers} pages.")
    print(f"[✓] Cleaned file ready at: '{out_file}'")


if __name__ == "__main__":
    clean_pdf_dump(INPUT_TXT, OUTPUT_TXT)

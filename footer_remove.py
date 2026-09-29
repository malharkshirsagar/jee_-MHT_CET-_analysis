import re
import time

INPUT_TXT = "2026A1.txt"
OUTPUT_TXT = "2026A2.txt"

# Pattern matching footer dates and page indicators
FOOTER_PATTERN = re.compile(r"Published on|Page\s+\d+\s+of\s+\d+", re.IGNORECASE)


def remove_footers(in_file: str, out_file: str):
    start = time.time()
    print(f"[*] Stripping footer lines from '{in_file}'...")

    kept_lines = []
    removed_count = 0

    with open(in_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Drop footer line
            if FOOTER_PATTERN.search(stripped):
                removed_count += 1
                continue

            kept_lines.append(line)

    with open(out_file, "w", encoding="utf-8") as f:
        f.writelines(kept_lines)

    elapsed = time.time() - start
    print(f"[✓] Finished in {elapsed:.2f}s!")
    print(f"[✓] Removed {removed_count:,} footer lines.")
    print(f"[✓] Output saved to '{out_file}'")


if __name__ == "__main__":
    remove_footers(INPUT_TXT, OUTPUT_TXT)

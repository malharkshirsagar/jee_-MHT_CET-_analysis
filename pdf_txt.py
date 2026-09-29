import pymupdf  # imports the PyMuPDF C-engine
import time

PDF_PATH = "2026A.pdf"  # Path to your merit list PDF
TXT_OUTPUT = "2026A.txt"  # Output plain text file


def dump_pdf_to_txt(pdf_path: str, output_path: str):
    start_time = time.time()
    print(f"[*] Opening '{pdf_path}'...")

    doc = pymupdf.open(pdf_path)
    total_pages = doc.page_count
    print(f"[*] Total Pages Detected: {total_pages}")
    print("[*] Starting extraction stream...")

    with open(output_path, "w", encoding="utf-8") as out_file:
        for page_idx in range(total_pages):
            page = doc[page_idx]

            # sort=True sorts text top-to-bottom, left-to-right
            page_text = page.get_text("text", sort=True)

            out_file.write(page_text)
            out_file.write(f"\n\n--- PAGE {page_idx + 1} END ---\n\n")

            # Progress milestone every 250 pages
            if (page_idx + 1) % 250 == 0 or (page_idx + 1) == total_pages:
                elapsed = time.time() - start_time
                pages_done = page_idx + 1
                rate = pages_done / elapsed if elapsed > 0 else 0
                print(
                    f" -> Processed {pages_done}/{total_pages} pages ({rate:.1f} pages/sec)"
                )

    doc.close()
    total_time = time.time() - start_time
    print(f"\n[✓] Finished in {total_time:.2f} seconds!")
    print(f"[✓] Extracted text saved to: '{output_path}'")


if __name__ == "__main__":
    dump_pdf_to_txt(PDF_PATH, TXT_OUTPUT)

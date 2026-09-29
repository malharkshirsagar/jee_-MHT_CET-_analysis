import pikepdf

input_file = "2026.pdf"
output_file = "2026A.pdf"

print("Opening original PDF...")
with pikepdf.open(input_file) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")

    # 0-indexed: index 0 = page 1, index 2955 = page 2955 inclusive
    end_idx = 2955

    print(f"Slicing pages 1 to {end_idx}...")
    new_pdf = pikepdf.Pdf.new()

    # Direct binary slice
    new_pdf.pages.extend(pdf.pages[:end_idx])

    print(f"Writing output to {output_file}...")
    new_pdf.save(output_file)

print("Done! Sliced PDF generated successfully.")

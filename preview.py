input_file = "2026A3.txt"
output_file = "preview_100_lines.txt"

try:
    with open(input_file, "r", encoding="utf-8") as f_in, open(
        output_file, "w", encoding="utf-8"
    ) as f_out:
        for idx in range(1, 301):
            line = f_in.readline()
            if not line:
                break
            f_out.write(line)

    print(f"Successfully created '{output_file}' with the first 100 lines.")

except FileNotFoundError:
    print(f"Error: '{input_file}' not found.")

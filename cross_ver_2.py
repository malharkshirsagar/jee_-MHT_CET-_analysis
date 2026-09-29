with open("2026A3.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "EN26467181" in line:
            print("RAW LINE:")
            print(line.strip())
            break

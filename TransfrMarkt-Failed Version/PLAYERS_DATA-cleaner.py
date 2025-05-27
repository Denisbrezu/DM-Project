import csv

def clean_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        headers = reader.fieldnames

    # Print headers for debugging
    print("Detected headers:", headers)

    # Find the actual name of the "Nume" column (account for invisible characters)
    name_col = next((h for h in headers if "nume" in h.lower()), None)
    if not name_col:
        print("❌ Could not find 'Nume' column.")
        return

    print(f"Using '{name_col}' as the name column.")

    original_count = len(rows)
    cleaned_rows = []
    removed_rows = []
    seen_names = set()

    for row in rows:
        raw_name = row.get(name_col, "")
        name = raw_name.strip().replace("\xa0", "").replace("\u200b", "")

        if name == "":
            removed_rows.append({**row, "reason": "Empty name"})
            continue

        if name in seen_names:
            removed_rows.append({**row, "reason": "Duplicate name"})
            continue

        seen_names.add(name)
        cleaned_rows.append(row)

    empty_names_removed = sum(1 for r in removed_rows if r["reason"] == "Empty name")
    duplicates_removed = sum(1 for r in removed_rows if r["reason"] == "Duplicate name")
    cleaned_count = len(cleaned_rows)

    # Write cleaned data
    with open(file_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print("\n✅ Cleaning complete!")
    print(f"Original rows: {original_count}")
    print(f"Removed empty 'Nume': {empty_names_removed}")
    print(f"Removed duplicates: {duplicates_removed}")
    print(f"Remaining rows: {cleaned_count}")

if __name__ == "__main__":
    clean_csv("PLAYERS_DATA.csv")

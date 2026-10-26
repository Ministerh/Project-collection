"""File organizer: sort files in a folder into subfolders by type (and month)."""
import argparse
import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG_NAME = "organizer_log.csv"
LOG_FIELDS = ["timestamp", "original", "new"]

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "Documents": {".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"},
    "Videos": {".mp4", ".mov", ".mkv"},
    "Audio": {".mp3", ".wav", ".m4a"},
    "Archives": {".zip", ".rar", ".7z"},
    "Code": {".py", ".js", ".html", ".css"},
}


def get_category(path):
    ext = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def unique_destination(dest):
    if not dest.exists():
        return dest
    counter = 1
    while True:
        candidate = dest.with_name(f"{dest.stem} ({counter}){dest.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def build_destination(folder, file, by_date):
    target_dir = folder / get_category(file)
    if by_date:
        month = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m")
        target_dir = target_dir / month
    return unique_destination(target_dir / file.name)


def organize(folder, dry_run=False, by_date=False):
    moved = Counter()
    skipped = 0
    log_rows = []
    now = datetime.now().isoformat(timespec="seconds")
    label = "[DRY RUN] " if dry_run else ""

    for item in sorted(folder.iterdir()):
        if not item.is_file() or item.name.startswith(".") or item.name == LOG_NAME:
            skipped += 1
            continue
        dest = build_destination(folder, item, by_date)
        note = "   (name already existed)" if dest.name != item.name else ""
        print(f"{label}{item.name} -> {dest.relative_to(folder).as_posix()}{note}")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(dest))
            log_rows.append({"timestamp": now, "original": str(item), "new": str(dest)})
        moved[get_category(item)] += 1
    return moved, skipped, log_rows


def write_log(folder, rows):
    if not rows:
        return
    log_path = folder / LOG_NAME
    is_new = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Sort files into subfolders by type.")
    parser.add_argument("folder", help="folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving files")
    parser.add_argument("--by-date", action="store_true", help="add a YYYY-MM subfolder")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        sys.exit(f"Error: '{folder}' is not a folder.")

    moved, skipped, log_rows = organize(folder, args.dry_run, args.by_date)
    write_log(folder, log_rows)

    total = sum(moved.values())
    if total == 0:
        print("No files to organize.")
    else:
        breakdown = ", ".join(f"{cat} {n}" for cat, n in moved.most_common())
        verb = "Would move" if args.dry_run else "Moved"
        print(f"{verb} {total} files: {breakdown}")
    print(f"Skipped {skipped} (folders or hidden files)")


if __name__ == "__main__":
    main()
# File Organizer

A command-line tool that tidies a messy folder by sorting its files into
subfolders by type (and optionally by month), with a safe preview mode and a
log of every move.

## Features

- Sorts files into `Images`, `Documents`, `Videos`, `Audio`, `Archives`,
  `Code`, and `Other` based on their extension.
- Matches extensions case-insensitively, so `.JPG` and `.jpg` are treated the
  same.
- `--dry-run` previews every move without touching the disk.
- `--by-date` adds a `YYYY-MM` level inside each category, based on the
  file's modified date.
- Never overwrites: if a file with the same name already exists in the
  target, the new file gets a numbered suffix like `photo (1).jpg`.
- Never deletes anything.
- Logs every move to `organizer_log.csv`.
- Prints a summary of what was moved and what was skipped.

## Usage

```
python file_organizer.py <folder> [--dry-run] [--by-date]
```

| Option | What it does |
|--------|--------------|
| `<folder>` | The folder to organize |
| `--dry-run` | Show what would happen, and change nothing |
| `--by-date` | Add a `YYYY-MM` subfolder, e.g. `Images/2026-10/` |

Always try a dry run first:

```
python file_organizer.py "C:\path\to\folder" --dry-run
python file_organizer.py "C:\path\to\folder"
```

## Example output

```
[DRY RUN] photo.jpg -> Images/photo.jpg
[DRY RUN] report.pdf -> Documents/report.pdf
[DRY RUN] backup.zip -> Archives/backup.zip
Would move 3 files: Images 1, Documents 1, Archives 1
Skipped 2 (folders or hidden files)
```

A real run drops the `[DRY RUN]` tag, and name clashes are marked:

```
photo.jpg -> Images/photo (1).jpg   (name already existed)
```

## Categories

| Category | Extensions |
|----------|------------|
| Images | .jpg .jpeg .png .gif .webp |
| Documents | .pdf .docx .txt .xlsx .pptx .csv |
| Videos | .mp4 .mov .mkv |
| Audio | .mp3 .wav .m4a |
| Archives | .zip .rar .7z |
| Code | .py .js .html .css |
| Other | everything else, including files with no extension |

To add or change a category, edit the `CATEGORIES` dictionary at the top of
`file_organizer.py`.

## Move log: `organizer_log.csv`

| column | example |
|--------|---------|
| timestamp | 2026-10-26T11:30:00 |
| original | C:\Downloads\photo.jpg |
| new | C:\Downloads\Images\photo.jpg |

The log is created inside the organized folder and grows with each real run.
Dry runs never write to it.

## Behaviour rules

- Only files in the top level of the chosen folder are moved, and subfolders
  and their contents are left alone.
- Hidden files (names starting with `.`) and the log file are skipped.
- Running it twice moves nothing the second time, since everything is already
  sorted.
- A missing or invalid folder prints a one-line error instead of a traceback.

## Testing it safely

Try it on a throwaway folder, not your real Downloads:

1. Create a test folder with a few empty files of different types (for
   example `photo.jpg`, `PHOTO2.JPG`, `report.pdf`, `song.mp3`, `README`).
2. Run with `--dry-run` and confirm nothing moved.
3. Run for real and check the category folders and `organizer_log.csv`.
4. Run it again and confirm that nothing new moves.
5. Add another `photo.jpg` and rerun to see the `photo (1).jpg` rename.

## Project structure

```
file_organizing_automation_03/
├── file_organizer.py
└── README.md
```

## Tech

Python 3, standard library only (`pathlib`, `shutil`, `argparse`, `csv`,
`datetime`, `collections`).

## Limitations

- Hidden files are detected by a leading `.` only, so files hidden through
  the Windows attribute are still moved.
- After the first run, the category folders count toward "Skipped".
- `--by-date` uses the modified date, not the creation date.
- There is no undo command yet, though the log has everything needed to
  build one.

## Ideas for next steps

- An `--undo` option that reverses moves using the log.
- Custom rules loaded from a JSON config file.
- Detect duplicate files by content hash (`hashlib`).
- Run automatically on a schedule or when new files appear.

## What I learned

(Fill this in after building it.)
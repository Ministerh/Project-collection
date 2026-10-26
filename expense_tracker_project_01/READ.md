# Expense Tracker (CLI + Django)

An expense tracker built twice: first as a command-line script, then as a
Django web app. Both record expenses, filter by category, delete entries, and
summarize spending per category.

## Screenshots

| Expense list | Add expense | Summary |
|--------------|-------------|---------|
| ![List](screenshots/list.png) | ![Add](screenshots/add.png) | ![Summary](screenshots/summary.png) |

## Part 1: Command-line version

### Features
- Add an expense with an amount, a category, an optional note, and an
  optional date (defaults to today).
- List all expenses, or filter by category.
- Delete an expense by its id.
- Summarize totals per category, largest first, with a grand total.
- Input validation: amounts must be positive numbers, and dates must be a
  real `YYYY-MM-DD` date.

### Usage
```
python expense_tracker.py add 12.5 food -n "lunch"
python expense_tracker.py add 40 transport -d 2026-10-10
python expense_tracker.py list
python expense_tracker.py list -c food
python expense_tracker.py delete 3
python expense_tracker.py summary
```

### Example output
```
Added #1: 12.50 (food)
#1   2026-10-09     12.50  food         lunch
transport         40.00
food              20.50
TOTAL             60.50
```

### Data
Expenses are stored in `expenses.json` in the folder where you run the
script. Each entry has an id, date, amount, category, and note. The CLI needs
no installs, since it uses only the Python standard library.

## Part 2: Django web version

### Features
- Expense list with a category filter.
- Add-expense form with validation (the amount must be at least 0.01).
- Delete button with a confirmation prompt (POST-only and CSRF-protected).
- Summary page with totals per category and a grand total.
- Django admin for managing data.

### Setup
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Then open http://127.0.0.1:8000/.

### Pages
| URL | Purpose |
|-----|---------|
| `/` | List expenses, filter with `?category=food` |
| `/add/` | Add an expense |
| `/summary/` | Totals per category |
|
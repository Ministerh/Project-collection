"""CLI Expense Tracker: add, list and summarize expenses stored"""

import argparse
import json
import math
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path


DATA_FILE = Path("expenses.json")

def load_expenses():
    if not DATA_FILE.exists():
        print("File not found.")
        return[]
    try:
        with DATA_FILE.open( "r", encoding="utf-8") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        print("expenses.json is corrupted. Fix or delete it")


def save_expenses(expenses):
    with DATA_FILE.open( "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2)

def add_expenses(args):
    expenses = load_expenses()
    print(expenses)
    print(type(expenses))
    expense = {
        "id": max((e["id"] for e in expenses), default=0) + 1,
        "date": args.date or date.today().isoformat(),
        "amount": round(args.amount, 2),
        "category": args.category.lower(),
        "description": args.description,
    }

    expenses.append(expense)
    save_expenses(expenses)
    print(f"Added  #{expense['id']}: {expense['amount']:.2f}: ({expense['category']}), {expense['description']} ")


def list_expenses(args):
    expenses = load_expenses()
    if args.category:
        expenses = [e for e in expenses if e["category"] == args.category.lower()]
    if not expenses:
        print("No expenses found")
        return
    for exp in expenses:
        print(f"#{exp['id']:< 3} {exp['date']} {exp['amount']:>8.2f} {exp['category']:<12} {exp['description']}")


def summarize_expenses(args):
    totals = defaultdict(float)
    for exp in load_expenses():
        totals[exp["category"]] += exp["amount"]
    if not totals:
        print("No expenses found")
        return
    for category, total in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"{category:>12}: {total:>10.2f}")
    print(f"{'TOTAL':<12} {sum(totals.values()):>10.2f}")

def delete_expenses(args):
    expenses = load_expenses()
    remaining = [e for e in expenses if e["id"] !=  args.id]
    if len(remaining) == len(expenses):
        print(f"No expenses found with id #{args.id}")
        return
    save_expenses(remaining)
    print(f"Deleted #{args.id}")

def positive_amount(value):
    try:
        amount = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a number")
    if not math.isfinite(amount)or amount < 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be greater than 0")
    return amount

def valid_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid date use YYYY-MM-DD")


def build_parser():
    parser = argparse.ArgumentParser(description="Adds, lists and summarizes expenses.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add an expense")
    add.add_argument("category", help="Category to add")
    add.add_argument("amount", type=positive_amount, help="Amount to add")
    add.add_argument("-dd",  "--description", default="")
    add.add_argument("-d", "--date", type=valid_date, help="YYYY-MM-DD")
    add.set_defaults(func=add_expenses)

    ls = subparsers.add_parser("list", help="List expenses")
    ls.add_argument("-c", "--category", help="Category to list")
    ls.set_defaults(func=list_expenses)

    delete = subparsers.add_parser("delete", help="Delete an expense")
    delete.add_argument("id", type=int, help="ID of expense to delete")
    delete.set_defaults(func=delete_expenses)

    summary = subparsers.add_parser("summary", help="totals per category")
    summary.set_defaults(func=summarize_expenses)

    return parser

def main():
    args = build_parser().parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

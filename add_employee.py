#!/usr/bin/env python3
"""
Adds ONE employee row to an Excel file. Jenkins runs this with the values
typed in "Build with Parameters".

    python3 add_employee.py --file employees.xlsx --name "Ravi Kumar" --empid EMP1011

- S.No is filled in automatically (last S.No + 1)
- Emp ID must not already exist in the file
- The row is added below the last filled row and the file is saved
"""
import argparse
import sys
from copy import copy

from openpyxl import load_workbook

HEADERS = ["S.No", "Name", "Emp ID"]


def fail(message):
    print("ERROR: " + message)
    sys.exit(1)


def as_number(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--name", default="")
    parser.add_argument("--empid", default="")
    args = parser.parse_args()

    name = args.name.strip()
    emp_id = args.empid.strip().upper()

    # A build started without any values (for example the very first build) adds nothing
    if not name and not emp_id:
        print("No Name or Emp ID entered - nothing added")
        return
    if not name:
        fail("Name is empty. Enter a Name and build again.")
    if not emp_id:
        fail("Emp ID is empty. Enter an Emp ID and build again.")

    try:
        workbook = load_workbook(args.file)
    except FileNotFoundError:
        fail(f"{args.file} not found")
    except PermissionError:
        fail(f"cannot open {args.file}. Close it in Excel and build again.")
    sheet = workbook.active

    # Check the column headings
    header = [str(cell.value).strip() if cell.value is not None else "" for cell in sheet[1]][:3]
    if header != HEADERS:
        fail(f"row 1 must be {HEADERS}, found {header}")

    # Read existing rows and find the last filled row
    last_row = 1
    numbers = []
    for row_number in range(2, sheet.max_row + 1):
        sno, existing_name, existing_id = (sheet.cell(row_number, col).value for col in (1, 2, 3))
        if all(v is None or str(v).strip() == "" for v in (sno, existing_name, existing_id)):
            continue
        last_row = row_number
        if as_number(sno) is not None:
            numbers.append(as_number(sno))
        if str(existing_id).strip().upper() == emp_id:
            fail(f"Emp ID {emp_id} already exists for {existing_name} (S.No {sno}). Nothing added.")

    # Add the new row
    new_sno = max(numbers, default=0) + 1
    new_row = last_row + 1
    for col, value in enumerate((new_sno, name, emp_id), start=1):
        cell = sheet.cell(new_row, col, value)
        above = sheet.cell(last_row, col)
        if last_row > 1 and above.has_style:
            cell._style = copy(above._style)

    try:
        workbook.save(args.file)
    except PermissionError:
        fail(f"cannot save {args.file}. Close it in Excel and build again.")

    print(f"Added row {new_row}: S.No {new_sno} | {name} | {emp_id}")
    print("\nLast 5 rows of the file:")
    for row_number in range(max(2, new_row - 4), new_row + 1):
        values = [sheet.cell(row_number, col).value for col in (1, 2, 3)]
        print(f"  {values[0]:>4} | {values[1]:<22} | {values[2]}")


if __name__ == "__main__":
    main()

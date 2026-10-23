"""
src/infrastructure/importing/spreadsheet_reader.py
==================================================
Spec 009 delivery I1: reading the Google Form's export — a `.csv` (UTF-8, with or without BOM, `,`
or `;`) or an `.xlsx` (its first sheet, values, not formulas). Cells keep their type: text stays
text and a numeric cell stays a number, so the domain decides what an identification is (FR-004,
US1-AS4). The first non-empty row is the header; empty rows are skipped and every row keeps its
line number in the sheet.

Limits (P12): at most MAX_BYTES, refused before parsing, and MAX_ROWS data rows, refused as soon as
one more appears. With `keep`, only those columns leave the reader (FR-016, N23): the form's other
columns are dropped while reading. Nothing here is written anywhere (FR-011).
"""

import csv
import io
from dataclasses import dataclass, field

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 500


class SpreadsheetError(ValueError):
    """A file that cannot be imported, with the reason as a code the screens put in words."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class SheetRow:
    number: int  # the row's line in the sheet, 1 = the first line of the file
    values: dict = field(repr=False)


@dataclass(frozen=True)
class Sheet:
    header: list
    rows: list = field(repr=False)


def _cells_of_csv(data: bytes):
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise SpreadsheetError("encoding") from None
    first_line = next((line for line in text.splitlines() if line.strip()), "")
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    for cells in csv.reader(io.StringIO(text, newline=""), delimiter=delimiter):
        yield cells


def _cells_of_xlsx(data: bytes):
    import openpyxl

    try:
        book = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception:
        raise SpreadsheetError("unreadable") from None
    try:
        for cells in book.worksheets[0].iter_rows(values_only=True):
            yield list(cells)
    finally:
        book.close()


def _blank(cell) -> bool:
    return cell is None or (isinstance(cell, str) and not cell.strip())


def read_spreadsheet(data: bytes, filename: str, keep=None) -> Sheet:
    """The header and the data rows of `data`, or SpreadsheetError. `keep` lists the mapped columns:
    only they appear in each row's values."""
    if len(data) > MAX_BYTES:
        raise SpreadsheetError("too_large")
    name = (filename or "").lower()
    if name.endswith(".csv"):
        lines = _cells_of_csv(data)
    elif name.endswith(".xlsx"):
        lines = _cells_of_xlsx(data)
    else:
        raise SpreadsheetError("format")

    header, rows = None, []
    for number, cells in enumerate(lines, start=1):
        if all(_blank(cell) for cell in cells):
            continue
        if header is None:
            header = ["" if cell is None else str(cell).strip() for cell in cells]
            while header and not header[-1]:
                header.pop()
            named = [column for column in header if column]
            if len(named) != len(set(named)):
                raise SpreadsheetError("duplicate_header")
            if keep is not None:
                missing = [column for column in keep if column not in named]
                if missing:
                    raise SpreadsheetError("unknown_column")
            wanted = set(named if keep is None else keep)
            continue
        if len(rows) == MAX_ROWS:
            raise SpreadsheetError("too_many_rows")
        values = {
            column: (cells[index] if index < len(cells) else None)
            for index, column in enumerate(header)
            if column in wanted
        }
        rows.append(SheetRow(number, values))
    if header is None:
        raise SpreadsheetError("empty")
    return Sheet(header, rows)

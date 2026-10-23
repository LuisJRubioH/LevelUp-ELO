"""
Spec 009 delivery I1: reading the Forms export (src/infrastructure/importing/spreadsheet_reader.py)
— CSV with or without BOM, `,` or `;`, and `.xlsx` with text and numeric cells as typed (FR-001,
US1-AS4); the size and row limits before reading everything (P12); and only the mapped columns
leave the reader (FR-016, N23). Invented identifications only.
"""

import io

import pytest

from src.infrastructure.importing.spreadsheet_reader import (
    MAX_BYTES,
    MAX_ROWS,
    SpreadsheetError,
    read_spreadsheet,
)

HEADER = ["Número de documento", "Nombres", "Apellidos", "Celular del acudiente"]


def _csv(rows, delimiter=",", bom=False) -> bytes:
    text = "\n".join(delimiter.join(cells) for cells in rows) + "\n"
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def _xlsx(rows) -> bytes:
    import openpyxl

    book = openpyxl.Workbook()
    for cells in rows:
        book.active.append(cells)
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


def _values(sheet):
    return [(row.number, row.values) for row in sheet.rows]


@pytest.mark.parametrize("delimiter", [",", ";"])
@pytest.mark.parametrize("bom", [False, True])
def test_spec009_a_csv_is_read_with_its_header_and_rows_as_typed(delimiter, bom):
    data = _csv(
        [
            HEADER,
            ["1012345678", "Ana María", "Pérez", "3001234567"],
            ["0012345", "Luis", "Gómez", ""],
        ],
        delimiter,
        bom,
    )

    sheet = read_spreadsheet(data, "respuestas.csv")

    assert sheet.header == HEADER  # no BOM left in the first name
    assert _values(sheet) == [
        (
            2,
            {
                "Número de documento": "1012345678",
                "Nombres": "Ana María",
                "Apellidos": "Pérez",
                "Celular del acudiente": "3001234567",
            },
        ),
        (
            3,
            {
                "Número de documento": "0012345",
                "Nombres": "Luis",
                "Apellidos": "Gómez",
                "Celular del acudiente": "",
            },
        ),
    ]


def test_spec009_an_xlsx_keeps_text_and_numeric_cells_as_typed():
    data = _xlsx(
        [
            HEADER,
            ["1012345678", "Ana", "Pérez", "3001234567"],  # typed as text
            [1098765432, "Luis", "Gómez", 3009876543],  # typed as numbers
            [1.2e9, "Eva", "Ruiz", None],  # a value the spreadsheet already altered
        ]
    )

    sheet = read_spreadsheet(data, "respuestas.xlsx")

    ids = [row.values["Número de documento"] for row in sheet.rows]
    assert ids[0] == "1012345678"
    assert ids[1] == 1098765432 and isinstance(ids[1], int)
    assert isinstance(ids[2], float)  # handed on as it is: the domain flags it, never the reader


def test_spec009_empty_rows_are_skipped_and_rows_keep_their_line_number():
    data = _csv([[""], HEADER, ["1", "A", "B", "C"], ["", "", "", ""], ["2", "D", "E", "F"]])

    sheet = read_spreadsheet(data, "r.csv")

    assert sheet.header == HEADER
    assert [row.number for row in sheet.rows] == [3, 5]


def test_spec009_only_the_mapped_columns_leave_the_reader():
    """FR-016, N23: the form's other columns — here the guardian's mobile — never reach the
    preview or the import; the header still lists them, for the mapping step."""
    data = _csv([HEADER, ["1012345678", "Ana", "Pérez", "3001234567"]])

    sheet = read_spreadsheet(data, "r.csv", keep=["Número de documento", "Nombres", "Apellidos"])

    assert sheet.header == HEADER
    assert sheet.rows[0].values == {
        "Número de documento": "1012345678",
        "Nombres": "Ana",
        "Apellidos": "Pérez",
    }
    assert "3001234567" not in repr(sheet)


def test_spec009_a_mapped_column_missing_from_the_file_is_refused():
    with pytest.raises(SpreadsheetError) as refused:
        read_spreadsheet(_csv([HEADER, ["1", "A", "B", "C"]]), "r.csv", keep=["Correo"])
    assert refused.value.code == "unknown_column"


def test_spec009_a_file_over_the_size_limit_is_refused_before_it_is_parsed():
    with pytest.raises(SpreadsheetError) as refused:
        read_spreadsheet(b"x" * (MAX_BYTES + 1), "r.csv")
    assert refused.value.code == "too_large"


def test_spec009_a_file_over_the_row_limit_is_refused():
    rows = [HEADER] + [[str(10_000_000 + n), "A", "B", ""] for n in range(MAX_ROWS + 1)]
    with pytest.raises(SpreadsheetError) as refused:
        read_spreadsheet(_csv(rows), "r.csv")
    assert refused.value.code == "too_many_rows"
    # Exactly the limit is accepted.
    assert len(read_spreadsheet(_csv(rows[:-1]), "r.csv").rows) == MAX_ROWS


@pytest.mark.parametrize(
    "data, name, code",
    [
        (b"", "r.csv", "empty"),
        (b"\n\n  \n", "r.csv", "empty"),
        (_csv([["a", "a"], ["1", "2"]]), "r.csv", "duplicate_header"),
        (b"\xff\xfe\x00a", "r.csv", "encoding"),
        (b"PK\x03\x04 not a workbook", "r.xlsx", "unreadable"),
        (b"a,b\n1,2\n", "r.txt", "format"),
    ],
)
def test_spec009_an_unusable_file_is_refused_with_its_reason(data, name, code):
    with pytest.raises(SpreadsheetError) as refused:
        read_spreadsheet(data, name)
    assert refused.value.code == code


def test_spec009_an_empty_xlsx_is_refused():
    with pytest.raises(SpreadsheetError) as refused:
        read_spreadsheet(_xlsx([]), "r.xlsx")
    assert refused.value.code == "empty"

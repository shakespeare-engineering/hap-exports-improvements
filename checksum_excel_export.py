from pathlib import Path
from typing import Callable

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.styles import PatternFill
from openpyxl.styles import Alignment

from models.air_system import AirSystem


def safe_number(
    value: float | None
) -> float:
    """
    Convert None to 0 for math.
    """

    return value or 0


def add_load_row(
    sheet,
    row: int,
    label: str,
    sensible: float | None,
    latent: float | None
) -> int:
    """
    Add a load row.

    Total is calculated
    with Excel formula.
    """

    sensible_value: float = (
        sensible or 0
    )

    latent_value: float = (
        latent or 0
    )

    # ======================================
    # Write values
    # ======================================

    sheet.cell(
        row=row,
        column=1,
        value=label
    )

    sheet.cell(
        row=row,
        column=2,
        value=sensible_value
    )

    sheet.cell(
        row=row,
        column=3,
        value=latent_value
    )

    # ======================================
    # Excel formula
    # ======================================

    sheet.cell(
        row=row,
        column=4,
        value=f"=SUM(B{row}:C{row})"
    )

    return row + 1


def add_section_header(
    sheet,
    row: int,
    title: str
) -> int:
    """
    Add a formatted section header.
    """

    sheet.merge_cells(
        start_row=row,
        start_column=1,
        end_row=row,
        end_column=4
    )

    cell = sheet.cell(
        row=row,
        column=1,
        value=title
    )

    cell.font = Font(
        bold=True
    )

    cell.fill = PatternFill(
        fill_type="solid",
        fgColor="DDDDDD"
    )

    return row + 1

def add_total_row(
    sheet,
    row: int,
    start_row: int,
    end_row: int,
    label: str = "Grand Total"
) -> int:
    """
    Add a total row using
    Excel SUM formulas.
    """

    sheet.cell(
        row=row,
        column=1,
        value=label
    )

    # Sensible total
    sheet.cell(
        row=row,
        column=2,
        value=(
            f"=SUM(B{start_row}"
            f":B{end_row})"
        )
    )

    # Latent total
    sheet.cell(
        row=row,
        column=3,
        value=(
            f"=SUM(C{start_row}"
            f":C{end_row})"
        )
    )

    # Overall total
    sheet.cell(
        row=row,
        column=4,
        value=(
            f"=SUM(D{start_row}"
            f":D{end_row})"
        )
    )

    # Formatting
    for column in range(1, 5):

        sheet.cell(
            row=row,
            column=column
        ).font = Font(
            bold=True
        )

    return row + 1

def format_sheet(sheet) -> None:
    """
    Apply simple formatting.
    """

    sheet.column_dimensions["A"].width = 30
    sheet.column_dimensions["B"].width = 15
    sheet.column_dimensions["C"].width = 15
    sheet.column_dimensions["D"].width = 15

    for column in [
        "B",
        "C",
        "D"
    ]:

        for cell in sheet[column]:

            cell.number_format = (
                '#,##0'
            )


def export_system_checksums(
    systems: dict[str, AirSystem],
    output_path: str | Path
) -> None:
    """
    Export system checksum workbook.
    """

    workbook: Workbook = Workbook()

    # Remove default sheet
    workbook.remove(
        workbook.active
    )

    for system in systems.values():

        sheet_name: str = (
            system.name[:31]
        )

        sheet = workbook.create_sheet(
            title=sheet_name
        )

        heat = system.heat_balance

        row: int = 1

        # ======================================
        # Title
        # ======================================

        sheet["A1"] = (
            "System Checksums"
        )

        sheet["A2"] = (
            "Shakespeare Engineering"
        )

        sheet["A4"] = (
            "System Name"
        )

        sheet["B4"] = (
            system.name
        )

        sheet["A1"].font = Font(
            bold=True,
            size=16
        )

        sheet["A2"].font = Font(
            italic=True
        )

        row = 6

        # ======================================
        # Cooling Conditions
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Cooling Conditions"
        )

        sheet.cell(
            row=row,
            column=1,
            value="Peak Time"
        )

        sheet.cell(
            row=row,
            column=2,
            value=(
                heat.cooling_design_time
            )
        )

        row += 1

        sheet.cell(
            row=row,
            column=1,
            value="Outside Air DB"
        )

        sheet.cell(
            row=row,
            column=2,
            value=(
                heat.cooling_oa_db_f
            )
        )

        row += 1

        sheet.cell(
            row=row,
            column=1,
            value="Outside Air WB"
        )

        sheet.cell(
            row=row,
            column=2,
            value=(
                heat.cooling_oa_wb_f
            )
        )

        row += 2

        # ======================================
        # Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Loads"
        )

        sheet.cell(
            row=row,
            column=1,
            value="Item"
        )

        sheet.cell(
            row=row,
            column=2,
            value="Sensible"
        )

        sheet.cell(
            row=row,
            column=3,
            value="Latent"
        )

        sheet.cell(
            row=row,
            column=4,
            value="Total"
        )

        row += 2

        # ======================================
        # Envelope Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Envelope Loads"
        )

        row = add_load_row(
            sheet,
            row,
            "Wall",
            heat.wall_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Roof",
            heat.roof_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Window",
            heat.window_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Skylight",
            heat.skylight_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Door",
            heat.door_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Floor",
            heat.floor_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Interior Wall",
            heat.interior_wall_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Ceiling",
            heat.ceiling_btu,
            None
        )

        row += 1

        # ======================================
        # Internal Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Internal Loads"
        )

        row = add_load_row(
            sheet,
            row,
            "People",
            heat.people_sensible_btu,
            heat.people_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Overhead Lighting",
            heat.overhead_lighting_btu,
            None
        )

        row += 1

        # ======================================
        # Equipment Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Equipment Loads"
        )

        row = add_load_row(
            sheet,
            row,
            "Task Lighting",
            heat.task_lighting_btu,
            None
        )

        row = add_load_row(
            sheet,
            row,
            "Electrical Equipment",
            heat.equipment_btu,
            None
        )

        # ======================================
        # Zone Total
        # ======================================

        row += 1

        zone_total_start_row: int = 14
        zone_total_end_row: int = row - 2

        row = add_total_row(
            sheet,
            row=row,
            start_row=zone_total_start_row,
            end_row=zone_total_end_row,
            label="Zone Total"
        )

        format_sheet(sheet)

    output_path = Path(
        output_path
    )

    workbook.save(
        output_path
    )

    print(
        f"\nSaved workbook:"
    )

    print(
        output_path
    )


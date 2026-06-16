from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.styles import PatternFill
from openpyxl.styles import Alignment

from models.air_system import AirSystem


def safe_number(
    value: float | None
) -> float:
    """
    Convert None to 0.
    """

    return value or 0


def add_section_header(
    sheet,
    row: int,
    title: str
) -> int:
    """
    Add formatted section header.
    """

    sheet.merge_cells(
        start_row=row,
        start_column=1,
        end_row=row,
        end_column=6
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


def add_load_row(
    sheet,
    row: int,
    label: str,
    sensible: float | None,
    latent: float | None,
    detail_value: float | None = None,
    detail_units: str | None = None
) -> int:
    """
    Add load row using Excel formulas.
    """

    sheet.cell(
        row=row,
        column=1,
        value=label
    )

    sheet.cell(
        row=row,
        column=2,
        value=safe_number(
            sensible
        )
    )

    sheet.cell(
        row=row,
        column=3,
        value=safe_number(
            latent
        )
    )

    # Total
    sheet.cell(
        row=row,
        column=4,
        value=f"=B{row}+C{row}"
    )

    # Details
    if detail_value is not None:

        detail_text: str = (
            f"{detail_value:,.0f}"
        )

        if detail_units:
            detail_text += (
                f" {detail_units}"
            )

        detail_cell = sheet.cell(
            row=row,
            column=6,
            value=detail_text
        )

        detail_cell.alignment = Alignment(
            horizontal="right"
        )

    return row + 1



def add_subtotal_row(
    sheet,
    row: int,
    title: str,
    start_row: int,
    end_row: int
) -> int:
    """
    Add subtotal row.
    """

    sheet.cell(
        row=row,
        column=1,
        value=title
    )

    sheet.cell(
        row=row,
        column=2,
        value=(
            f"=SUM(B{start_row}:"
            f"B{end_row})"
        )
    )

    sheet.cell(
        row=row,
        column=3,
        value=(
            f"=SUM(C{start_row}:"
            f"C{end_row})"
        )
    )

    sheet.cell(
        row=row,
        column=4,
        value=f"=B{row}+C{row}"
    )

    for cell in sheet[row]:
        cell.font = Font(
            bold=True
        )

    return row + 2


def format_sheet(
    sheet
) -> None:
    """
    Apply formatting.
    """

    sheet.column_dimensions[
        "A"
    ].width = 35

    for column in [
        "B",
        "C",
        "D"
    ]:
        sheet.column_dimensions[
            column
        ].width = 14

    sheet.column_dimensions[
        "E"
    ].width = 12

    sheet.column_dimensions[
        "F"
    ].width = 18

    for column in [
        "B",
        "C",
        "D"
    ]:
        for cell in sheet[column]:
            cell.number_format = (
                '#,##0'
            )

    for cell in sheet["E"]:
        cell.number_format = (
            '0.0%'
        )


def export_system_checksums(systems: dict[str, AirSystem], output_path: str | Path) -> None:
    """
    Export checksum workbook.
    """

    workbook: Workbook = (Workbook())

    # Remove the default sheet
    workbook.remove(workbook.active)

    for system in systems.values():

        sheet = (workbook.create_sheet(title=(system.name[:31])))

        heat = (system.heat_balance)

        row: int = 1

        # ======================================
        # Title
        # ======================================

        sheet["A1"] = ("System Checksums")

        sheet["A2"] = ("Shakespeare Engineering")

        sheet["A4"] = ("Project")

        sheet["B4"] = (system.project_name)

        sheet["A5"] = ("System Name")

        sheet["B5"] = (system.name)

        sheet["A1"].font = Font(
            bold=True,
            size=16
        )

        sheet["A2"].font = Font(
            italic=True
        )

        # Set the initial row
        row = 7

        # ======================================
        # Cooling Conditions
        # ======================================

        row = (
            add_section_header(
                sheet,
                row,
                "Cooling Conditions"
            )
        )

        sheet.cell(
            row=row,
            column=1,
            value="Peak Time"
        )
        sheet.cell(
            row=row,
            column=2,
            value= heat.cooling_design_time
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
            value=(heat.cooling_oa_db_f)
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
            value= heat.cooling_oa_wb_f
        )

        row += 2

        # ======================================
        # Loads Header
        # ======================================

        row = (
            add_section_header(
                sheet,
                row,
                "Cooling Loads"
            )
        )

        header_cell = sheet.cell(
            row=row,
            column=1,
            value="Item"
        )
        header_cell.alignment = Alignment(horizontal="center")

        header_cell = sheet.cell(
            row=row,
            column=2,
            value="Sensible"
        )
        header_cell.alignment = Alignment(horizontal="center")

        header_cell = sheet.cell(
            row=row,
            column=3,
            value="Latent"
        )
        header_cell.alignment = Alignment(horizontal="center")

        header_cell = sheet.cell(
            row=row,
            column=4,
            value="Total Load"
        )
        header_cell.alignment = Alignment(horizontal="center")

        header_cell = sheet.cell(
            row=row,
            column=5,
            value="% Total Load"
        )
        header_cell.alignment = Alignment(horizontal="center")

        header_cell = sheet.cell(
            row=row,
            column=6,
            value="Details"
        )
        header_cell.alignment = Alignment(horizontal="center")

        row += 2

        # Keep track of rows that need to be formatted as percentages
        percent_rows: list[int] = []

        # ======================================
        # Envelope Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Envelope Loads"
        )

        # Keep track of starting row for percentage formatting
        start_row = row

        row = add_load_row(
            sheet,
            row,
            "Wall",
            heat.wall_btu,
            None,
            heat.wall_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Roof",
            heat.roof_btu,
            None,
            heat.roof_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Window",
            heat.window_btu,
            None,
            heat.window_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Skylight",
            heat.skylight_btu,
            None,
            heat.skylight_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Door",
            heat.door_btu,
            None,
            heat.door_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Floor",
            heat.floor_btu,
            None,
            heat.floor_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Interior Wall",
            heat.interior_wall_btu,
            None,
            heat.interior_wall_sqft,
            "sqft"
        )

        row = add_load_row(
            sheet,
            row,
            "Ceiling",
            heat.ceiling_btu,
            None,
            heat.ceiling_sqft,
            "sqft"
        )

        end_row = row - 1

        percent_rows.extend(
            range(
                start_row,
                end_row + 1
            )
        )

        subtotal_row = row

        row = add_subtotal_row(
            sheet,
            row,
            "Envelope Subtotal",
            start_row,
            end_row
        )

        percent_rows.append(
            subtotal_row
        )

        # ======================================
        # Internal Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Internal Loads"
        )

        start_row = row

        row = add_load_row(
            sheet,
            row,
            "People",
            heat.people_sensible_btu,
            heat.people_latent_btu,
            heat.people_count,
            "people"
        )

        row = add_load_row(
            sheet,
            row,
            "Infiltration",
            heat.infiltration_sensible_btu,
            heat.infiltration_latent_btu,
            heat.infiltration_cfm,
            "CFM"
        )

        row = add_load_row(
            sheet,
            row,
            "Misc Equipment",
            heat.misc_equipment_sensible_btu,
            heat.misc_equipment_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Air Energy Change",
            heat.air_energy_change_sensible_btu,
            heat.air_energy_change_latent_btu
        )

        end_row = row - 1

        percent_rows.extend(
            range(
                start_row,
                end_row + 1
            )
        )

        subtotal_row = row

        row = add_subtotal_row(
            sheet,
            row,
            "Internal Subtotal",
            start_row,
            end_row
        )

        percent_rows.append(
            subtotal_row
        )

        # ======================================
        # Equipment Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Equipment Loads"
        )

        start_row = row

        row = add_load_row(
            sheet,
            row,
            "Overhead Lighting",
            heat.overhead_lighting_btu,
            None,
            heat.overhead_lighting_watts,
            "W"
        )

        row = add_load_row(
            sheet,
            row,
            "Task Lighting",
            heat.task_lighting_btu,
            None,
            heat.task_lighting_watts,
            "W"
        )

        row = add_load_row(
            sheet,
            row,
            "Equipment",
            heat.equipment_btu,
            None,
            heat.equipment_watts,
            "W"
        )

        end_row = row - 1

        percent_rows.extend(
            range(
                start_row,
                end_row + 1
            )
        )

        subtotal_row = row

        row = add_subtotal_row(
            sheet,
            row,
            "Equipment Subtotal",
            start_row,
            end_row
        )

        percent_rows.append(
            subtotal_row
        )

        # ======================================
        # System Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "System / Airside Loads"
        )

        start_row = row

        row = add_load_row(
            sheet,
            row,
            "Zone Conditioning",
            heat.zone_conditioning_sensible_btu,
            heat.zone_conditioning_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Plenum Load",
            heat.plenum_load_sensible_btu,
            heat.plenum_load_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Return Fan Load",
            heat.return_fan_sensible_btu,
            heat.return_fan_latent_btu,
            heat.return_fan_cfm,
            "CFM"
        )

        row = add_load_row(
            sheet,
            row,
            "Ventilation Load",
            heat.ventilation_sensible_btu,
            heat.ventilation_latent_btu,
            heat.ventilation_cfm,
            "CFM"
        )

        row = add_load_row(
            sheet,
            row,
            "Supply Fan Load",
            heat.supply_fan_sensible_btu,
            heat.supply_fan_latent_btu,
            heat.return_fan_cfm,
            "CFM"
        )

        row = add_load_row(
            sheet,
            row,
            "Zone Fan Coil Fans",
            heat.zone_fan_coils_sensible_btu,
            heat.zone_fan_coils_latent_btu
        )

        end_row = row - 1

        percent_rows.extend(
            range(
                start_row,
                end_row + 1
            )
        )

        subtotal_row = row

        row = add_subtotal_row(
            sheet,
            row,
            "System Load Subtotal",
            start_row,
            end_row
        )

        percent_rows.append(
            subtotal_row
        )

        # ======================================
        # HAP Totals
        # ======================================

        start_row = row


        row = add_section_header(
            sheet,
            row,
            "HAP Totals"
        )

        row = add_load_row(
            sheet,
            row,
            "Total System Loads",
            heat.total_system_sensible_btu,
            heat.total_system_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Central Cooling Coil",
            heat.central_cooling_coil_sensible_btu,
            heat.central_cooling_coil_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Central Heating Coil",
            heat.central_heating_coil_sensible_btu,
            heat.central_heating_coil_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Total Conditioning",
            heat.total_conditioning_sensible_btu,
            heat.total_conditioning_latent_btu
        )

        end_row = row - 1

        percent_rows.extend(
            range(
                start_row,
                end_row + 1
            )
        )

        # ======================================
        # Grand Total
        # ======================================

        sheet.cell(
            row=row,
            column=1,
            value="Grand Total"
        )

        sheet.cell(
            row=row,
            column=4,
            value=f"=D{row - 3}"
        )

        sheet[
            f"A{row}"
        ].font = Font(bold=True)

        sheet[
            f"D{row}"
        ].font = Font(bold=True)

        # ======================================
        # % Total Formulas
        # ======================================

        for percent_row in percent_rows:

            # Skip merged rows
            if (
                sheet.cell(
                    row=percent_row,
                    column=5
                ).__class__.__name__
                == "MergedCell"
            ):
                continue

            sheet.cell(
                row=percent_row,
                column=5,
                value=(
                    f"=D{percent_row}"
                    f"/D{row}"
                )
            )

        format_sheet(sheet)

    workbook.save(Path(output_path))

    print("\nSaved workbook:")

    print(output_path)

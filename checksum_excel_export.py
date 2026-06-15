from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.styles import PatternFill

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
        end_column=5
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
    latent: float | None
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


def export_system_checksums(
    systems: dict[str, AirSystem],
    output_path: str | Path
) -> None:
    """
    Export checksum workbook.
    """

    workbook: Workbook = (
        Workbook()
    )

    workbook.remove(
        workbook.active
    )

    for system in systems.values():

        sheet = (
            workbook.create_sheet(
                title=(
                    system.name[:31]
                )
            )
        )

        heat = (
            system.heat_balance
        )

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
        # Loads Header
        # ======================================

        row = (
            add_section_header(
                sheet,
                row,
                "Cooling Loads"
            )
        )

        headers_row = row

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

        sheet.cell(
            row=row,
            column=5,
            value="% Total"
        )

        row += 2

        percent_rows: list[int] = []

        # ======================================
        # Envelope Loads
        # ======================================

        row = add_section_header(
            sheet,
            row,
            "Envelope Loads"
        )

        start_row = row

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
            heat.people_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Infiltration",
            heat.infiltration_sensible_btu,
            heat.infiltration_latent_btu
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
            None
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
            "Equipment",
            heat.equipment_btu,
            None
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
            heat.return_fan_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Ventilation Load",
            heat.ventilation_sensible_btu,
            heat.ventilation_latent_btu
        )

        row = add_load_row(
            sheet,
            row,
            "Supply Fan Load",
            heat.supply_fan_sensible_btu,
            heat.supply_fan_latent_btu
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

        # ======================================
        # Grand Total
        # ======================================

        grand_total_row = (
            row + 2
        )

        sheet.cell(
            row=grand_total_row,
            column=1,
            value="Grand Total"
        )

        sheet.cell(
            row=grand_total_row,
            column=4,
            value=(
                f"=D51"
            )
        )

        sheet[
            f"A{grand_total_row}"
        ].font = Font(
            bold=True
        )

        sheet[
            f"D{grand_total_row}"
        ].font = Font(
            bold=True
        )

        # ======================================
        # % Total Formulas
        # ======================================

        for percent_row in (
            percent_rows
        ):
            sheet.cell(
                row=percent_row,
                column=5,
                value=(
                    f"=D{percent_row}"
                    f"/D{51}"
                )
            )

        for percent_row in (
            [48, 49, 50, 51, 54]
        ):
            sheet.cell(
                row=percent_row,
                column=5,
                value=(
                    f"=D{percent_row}"
                    f"/D{51}"
                )
            )

        format_sheet(
            sheet
        )

    workbook.save(
        Path(output_path)
    )

    print(
        "\nSaved workbook:"
    )

    print(
        output_path
    )

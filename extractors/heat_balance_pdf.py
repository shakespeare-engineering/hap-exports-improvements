import re

from pathlib import Path
from pypdf import PdfReader

from models.air_system import AirSystem


def clean_number(value: str | None) -> float | None:
    try:
        return float(value) if value else None
    except Exception:
        return None


def extract_row_values(
    text: str,
    label: str
) -> tuple[float | None, float | None]:
    """
    Extract sensible + latent values
    from heat balance rows.
    """

    match = re.search(
        rf"^{re.escape(label)}\s+(-?[\d.]+)\s+(-?[\d.]+)",
        text,
        re.MULTILINE
    )

    return (
        clean_number(match.group(1)),
        clean_number(match.group(2))
    ) if match else (None, None)


def extract_detail_values(
    text: str,
    label: str
) -> tuple[
    float | None,
    float | None,
    float | None
]:
    """
    Extract cooling-side detail rows from
    Table 2.

    Examples:

    Exterior Wall Convection
    1269 sqft
    4916
    -

    Overhead Lighting Convection
    331 W
    501
    -

    Electric Equipment Convection
    1928 W
    4933
    -
    """

    match = re.search(
        rf"{re.escape(label)}\s+"
        rf"(\d+(?:\.\d+)?)\s*"
        rf"(sqft|W|CFM)?\s+"
        rf"(-?\d+(?:\.\d+)?)",
        text,
        re.MULTILINE
    )

    if not match:

        print(
            f"Could not find: {label}"
        )

        return (
            None,
            None,
            None
        )

    detail_value: float | None = clean_number(
        match.group(1)
    )

    detail_type: str | None = (
        match.group(2)
    )

    btu_value: float | None = clean_number(
        match.group(3)
    )

    sqft: float | None = (
        detail_value
        if detail_type == "sqft"
        else None
    )

    watts: float | None = (
        detail_value
        if detail_type == "W"
        else None
    )

    return (
        btu_value,
        sqft,
        watts
    )


def extract_heat_balance_pdf(
    pdf_path_str: str,
    systems: dict[str, AirSystem]
) -> None:

    pdf_path: Path = Path(pdf_path_str)

    print(
        f"\nReading heat balance PDF: "
        f"{pdf_path.name}"
    )

    reader: PdfReader = PdfReader(pdf_path)

    for page in reader.pages:

        text: str | None = page.extract_text()

        if not text:
            continue

        # ==================================================
        # Find system
        # ==================================================

        system_match = re.search(
            r"Air System Heat Balance Summary for (.+)",
            text
        )

        if not system_match:
            continue

        system_name: str = (
            system_match.group(1)
            .strip()
        )

        if system_name not in systems:

            print(
                f"System not found: "
                f"{system_name}"
            )

            continue

        system: AirSystem = systems[system_name]
        heat = system.heat_balance

        # ==================================================
        # Design Conditions
        # ==================================================

        cooling_match = re.search(
            r"DESIGN COOLING - ([A-Z]+ \d{2}:\d{2})",
            text
        )

        if cooling_match:
            heat.cooling_design_time = (
                cooling_match.group(1)
            )

        oa_match = re.search(
            r"OA DB / WB\s+"
            r"([\d.]+)\s+F\s*/\s*([\d.]+)\s+F"
            r".*?"
            r"OA DB / WB\s+"
            r"([\d.]+)\s+F\s*/\s*([\d.]+)\s+F",
            text,
            re.DOTALL
        )

        if oa_match:

            heat.cooling_oa_db_f = clean_number(
                oa_match.group(1)
            )

            heat.cooling_oa_wb_f = clean_number(
                oa_match.group(2)
            )

            heat.heating_oa_db_f = clean_number(
                oa_match.group(3)
            )

            heat.heating_oa_wb_f = clean_number(
                oa_match.group(4)
            )

        # ==================================================
        # Table 1 - System Loads
        # ==================================================

        (
            heat.zone_conditioning_sensible_btu,
            heat.zone_conditioning_latent_btu
        ) = extract_row_values(
            text,
            "Zone Conditioning"
        )

        (
            heat.plenum_load_sensible_btu,
            heat.plenum_load_latent_btu
        ) = extract_row_values(
            text,
            "Plenum Load"
        )

        (
            heat.return_fan_sensible_btu,
            heat.return_fan_latent_btu
        ) = extract_row_values(
            text,
            "Return Fan Load"
        )

        (
            heat.ventilation_sensible_btu,
            heat.ventilation_latent_btu
        ) = extract_row_values(
            text,
            "Ventilation Load"
        )

        (
            heat.supply_fan_sensible_btu,
            heat.supply_fan_latent_btu
        ) = extract_row_values(
            text,
            "Supply Fan Load"
        )

        (
            heat.zone_fan_coils_sensible_btu,
            heat.zone_fan_coils_latent_btu
        ) = extract_row_values(
            text,
            "Zone Fan Coil Fans Load"
        )

        (
            heat.total_system_sensible_btu,
            heat.total_system_latent_btu
        ) = extract_row_values(
            text,
            ">> Total System Loads"
        )

        (
            heat.central_cooling_coil_sensible_btu,
            heat.central_cooling_coil_latent_btu
        ) = extract_row_values(
            text,
            "Central Cooling Coil"
        )

        (
            heat.central_heating_coil_sensible_btu,
            heat.central_heating_coil_latent_btu
        ) = extract_row_values(
            text,
            "Central Heating Coil"
        )

        (
            heat.total_conditioning_sensible_btu,
            heat.total_conditioning_latent_btu
        ) = extract_row_values(
            text,
            ">> Total Conditioning"
        )

        # ==================================================
        # Table 2 - Zone Heat Balance
        # ==================================================

        (
            heat.wall_btu,
            heat.wall_sqft,
            heat.wall_watts
        ) = extract_detail_values(
            text,
            "Exterior Wall Convection"
        )

        (
            heat.roof_btu,
            heat.roof_sqft,
            heat.roof_watts
        ) = extract_detail_values(
            text,
            "Roof Convection"
        )

        (
            heat.window_btu,
            heat.window_sqft,
            heat.window_watts
        ) = extract_detail_values(
            text,
            "Window Convection"
        )

        (
            heat.skylight_btu,
            heat.skylight_sqft,
            heat.skylight_watts
        ) = extract_detail_values(
            text,
            "Skylight Convection"
        )

        (
            heat.door_btu,
            heat.door_sqft,
            heat.door_watts
        ) = extract_detail_values(
            text,
            "Door Convection"
        )

        (
            heat.floor_btu,
            heat.floor_sqft,
            heat.floor_watts
        ) = extract_detail_values(
            text,
            "Floor Convection"
        )

        (
            heat.interior_wall_btu,
            heat.interior_wall_sqft,
            heat.interior_wall_watts
        ) = extract_detail_values(
            text,
            "Interior Wall Convection"
        )

        (
            heat.ceiling_btu,
            heat.ceiling_sqft,
            heat.ceiling_watts
        ) = extract_detail_values(
            text,
            "Ceiling Convection"
        )

        (
            heat.overhead_lighting_btu,
            heat.overhead_lighting_sqft,
            heat.overhead_lighting_watts
        ) = extract_detail_values(
            text,
            "Overhead Lighting Convection"
        )

        (
            heat.task_lighting_btu,
            heat.task_lighting_sqft,
            heat.task_lighting_watts
        ) = extract_detail_values(
            text,
            "Task Lighting Convection"
        )

        (
            heat.equipment_btu,
            heat.equipment_sqft,
            heat.equipment_watts
        ) = extract_detail_values(
            text,
            "Electric Equipment Convection"
        )

        # This is broken TODO: Fix the extraction of people loads
        (
            heat.people_sensible_btu,
            heat.people_latent_btu
        ) = extract_row_values(
            text,
            "People Convection"
        )

        (
            heat.infiltration_sensible_btu,
            heat.infiltration_latent_btu
        ) = extract_row_values(
            text,
            "Infiltration"
        )

        (
            heat.misc_equipment_sensible_btu,
            heat.misc_equipment_latent_btu
        ) = extract_row_values(
            text,
            "Miscellaneous Equipment"
        )

        (
            heat.air_energy_change_sensible_btu,
            heat.air_energy_change_latent_btu
        ) = extract_row_values(
            text,
            "Air Internal Energy Change"
        )

        (
            heat.total_zone_sensible_btu,
            heat.total_zone_latent_btu
        ) = extract_row_values(
            text,
            ">> Total Zone Loads"
        )

    print(
        "Heat balance extraction complete."
    )
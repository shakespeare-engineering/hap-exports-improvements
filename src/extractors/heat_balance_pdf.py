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


def extract_system_load_values(
    text: str,
    label: str
) -> tuple[
    float | None,
    float | None,
    float | None
]:
    """
    Extract cooling sensible + latent and heating sensible
    values from Table 1.

    The heating tail is optional so that cooling extraction
    still succeeds on reports that lack a heating column.

    Args:
        text (str): Extracted text from the heat balance page.
        label (str): Row label to search for.

    Returns:
        tuple: (cooling_sensible, cooling_latent, heating_sensible),
            each None if not present.
    """

    pattern: str = (
        rf"^{re.escape(label)}\s+"
        rf"(?:[-\d.]+\s*(?:CFM|sqft|W)?\s+)?"
        rf"(-?\d+(?:\.\d+)?)\s+"                 # 1 cooling sensible
        rf"(-|-?\d+(?:\.\d+)?)"                  # 2 cooling latent
        rf"(?:\s+"                               # -- optional heating tail --
        rf"(?:[-\d.]+\s*(?:CFM|sqft|W)?\s+)?"
        rf"(-?\d+(?:\.\d+)?)\s+"                 # 3 heating sensible
        rf"(-|-?\d+(?:\.\d+)?))?"                # 4 heating latent
    )

    match = re.search(
        pattern,
        text,
        re.MULTILINE
    )

    if not match:
        return (
            None,
            None,
            None
        )

    sensible: float | None = clean_number(
        match.group(1)
    )

    latent_raw: str = (
        match.group(2)
    )

    latent: float | None = (
        0
        if latent_raw == "-"
        else clean_number(
            latent_raw
        )
    )

    heating_sensible: float | None = (
        clean_number(match.group(3))
        if match.group(3) is not None
        else None
    )

    return (
        sensible,
        latent,
        heating_sensible
    )


def extract_detail_values(
    text: str,
    label: str
) -> tuple[
    float | None,
    float | None,
    float | None,
    float | None
]:
    """
    Extract cooling-side detail rows and heating sensible
    from Table 2.

    The heating tail is optional so that cooling extraction
    still succeeds on reports that lack a heating column.

    Args:
        text (str): Extracted text from the heat balance page.
        label (str): Row label to search for.

    Returns:
        tuple: (cooling_btu, sqft, watts, heating_btu),
            each None if not present.
    """

    match = re.search(
        rf"{re.escape(label)}\s+"
        rf"(\d+(?:\.\d+)?)\s*"                          # 1 detail value
        rf"(sqft|W|CFM)?\s+"                            # 2 detail type
        rf"(-?\d+(?:\.\d+)?)"                           # 3 cooling sensible btu
        rf"(?:\s+(?:-|-?\d+(?:\.\d+)?)\s+"              # cooling latent (dash/num)
        rf"(?:\d+(?:\.\d+)?\s*(?:sqft|W|CFM)?\s+)?"     # heating detail (same units)
        rf"(-?\d+(?:\.\d+)?))?",                        # 4 heating sensible btu
        text,
        re.MULTILINE
    )

    if not match:
        return (
            None,
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

    heating_btu: float | None = (
        clean_number(match.group(4))
        if match.group(4) is not None
        else None
    )

    return (
        btu_value,
        sqft,
        watts,
        heating_btu
    )


def extract_table1CFM_values(
    text: str,
    label: str
) -> tuple[
    float | None,
    float | None,
    float | None,
    float | None
]:
    """
    Extract CFM + sensible + latent and heating sensible
    from Table 1 CFM rows.

    The heating tail is optional so that cooling extraction
    still succeeds on reports that lack a heating column.

    Args:
        text (str): Extracted text from the heat balance page.
        label (str): Row label to search for.

    Returns:
        tuple: (cfm, cooling_sensible, cooling_latent, heating_sensible),
            each None if not present.
    """

    match = re.search(
        rf"{re.escape(label)}\s+"
        rf"(\d+(?:\.\d+)?)\s*CFM\s+"             # 1 cfm
        rf"(-?\d+(?:\.\d+)?|-)\s+"               # 2 cooling sensible
        rf"(-?\d+(?:\.\d+)?|-)"                  # 3 cooling latent
        rf"(?:\s+\d+(?:\.\d+)?\s*CFM\s+"         # -- optional heating tail (same cfm) --
        rf"(-?\d+(?:\.\d+)?|-)\s+"               # 4 heating sensible
        rf"(-?\d+(?:\.\d+)?|-))?",               # 5 heating latent
        text,
        re.MULTILINE
    )

    if not match:
        return (
            None,
            None,
            None,
            None
        )

    cfm: float | None = clean_number(
        match.group(1)
    )

    sensible_raw: str = (
        match.group(2)
    )

    latent_raw: str = (
        match.group(3)
    )

    sensible: float | None = (
        None
        if sensible_raw == "-"
        else clean_number(
            sensible_raw
        )
    )

    latent: float | None = (
        None
        if latent_raw == "-"
        else clean_number(
            latent_raw
        )
    )

    heating_sensible_raw: str | None = (
        match.group(4)
    )

    heating_sensible: float | None = (
        None
        if heating_sensible_raw is None
        or heating_sensible_raw == "-"
        else clean_number(
            heating_sensible_raw
        )
    )

    return (
        cfm,
        sensible,
        latent,
        heating_sensible
    )


def extract_heat_balance_pdf(
    pdf_path_str: str,
    systems: dict[str, AirSystem]
) -> None:

    pdf_path: Path = Path(pdf_path_str)

    print(
        f"\nReading heat balance PDF:\n"
        f"  {pdf_path.name}"
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
                f"\n[WARNING] Skipping unmatched system:"
                f"\n  {system_name}"
            )

            continue

        system: AirSystem = systems[
            system_name
        ]

        heat = system.heat_balance

        missing_table1: list[str] = []
        missing_table2: list[str] = []

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
        # TABLE 1
        # ==================================================

        table1_rows = [
            ("Zone Conditioning", "zone_conditioning"),
            ("Plenum Load", "plenum_load"),
            ("Zone Fan Coil Fans Load", "zone_fan_coils"),
            (">> Total System Loads", "total_system"),
            ("Central Cooling Coil", "central_cooling_coil"),
            ("Central Heating Coil", "central_heating_coil"),
            (">> Total Conditioning", "total_conditioning")
        ]

        for label, attr in table1_rows:

            sensible, latent, heating_sensible = (
                extract_system_load_values(
                    text,
                    label
                )
            )

            setattr(
                heat,
                f"{attr}_sensible_btu",
                sensible
            )

            setattr(
                heat,
                f"{attr}_latent_btu",
                latent
            )

            setattr(
                heat,
                f"{attr}_heating_sensible_btu",
                heating_sensible
            )

            if (
                sensible is None
                and latent is None
            ):
                missing_table1.append(
                    label
                )

        cfm_rows = [
            ("Return Fan Load", "return_fan"),
            ("Ventilation Load", "ventilation"),
            ("Supply Fan Load", "supply_fan")
        ]

        for label, attr in cfm_rows:

            cfm, sensible, latent, heating_sensible = (
                extract_table1CFM_values(
                    text,
                    label
                )
            )

            setattr(
                heat,
                f"{attr}_cfm",
                cfm
            )

            setattr(
                heat,
                f"{attr}_sensible_btu",
                sensible
            )

            setattr(
                heat,
                f"{attr}_latent_btu",
                latent
            )

            setattr(
                heat,
                f"{attr}_heating_sensible_btu",
                heating_sensible
            )

            if (
                cfm is None
                and sensible is None
            ):
                missing_table1.append(
                    label
                )

        # ==================================================
        # TABLE 2
        # ==================================================

        detail_rows = [
            ("Exterior Wall Convection", "wall"),
            ("Roof Convection", "roof"),
            ("Window Convection", "window"),
            ("Skylight Convection", "skylight"),
            ("Door Convection", "door"),
            ("Floor Convection", "floor"),
            ("Interior Wall Convection", "interior_wall"),
            ("Ceiling Convection", "ceiling"),
            ("Overhead Lighting Convection", "overhead_lighting"),
            ("Task Lighting Convection", "task_lighting"),
            ("Electric Equipment Convection", "equipment")
        ]

        for label, attr in detail_rows:

            btu, sqft, watts, heating_btu = (
                extract_detail_values(
                    text,
                    label
                )
            )

            setattr(
                heat,
                f"{attr}_btu",
                btu
            )

            setattr(
                heat,
                f"{attr}_sqft",
                sqft
            )

            setattr(
                heat,
                f"{attr}_watts",
                watts
            )

            setattr(
                heat,
                f"{attr}_heating_sensible_btu",
                heating_btu
            )

            if btu is None:
                missing_table2.append(
                    label
                )

        # ==================================================
        # People
        # ==================================================

        people_match = re.search(
            r"People Convection\s+"
            r"(\d+(?:\.\d+)?)\s+"                    # 1 people count
            r"(-?\d+(?:\.\d+)?)\s+"                  # 2 cooling sensible
            r"(-?\d+(?:\.\d+)?)"                     # 3 cooling latent
            r"(?:\s+(-?\d+(?:\.\d+)?)\s+"            # heating count (ignored)
            r"(-?\d+(?:\.\d+)?))?",                  # 5 heating sensible
            text,
            re.MULTILINE
        )

        if people_match:

            heat.people_count = (
                clean_number(
                    people_match.group(1)
                )
            )

            heat.people_sensible_btu = (
                clean_number(
                    people_match.group(2)
                )
            )

            heat.people_heating_sensible_btu = (
                clean_number(people_match.group(5))
                if people_match.group(5) is not None
                else None
            )

            heat.people_latent_btu = (
                clean_number(
                    people_match.group(3)
                )
            )

        # ==================================================
        # Clean Debug Output
        # ==================================================

        if (
            missing_table1
            or
            missing_table2
        ):

            print(
                f"\n[WARNING] Heat balance incomplete:"
                f"\n  System: {system.name}"
            )

            if missing_table1:

                print(
                    "\n  Missing Table 1:"
                )

                for item in missing_table1:
                    print(
                        f"    • {item}"
                    )

            if missing_table2:

                print(
                    "\n  Missing Table 2:"
                )

                for item in missing_table2:
                    print(
                        f"    • {item}"
                    )

    print(
        "\nHeat balance extraction complete."
    )

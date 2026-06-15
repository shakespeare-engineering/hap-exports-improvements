import re

from pathlib import Path
from pypdf import PdfReader

from models.air_system import AirSystem


def clean_number(value):
    try:
        return float(value)
    except:
        return None


def normalize_name(text: str) -> str:
    return (
        text.upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("/", "")
    )


def extract_ventilation_pdf(pdf_path_str: str,systems: dict[str, AirSystem]):

    pdf_path = Path(pdf_path_str)

    print(
        f"\nReading ventilation PDF: "
        f"{pdf_path.name}"
    )

    reader = PdfReader(pdf_path)

    for page in reader.pages:

        text = page.extract_text()

        if not text:
            continue

        # ==================================================
        # Find system name
        # ==================================================

        system_match = re.search(
            r"Ventilation Sizing Summary for (.+)",
            text
        )

        if not system_match:
            continue

        system_name = system_match.group(1).strip()

        if system_name not in systems:
            print(
                f"System not found: "
                f"{system_name}"
            )
            continue

        system = systems[system_name]

        # ==================================================
        # Project Name
        # ==================================================

        project_match = re.search(
            r"Project:\s+(.+?)\s+\d{2}/\d{2}/\d{4}",
            text
        )

        if project_match:

            system.project_name = (
                project_match.group(1)
                .strip()
            )

        # ==================================================
        # System Ventilation Airflow
        # ==================================================

        design_match = re.search(
            r"Design Ventilation Airflow Rate\s+([\d.]+)\s+CFM",
            text
        )

        corrected_match = re.search(
            r"Corrected for Exhaust Air\s+([\d.]+)\s+CFM",
            text
        )

        system.ventilation.design_oa_cfm = (
            clean_number(
                design_match.group(1)
            )
            if design_match
            else None
        )

        system.ventilation.corrected_oa_cfm = (
            clean_number(
                corrected_match.group(1)
            )
            if corrected_match
            else system.ventilation.design_oa_cfm
        )

        # ==================================================
        # Space Ventilation Rows
        # ==================================================

        space_matches = re.findall(
            r"([A-Za-z0-9/\-\(\) ]+)\s+"
            r"([\d.]+)\s+"
            r"([\d.]+)\s+"
            r"([\d.]+)\s+"
            r"([\d.]+)\s+"
            r"([\d.]+)\s+"
            r"[\d.]+\s+"
            r"[\d.]+\s+"
            r"[\d.]+\s+"
            r"([\d.]+)\s+"
            r"([\d.]+)",
            text
        )

        for match in space_matches:

            space_name = match[0].strip()

            # Skip system header/totals rows
            if (
                normalize_name(space_name)
                == normalize_name(system_name)
                or "TOTALS" in space_name.upper()
            ):
                continue

            # ==================================================
            # Find matching space
            # ==================================================

            matching_space = None

            for zone in system.zones:

                matching_space = next(
                    (
                        space
                        for space in zone.spaces
                        if (
                            normalize_name(space.name)
                            ==
                            normalize_name(space_name)
                        )
                    ),
                    None
                )

                if matching_space:
                    break

            if matching_space is None:

                print(
                    f"Space not found in "
                    f"{system.name}: "
                    f"{space_name}"
                )

                continue

            # ==================================================
            # Ventilation Data
            # ==================================================

            matching_space.maximum_occupants = clean_number(match[2])

            matching_space.supply_airflow_cfm = clean_number(match[3])

            matching_space.oa_per_person = clean_number(match[4])

            matching_space.oa_per_sqft = clean_number(match[5])

            matching_space.uncorrected_oa_cfm = clean_number(match[6])

            matching_space.direct_exhaust_cfm = clean_number(match[7])

    print(
        "Ventilation PDF extraction complete."
    )
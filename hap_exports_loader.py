from pathlib import Path

from extractors.system_sizing_excel import (
    extract_system_sizing_excel,
)
from extractors.zone_sizing_excel import (
    extract_zone_sizing_excel,
)
from extractors.ventilation_pdf import (
    extract_ventilation_pdf,
)
from extractors.heat_balance_pdf import (
    extract_heat_balance_pdf,
)

from models.air_system import AirSystem
from ventilationPDFTesting import print_dataclass


def find_file(directory: Path,pattern: str,description: str) -> Path:
    """
    Find a file matching pattern.
    The description is used for error messages.
    """

    matches: list[Path] = list(directory.glob(pattern))

    if not matches:
        raise FileNotFoundError(
            f"Could not find "
            f"{description}\n"
            f"Expected pattern:\n"
            f"{pattern}\n"
            f"Inside:\n"
            f"{directory}"
        )

    if len(matches) > 1:
        print(
            f"\nWarning: Multiple "
            f"{description} files found."
        )

        for file in matches:
            print(
                f"  - {file.name}"
            )

        print(
            f"Using: "
            f"{matches[0].name}"
        )

    return matches[0]


# Not fully cleaned up
def find_latest_hap_export_folder(project_directory: Path) -> Path:
    """
    Find newest *_Hap Exports folder.
    """

    export_folders: list[Path] = [
        folder
        for folder in (
            project_directory.iterdir()
        )
        if (
            folder.is_dir()
            and folder.name.endswith(
                "_HAP Exports"
            )
        )
    ]

    if not export_folders:

        raise FileNotFoundError(
            f"No *_HAP Exports "
            f"folder found in:\n"
            f"{project_directory}"
        )

    return max(
        export_folders,
        key=lambda folder:
        folder.stat().st_mtime
    )


def load_hap_exports(project_directory_str: str) -> dict[str, AirSystem]:
    """
    Automatically find and load
    all HAP export files.

    Expected structure:

    Project Folder/
    ├── *_SysSizingSummary.xlsx
    ├── *_ZoneSizingSummary.xlsx
    └── *_Hap Exports/
        ├── *_VentilationSizingSummary.pdf
        └── *_HeatBalanceSummary.pdf
    """

    project_directory: Path = Path(project_directory_str)

    if not project_directory.exists():

        raise FileNotFoundError(f"Directory not found:\n"f"{project_directory}")

    # ==========================================
    # Find newest HAP export folder
    # ==========================================

    hap_export_folder: Path = (find_latest_hap_export_folder(project_directory))

    print(
        f"\nUsing HAP folder:\n"
        f"{hap_export_folder.name}"
    )

    # ==========================================
    # Find files
    # ==========================================

    system_excel: Path = find_file(
        project_directory,
        "*SysSizingSummary.xlsx",
        "System Sizing Excel"
    )

    zone_excel: Path = find_file(
        project_directory,
        "*ZoneSizingSummary.xlsx",
        "Zone Sizing Excel"
    )

    ventilation_pdf: Path = find_file(
        hap_export_folder,
        "*VentilationSizingSummary.pdf",
        "Ventilation PDF"
    )

    heat_balance_pdf: Path = find_file(
        hap_export_folder,
        "*HeatBalanceSummary.pdf",
        "Heat Balance PDF"
    )

    # ==========================================
    # Print found files
    # ==========================================

    print("\nFound files:")

    print(
        f"  System Excel: "
        f"{system_excel.name}"
    )

    print(
        f"  Zone Excel: "
        f"{zone_excel.name}"
    )

    print(
        f"  Ventilation PDF: "
        f"{ventilation_pdf.name}"
    )

    print(
        f"  Heat Balance PDF: "
        f"{heat_balance_pdf.name}"
    )

    # ==========================================
    # Run extractors
    # ==========================================

    systems: dict[str, AirSystem] = (extract_system_sizing_excel(str(system_excel)))

    extract_zone_sizing_excel(str(zone_excel), systems)

    extract_ventilation_pdf(str(ventilation_pdf), systems)

    extract_heat_balance_pdf(str(heat_balance_pdf), systems)

    print(
        "\nAll HAP extraction "
        f"complete."
    )

    return systems

def main() -> None:

    project_directory: str = (
        input("Drag project folder here: ")
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    systems: dict[str, AirSystem] = (load_hap_exports(project_directory))

    # Debug print the first system from ventilation testing
    first_system: AirSystem = next(iter(systems.values()))
    print_dataclass(first_system)

    # Additional testing
    # print(first_system.heat_balance)


if __name__ == "__main__":
    main()
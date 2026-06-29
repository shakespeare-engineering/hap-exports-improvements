from pathlib import Path

from hap_exports_loader import (
    load_hap_exports
)

from checksum_excel_export import (
    export_system_checksums
)

from models.air_system import (
    AirSystem
)


def main() -> None:
    """
    Load HAP exports and generate
    checksum workbook.
    """

    # ==========================================
    # Get project folder
    # ==========================================

    project_directory: str = (
        input(
            "Drag project folder here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    project_path: Path = Path(
        project_directory
    )

    # ==========================================
    # Load HAP exports
    # ==========================================

    systems: dict[
        str,
        AirSystem
    ] = load_hap_exports(
        project_directory
    )

    # ==========================================
    # Output path
    # ==========================================

    output_file: Path = (
        project_path
        / "System Checksums.xlsx"
    )

    # ==========================================
    # Export workbook
    # ==========================================

    export_system_checksums(
        systems=systems,
        output_path=output_file
    )

    print(
        "\nDone."
    )

    input(
        "\nPress Enter to close..."
    )


if __name__ == "__main__":
    main()
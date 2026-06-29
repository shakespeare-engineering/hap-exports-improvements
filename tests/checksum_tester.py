import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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
    # Export workbook
    # ==========================================

    export_system_checksums(
        systems=systems,
        output_directory=project_path
    )

    print(
        "\nDone."
    )

    input(
        "\nPress Enter to close..."
    )


if __name__ == "__main__":
    main()
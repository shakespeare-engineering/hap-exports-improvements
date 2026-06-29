import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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
    extract_heat_balance_pdf
)


from print_utils import print_dataclass


def main() -> None:

    system_excel: str = (
        input(
            "Drag System Sizing Excel here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    zone_excel: str = (
        input(
            "Drag Zone Sizing Excel here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    ventilation_pdf: str = (
        input(
            "Drag Ventilation PDF here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    heat_balance_pdf: str = (
        input(
            "Drag Heat Balance PDF here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    # ==================================================
    # Extraction
    # ==================================================

    systems: dict = (
        extract_system_sizing_excel(
            system_excel
        )
    )

    extract_zone_sizing_excel(
        zone_excel,
        systems
    )

    extract_ventilation_pdf(
        ventilation_pdf,
        systems
    )

    extract_heat_balance_pdf(
        heat_balance_pdf,
        systems
    )

    # ==================================================
    # Print first system
    # ==================================================

    if systems:

        first_system = next(
            iter(systems.values())
        )

        print(
            "\n" + "=" * 80
        )

        print(
            "FIRST SYSTEM "
            "FULL DATA"
        )

        print("=" * 80)

        print_dataclass(
            first_system
        )


if __name__ == "__main__":
    main()
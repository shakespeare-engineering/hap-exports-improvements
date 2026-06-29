from dataclasses import fields, is_dataclass

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


def format_value(value) -> str:
    """
    Make printed numbers easier to read.
    """

    if isinstance(value, float):

        if value.is_integer():
            return str(int(value))

        return f"{value:.2f}"

    return str(value)


def print_dataclass(
    obj,
    indent: int = 0
) -> None:
    """
    Recursively print populated dataclass data.
    """

    spacing: str = "    " * indent

    if not is_dataclass(obj):

        print(
            f"{spacing}"
            f"{format_value(obj)}"
        )

        return

    print(
        f"{spacing}"
        f"{obj.__class__.__name__}:"
    )

    for field in fields(obj):

        value = getattr(
            obj,
            field.name
        )

        # Skip empty values
        if value is None:
            continue

        # Skip empty lists
        if isinstance(value, list) and not value:
            continue

        # Nested list
        if isinstance(value, list):

            print(
                f"{spacing}  "
                f"{field.name}: "
                f"{len(value)} item(s)"
            )

            for item in value:

                print_dataclass(
                    item,
                    indent + 2
                )

        # Nested dataclass
        elif is_dataclass(value):

            print(
                f"{spacing}  "
                f"{field.name}:"
            )

            print_dataclass(
                value,
                indent + 2
            )

        # Normal value
        else:

            print(
                f"{spacing}  "
                f"{field.name}: "
                f"{format_value(value)}"
            )


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
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


def print_dataclass(obj, indent=0) -> None:
    """
    Recursively print all populated data
    from dataclasses.
    """

    spacing = "    " * indent

    # Non-dataclass object
    if not is_dataclass(obj):
        print(f"{spacing}{obj}")
        return

    print(
        f"{spacing}"
        f"{obj.__class__.__name__}:"
    )

    for field in fields(obj):

        value = getattr(obj, field.name)

        # Skip empty values
        if value is None:
            continue

        # Lists (zones, spaces, etc.)
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

        # Nested dataclasses
        elif is_dataclass(value):

            print(
                f"{spacing}  "
                f"{field.name}:"
            )

            print_dataclass(
                value,
                indent + 2
            )

        # Normal values
        else:

            print(
                f"{spacing}  "
                f"{field.name}: "
                f"{value}"
            )


def main() -> None:

    system_excel = (
        input(
            "Drag System Sizing Excel here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    zone_excel = (
        input(
            "Drag Zone Sizing Excel here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    ventilation_pdf = (
        input(
            "Drag Ventilation PDF here: "
        )
        .strip()
        .strip('"')
        .replace("& ", "")
        .replace("'", "")
    )

    # ==================================================
    # Extraction
    # ==================================================

    systems = extract_system_sizing_excel(
        system_excel
    )

    extract_zone_sizing_excel(
        zone_excel,
        systems
    )

    extract_ventilation_pdf(
        ventilation_pdf,
        systems
    )

    # ==================================================
    # Print first system
    # ==================================================

    if systems:

        first_system = next(
            iter(systems.values())
        )

        print("\n" + "=" * 80)
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
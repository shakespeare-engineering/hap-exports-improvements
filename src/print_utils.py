from dataclasses import fields, is_dataclass


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

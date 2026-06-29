import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extractors.zone_sizing_excel import (
    extract_zone_sizing_excel
)


def main() -> None:

    excel_path = input(
        "Drag Zone Sizing Excel here: "
    ).strip().removeprefix("& ").strip("'").strip('"')

    zones = extract_zone_sizing_excel(
        excel_path
    )

    print("\n==========================")
    print("ZONE SUMMARY")
    print("==========================")

    for zone_name, zone in zones.items():

        print("\n--------------------------")
        print(zone)

        print(
            f"System Name: "
            f"{zone.system_name}"
        )

        print(
            f"Alternative Name: "
            f"{zone.alternative_name}"
        )

        print(
            f"Floor Area: "
            f"{zone.floor_area_sqft}"
        )

        # Cooling
        print("\nCooling")

        print(
            f"  Total MBH: "
            f"{zone.cooling_total_mbh}"
        )

        print(
            f"  Sensible MBH: "
            f"{zone.cooling_sensible_mbh}"
        )

        print(
            f"  Latent MBH: "
            f"{zone.cooling_latent_mbh}"
        )

        print(
            f"  Airflow: "
            f"{zone.design_supply_airflow_cfm}"
        )

        print(
            f"  Peak Time: "
            f"{zone.cooling_peak_time}"
        )

        print(
            f"  CFM/sqft: "
            f"{zone.cooling_cfm_per_sqft}"
        )

        # Spaces
        print("\nSpaces")

        print(
            f"  Count: "
            f"{len(zone.spaces)}"
        )

        for space in zone.spaces:

            print(
                f"\n  Space: "
                f"{space.name}"
            )

            print(
                f"    Floor Area: "
                f"{space.floor_area_sqft}"
            )

            print(
                f"    Sensible MBH: "
                f"{space.cooling_sensible_mbh}"
            )

            print(
                f"    Latent MBH: "
                f"{space.cooling_latent_mbh}"
            )

            print(
                f"    Total MBH: "
                f"{space.cooling_total_mbh}"
            )

            print(
                f"    Airflow: "
                f"{space.supply_airflow_cfm}"
            )

            print(
                f"    Peak Time: "
                f"{space.cooling_peak_time}"
            )

        # Optional:
        # Uncomment to limit output
        # break

    print("\nDone!")


if __name__ == "__main__":
    main()
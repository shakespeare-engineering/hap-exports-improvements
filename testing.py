from extractors.system_sizing_excel import (
    extract_system_sizing_excel
)


def main() -> None:

    excel_path = input(
    "Drag System Sizing Excel here: "
).strip().removeprefix("& ").strip("'").strip('"')

    systems = extract_system_sizing_excel(
        excel_path
    )

    print("\n==========================")
    print("SYSTEM SUMMARY")
    print("==========================")

    for system_name, system in systems.items():

        print("\n--------------------------")
        print(system)

        print(
            f"Equipment Type: "
            f"{system.equipment_class}"
        )

        print(
            f"System Type: "
            f"{system.system_type}"
        )

        # Cooling coil
        print("\nCooling Coil")

        print(
            f"  Total MBH: "
            f"{system.cooling_coil.total_load_mbh}"
        )

        print(
            f"  Sensible MBH: "
            f"{system.cooling_coil.sensible_load_mbh}"
        )

        print(
            f"  Airflow: "
            f"{system.cooling_coil.airflow_cfm}"
        )

        print(
            f"  Peak Time: "
            f"{system.cooling_coil.peak_time}"
        )

        # Heating coil
        print("\nHeating Coil")

        print(
            f"  Load MBH: "
            f"{system.heating_coil.total_load_mbh}"
        )

        print(
            f"  Airflow: "
            f"{system.heating_coil.airflow_cfm}"
        )

        # Supply fan
        print("\nSupply Fan")

        print(
            f"  Airflow: "
            f"{system.supply_fan.airflow_cfm}"
        )

        print(
            f"  BHP: "
            f"{system.supply_fan.fan_bhp}"
        )

        print(
            f"  kW: "
            f"{system.supply_fan.fan_kw}"
        )

    print("\nDone!")


if __name__ == "__main__":
    main()
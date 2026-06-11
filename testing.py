from models.air_system import AirSystem
from models.zone import Zone
from models.space import Space


def main() -> None:

    # Create system
    rtu_101 = AirSystem(name="RTU - 101")

    rtu_101.cooling_tons = 2.4
    rtu_101.supply_airflow_cfm = 1659
    rtu_101.fan_bhp = 0.91

    # Create zone
    office_zone = Zone(name="OFFICE")

    office_zone.design_supply_airflow_cfm = 332
    office_zone.floor_area_sqft = 774

    # Create spaces
    sales_office = Space(name="119-SALES OFFICE")
    sales_office.floor_area_sqft = 109.9
    sales_office.cooling_airflow_cfm = 44

    gm_office = Space(name="122-GM OFFICE")
    gm_office.floor_area_sqft = 87.4
    gm_office.cooling_airflow_cfm = 39

    # Add spaces to zone
    office_zone.add_space(sales_office)
    office_zone.add_space(gm_office)

    # Add zone to RTU
    rtu_101.add_zone(office_zone)

    # Print results
    print(rtu_101)

    print()

    for zone in rtu_101.zones:
        print(f"Zone: {zone.name}")

        for space in zone.spaces:
            print(
                f"    {space.name} | "
                f"{space.floor_area_sqft} sqft | "
                f"{space.cooling_airflow_cfm} CFM"
            )


if __name__ == "__main__":
    main()
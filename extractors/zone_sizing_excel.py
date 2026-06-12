from pathlib import Path

import pandas as pd

from models.air_system import AirSystem
from models.zone import Zone
from models.space import Space


def clean_value(value):
    """
    Convert pandas NaN values to None.
    """
    return None if pd.isna(value) else value


def extract_zone_sizing_excel(excel_path_str: str, systems: dict[str, AirSystem]) -> None:
    """
    Extract Zone objects from a
    HAP Zone Sizing Summary Excel export.
    """

    excel_path: Path = Path(excel_path_str)

    if not excel_path.exists():
        raise FileNotFoundError(
            f"Excel file not found: {excel_path}"
        )

    print(f"\nReading: {excel_path.name}")

    zones: dict[str, Zone] = {}

    # ==================================================
    # Zone-Air-Terminal-Sizing
    # ==================================================

    terminal_dataframe: pd.DataFrame = pd.read_excel(
        excel_path,
        sheet_name="Zone-Air-Terminal-Sizing",
        header=1
    )

    print("\nZone-Air-Terminal-Sizing columns found:")
    print(terminal_dataframe.columns.tolist())

    for _, row in terminal_dataframe.iterrows():

        zone_name: str = row.get("Zone Name")

        if pd.isna(zone_name):
            continue
        
        # Convert zone name to string if it's not already.
        zone_name = str(zone_name)

        if zone_name not in zones:
            # Create a new zone if it doesn't exist
            zones[zone_name] = Zone(name=zone_name)

        # Get the zone object from the dictionary
        zone: Zone = zones[zone_name]

        # General
        zone.floor_area_sqft = clean_value(row.get("Zone Floor Area (sqft)"))
        zone.system_name = clean_value(row.get("System Name"))
        zone.alternative_name = clean_value(row.get("Alternative Name"))

        # Terminal extraction not implemented.

        # Airflow
        zone.design_supply_airflow_cfm = clean_value(row.get("Design Supply Airflow (CFM)"))
        zone.minimum_supply_airflow_cfm = clean_value(row.get("Minimum Supply Airflow (CFM)"))
        zone.cooling_cfm_per_sqft = clean_value(row.get("CFM/sqft"))

        # Heating sizing    Shouldn't be used, I think
        # zone.heating_load_mbh = clean_value(row.get("Heating Load (MBH)"))
        # zone.heating_airflow_cfm = clean_value(row.get("Heating Airflow (CFM)"))

        # Ventilation    Shouldn't be used, I think
        # zone.breathing_zone_oa_cfm = clean_value(row.get("Breathing Zone OA (CFM)"))
        # zone.adjusted_zone_oa_cfm = clean_value(row.get("Adjusted Zone OA (CFM)"))

    # ==================================================
    # Zone-Loads
    # ==================================================

    zone_loads_dataframe: pd.DataFrame = pd.read_excel(
        excel_path,
        sheet_name="Zone-Loads",
        header=1
    )

    print("\nZone-Loads columns found:")
    print(zone_loads_dataframe.columns.tolist())

    for _, row in zone_loads_dataframe.iterrows():

        zone_name: str = row.get("Zone Name")

        if pd.isna(zone_name):
            continue

        zone_name = str(zone_name)

        if zone_name not in zones:
            zones[zone_name] = Zone(name=zone_name)

        zone: Zone = zones[zone_name]

        # Only update fields if they are not already set
        if zone.floor_area_sqft is None:
            zone.floor_area_sqft = clean_value(row.get("Zone Floor Area (sqft)"))

        if zone.cooling_cfm_per_sqft is None:
            zone.cooling_cfm_per_sqft = clean_value(row.get("CFM/sqft"))

        if zone.cooling_peak_time is None:
            zone.cooling_peak_time = clean_value(row.get("Time of Peak Sensible Clg Load"))
        
        # Cooling load
        zone.cooling_sensible_mbh = clean_value(row.get("Peak Sensible Clg Load (BTU/hr)"))/1000.0
        zone.cooling_latent_mbh = clean_value(row.get("Latent Clg Load (BTU/hr)"))/1000.0
        zone.cooling_peak_time = clean_value(row.get("Time of Peak Sensible Clg Load")) 
        zone.cooling_total_mbh =  zone.cooling_sensible_mbh + zone.cooling_latent_mbh

        # Occ. Clg Setpoint (F) not implemented


    # ==================================================
    # Space-Loads
    # ==================================================

    space_dataframe: pd.DataFrame = pd.read_excel(
        excel_path,
        sheet_name="Space-Loads",
        header=1
    )

    print("\nSpace-Loads columns found:")
    print(space_dataframe.columns.tolist())

    for _, row in space_dataframe.iterrows():

        zone_name: str = row.get("Zone Name")
        space_name: str = row.get("Space Name")

        if pd.isna(zone_name) or pd.isna(space_name):
            continue

        zone_name = str(zone_name)

        if zone_name not in zones:
            zones[zone_name] = Zone(name=zone_name)

        zone: Zone = zones[zone_name]

        space = Space(name=str(space_name))

        # General
        space.floor_area_sqft = clean_value(row.get("Space Floor Area (sqft)"))
        space.alternative_name = clean_value(row.get("Alternative Name"))
        space.system_name = clean_value(row.get("System Name"))
        space.zone_name = zone_name

        # Cooling
        space.cooling_sensible_mbh = clean_value(row.get("Peak Sensible Clg Load (BTU/hr)"))/1000.0
        space.cooling_latent_mbh = clean_value(row.get("Latent Clg Load (BTU/hr)"))/1000.0
        space.cooling_peak_time = clean_value(row.get("Time of Peak Sensible Clg Load"))
        space.cooling_cfm_per_sqft = clean_value(row.get("CFM/sqft"))
        space.cooling_total_mbh = (space.cooling_sensible_mbh+ space.cooling_latent_mbh)

        # Heating
        space.heating_sensible_mbh = clean_value(row.get("Peak Sensible Htg Load (BTU/hr)"))/1000.0

        # Airflow
        space.supply_airflow_cfm = clean_value(row.get("Supply Airflow Rate (CFM)"))

        # Occ. stuff not implemented

        zone.add_space(space)

    # ==================================================
    # Attach zones to systems
    # ==================================================

    attached_count = 0

    for zone in zones.values():

        if not zone.system_name:
            continue

        system = systems.get(zone.system_name)

        if system is None:
            print(
                f"System not found for zone: "
                f"{zone.name} "
                f"({zone.system_name})"
            )
            continue

        system.add_zone(zone)
        attached_count += 1

    print(f"\nLoaded {len(zones)} zones.")
    print(f"Attached {attached_count} zones to systems.")

    print("\nZone extraction complete.")
from pathlib import Path

# Excel library
import pandas as pd

from models.air_system import AirSystem

def clean_value(value):
    """
    Convert pandas NaN values to None.
    """
    return None if pd.isna(value) else value


def extract_system_sizing_excel(excel_path_str: str) -> dict[str, AirSystem]:
    """
    Extract AirSystem objects from a
    HAP System Sizing Summary Excel export.
    """

    excel_path: Path = Path(excel_path_str)

    if not excel_path.exists():
        raise FileNotFoundError(
            f"Excel file not found: {excel_path}"
        )

    print(f"\nReading: {excel_path.name}")

    # Read first worksheet
    dataframe: pd.DataFrame = pd.read_excel(
        excel_path,
        sheet_name=0,
        header=2
    )

    print("\nColumns found:")
    print(dataframe.columns.tolist())

    systems: dict[str, AirSystem] = {}

    # Iterate rows
    for _, row in dataframe.iterrows():

        system_name = row["System Name"]

        # Skip blank rows
        if pd.isna(system_name):
            continue

        # Create AirSystem
        system: AirSystem = AirSystem(name=str(system_name))

        # ==================================================
        # General System Info
        # ==================================================

        system.equipment_class = clean_value(row.get("Equipment Type"))
        system.system_type = clean_value(row.get("System Type"))
        system.floor_area_sqft = clean_value(row.get("Total Floor Area (sqft)"))
        system.number_of_zones = clean_value(row.get("Number of Zones"))

        # ==================================================
        # Cooling Coil
        # ==================================================

        system.cooling_coil.total_load_mbh = clean_value(row.get("Total Coil Load (MBH)"))
        system.cooling_coil.sensible_load_mbh = clean_value(row.get("Sensible Coil Load (MBH)"))
        system.cooling_coil.latent_load_mbh = clean_value(row.get("Latent Coil Load (MBH)"))
        system.cooling_coil.airflow_cfm = clean_value(row.get("Coil Airflow at Peak Time (CFM)"))
        system.cooling_coil.max_airflow_cfm = clean_value(row.get("Sum of Peak Zone Airflows (CFM)"))
        system.cooling_coil.water_flow_gpm = clean_value(row.get("Coil Water Flow Rate (gpm)"))
        system.cooling_coil.peak_time = clean_value(row.get("Time of Peak Coil Load"))
        system.cooling_coil.entering_db_f = clean_value(row.get("Coil Entering DB (F)"))
        system.cooling_coil.entering_wb_f = clean_value(row.get("Coil Entering WB (F)"))
        system.cooling_coil.leaving_db_f = clean_value(row.get("Coil Leaving DB (F)"))
        system.cooling_coil.leaving_wb_f = clean_value(row.get("Coil Leaving WB (F)"))

        # ==================================================
        # Heating Coil
        # ==================================================

        system.heating_coil.total_load_mbh = clean_value(row.get("Peak Coil Load (MBH)"))
        system.heating_coil.airflow_cfm = clean_value(row.get("Coil Airflow at Peak Time (CFM)"))
        system.heating_coil.max_airflow_cfm = clean_value(row.get("Max Coil Airflow (CFM)"))
        system.heating_coil.water_flow_gpm = clean_value(row.get("Coil Water Flow Rate (gpm)"))
        system.heating_coil.peak_time = clean_value(row.get("Time of Peak Coil Load"))
        system.heating_coil.entering_db_f = clean_value(row.get("Coil Entering DB (F)"))
        system.heating_coil.leaving_db_f = clean_value(row.get("Coil Leaving DB (F)"))

        # ==================================================
        # Supply Fan
        # ==================================================

        system.supply_fan.airflow_cfm = clean_value(row.get("Coil Airflow at Peak Time (CFM)"))
        system.supply_fan.fan_bhp = clean_value(row.get("Fan BHP"))
        system.supply_fan.fan_kw = clean_value(row.get("Fan Motor kW"))
        system.supply_fan.cfm_per_sqft = clean_value(row.get("Fan Motor kW"))

        # ==================================================
        # Store System
        # ==================================================

        systems[system.name] = system

    print(
        f"\nLoaded "
        f"{len(systems)} air systems."
    )

    return systems
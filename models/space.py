from dataclasses import dataclass

# Note: @dataclass helps in automatically generating special methods like __init__, __repr__, and __eq__ for the class.
@dataclass
class Space:
    """
    Represents a single HAP space/room.
    """

    name: str

    # Geometry
    floor_area_sqft: float | None = None

    # Cooling
    cooling_total_mbh: float | None = None
    cooling_sensible_mbh: float | None = None
    cooling_latent_mbh: float | None = None
    cooling_airflow_cfm: float | None = None
    cooling_cfm_per_sqft: float | None = None
    cooling_peak_time: str | None = None

    # Heating
    heating_load_mbh: float | None = None
    heating_airflow_cfm: float | None = None

    # Ventilation
    maximum_occupants: float | None = None
    breathing_zone_oa_cfm: float | None = None
    adjusted_oa_cfm: float | None = None
    oa_per_person: float | None = None
    oa_per_sqft: float | None = None
    direct_exhaust_cfm: float | None = None
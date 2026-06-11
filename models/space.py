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

    def __str__(self) -> str:
        """
        Human-readable summary of the space.
        Only prints populated fields.
        """

        lines: list[str] = [f"Space: {self.name}"]

        if self.floor_area_sqft is not None:
            lines.append(
                f"Floor Area: {self.floor_area_sqft} sqft"
            )

        if self.cooling_airflow_cfm is not None:
            lines.append(
                f"Cooling Airflow: "
                f"{self.cooling_airflow_cfm} CFM"
            )

        if self.maximum_occupants is not None:
            lines.append(
                f"Occupants: "
                f"{self.maximum_occupants}"
            )

        return "\n".join(lines)
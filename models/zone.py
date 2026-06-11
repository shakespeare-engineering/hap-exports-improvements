from dataclasses import dataclass, field
from models.space import Space


@dataclass
class Zone:
    """
    Represents a HAP zone.
    """

    name: str

    # General
    floor_area_sqft: float | None = None

    # Cooling sizing
    design_supply_airflow_cfm: float | None = None
    minimum_supply_airflow_cfm: float | None = None
    cooling_total_mbh: float | None = None
    cooling_sensible_mbh: float | None = None
    cooling_latent_mbh: float | None = None
    cooling_cfm_per_sqft: float | None = None
    cooling_peak_time: str | None = None

    # Heating sizing
    heating_load_mbh: float | None = None
    heating_airflow_cfm: float | None = None

    # Ventilation
    breathing_zone_oa_cfm: float | None = None
    adjusted_zone_oa_cfm: float | None = None

    # Child spaces
    # Note: field is used to create a default empty list for the spaces attribute. 
    # This ensures that each Zone instance has its own list of spaces, rather than sharing a single list.
    # This is better than using a mutable default argument like spaces: list[Space] = []
    # Which would mean that all instances of Zone would share the same list of spaces.
    spaces: list[Space] = field(default_factory=list)

    def add_space(self, space: Space) -> None:
        self.spaces.append(space)

    def __str__(self) -> str:
        """
        Human-readable summary of the zone.
        Only prints populated fields.
        """

        lines: list[str] = [f"Zone: {self.name}"]

        if self.floor_area_sqft is not None:
            lines.append(f"Floor Area: {self.floor_area_sqft} sqft")

        if self.design_supply_airflow_cfm is not None:
            lines.append(
                f"Supply Airflow: "
                f"{self.design_supply_airflow_cfm} CFM"
            )

        lines.append(f"Spaces: {len(self.spaces)}")

        return "\n".join(lines)
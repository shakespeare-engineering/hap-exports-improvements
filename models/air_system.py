from dataclasses import dataclass, field

from models.zone import Zone
from models.heat_balance import HeatBalance


@dataclass
class AirSystem:
    """
    Represents a complete HAP air system.
    """

    name: str

    # General system info
    equipment_class: str | None = None
    system_type: str | None = None
    location: str | None = None

    floor_area_sqft: float | None = None
    number_of_zones: int | None = None

    # Cooling sizing
    cooling_tons: float | None = None
    cooling_total_mbh: float | None = None
    cooling_sensible_mbh: float | None = None
    cooling_peak_time: str | None = None

    # Heating sizing
    heating_load_mbh: float | None = None

    # Airflow
    supply_airflow_cfm: float | None = None
    outdoor_airflow_cfm: float | None = None

    # Fan
    fan_bhp: float | None = None
    fan_kw: float | None = None
    fan_static_pressure_inwg: float | None = None

    # Ventilation
    occupants: float | None = None

    # Child objects
    zones: list[Zone] = field(default_factory=list)
    heat_balance: HeatBalance = field(default_factory=HeatBalance)

    def add_zone(self, zone: Zone) -> None:
        self.zones.append(zone)

    def __str__(self) -> str:
        """
        Human-readable summary of the air system.
        Only prints populated fields.
        """

        lines: list[str] = [f"Air System: {self.name}"]

        if self.cooling_tons is not None:
            lines.append(f"Cooling Tons: {self.cooling_tons}")

        if self.supply_airflow_cfm is not None:
            lines.append(f"Supply Airflow: {self.supply_airflow_cfm} CFM")

        if self.fan_bhp is not None:
            lines.append(f"Fan BHP: {self.fan_bhp}")

        if self.floor_area_sqft is not None:
            lines.append(f"Floor Area: {self.floor_area_sqft} sqft")

        lines.append(f"Zones: {len(self.zones)}")

        return "\n".join(lines)
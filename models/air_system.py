from dataclasses import dataclass, field

from models.zone import Zone
from models.coil import Coil
from models.fan import Fan
from models.ventilation import Ventilation
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

    # Coils
    cooling_coil: Coil = field(default_factory=Coil)
    heating_coil: Coil = field(default_factory=Coil)
    precool_coil: Coil = field(default_factory=Coil)
    preheat_coil: Coil = field(default_factory=Coil)

    # Fans
    supply_fan: Fan = field(default_factory=Fan)
    return_fan: Fan = field(default_factory=Fan)

    # Ventilation TODO:May need to change
    ventilation: Ventilation = field(default_factory=Ventilation)

    # Child objects
    zones: list[Zone] = field(default_factory=list)
    heat_balance: HeatBalance = field(default_factory=HeatBalance)

    def add_zone(self, zone: Zone) -> None:
        self.zones.append(zone)

    def __str__(self) -> str:
        """
        Human-readable summary of the air system.
        """

        lines: list[str] = [f"Air System: {self.name}"]

        if self.cooling_coil.total_load_mbh is not None:
            lines.append(
                f"Cooling Tons: "
                f"{self.cooling_coil.total_load_mbh/12.0:.1f}"
            )

        if (self.supply_fan.airflow_cfm is not None):
            lines.append(
                f"Supply Airflow: "
                f"{self.supply_fan.airflow_cfm:.0f} CFM"
            )

        if self.supply_fan.fan_bhp is not None:
            lines.append(
                f"Fan BHP: "
                f"{self.supply_fan.fan_bhp}"
            )

        if self.floor_area_sqft is not None:
            lines.append(
                f"Floor Area: "
                f"{self.floor_area_sqft:.0f} sqft"
            )

        lines.append(
        f"Zones: "
        f"{len(self.zones)}"
        f"/{self.number_of_zones}"
    )

        return "\n".join(lines)
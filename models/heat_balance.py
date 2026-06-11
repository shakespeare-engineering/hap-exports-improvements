from dataclasses import dataclass


@dataclass
class HeatBalance:
    """
    Heat balance breakdown for an air system.
    """

    roof_btu_hr: float | None = None
    wall_btu_hr: float | None = None
    glass_btu_hr: float | None = None
    skylight_btu_hr: float | None = None
    door_btu_hr: float | None = None
    floor_btu_hr: float | None = None
    ceiling_btu_hr: float | None = None

    people_sensible_btu_hr: float | None = None
    people_latent_btu_hr: float | None = None

    lighting_btu_hr: float | None = None
    equipment_btu_hr: float | None = None

    infiltration_btu_hr: float | None = None
    ventilation_btu_hr: float | None = None

    misc_btu_hr: float | None = None
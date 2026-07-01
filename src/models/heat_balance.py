from dataclasses import dataclass


@dataclass
class HeatBalance:

    # Naming note:
    #   Fields without a "heating" qualifier hold the DESIGN COOLING
    #   column values (sensible / latent). The "_heating_sensible_btu"
    #   fields hold the DESIGN HEATING column sensible values.

    # ==========================================
    # Design Conditions
    # ==========================================

    cooling_design_time: str | None = None
    heating_design_time: str | None = None

    cooling_oa_db_f: float | None = None
    cooling_oa_wb_f: float | None = None

    heating_oa_db_f: float | None = None
    heating_oa_wb_f: float | None = None

    # ==========================================
    # Table 1 - System Loads
    # ==========================================

    zone_conditioning_sensible_btu: float | None = None
    zone_conditioning_latent_btu: float | None = None
    zone_conditioning_heating_sensible_btu: float | None = None

    plenum_load_sensible_btu: float | None = None
    plenum_load_latent_btu: float | None = None
    plenum_load_heating_sensible_btu: float | None = None

    return_fan_sensible_btu: float | None = None
    return_fan_latent_btu: float | None = None
    return_fan_heating_sensible_btu: float | None = None

    ventilation_sensible_btu: float | None = None
    ventilation_latent_btu: float | None = None
    ventilation_heating_sensible_btu: float | None = None

    supply_fan_sensible_btu: float | None = None
    supply_fan_latent_btu: float | None = None
    supply_fan_heating_sensible_btu: float | None = None

    zone_fan_coils_sensible_btu: float | None = None
    zone_fan_coils_latent_btu: float | None = None
    zone_fan_coils_heating_sensible_btu: float | None = None

    total_system_sensible_btu: float | None = None
    total_system_latent_btu: float | None = None
    total_system_heating_sensible_btu: float | None = None

    central_cooling_coil_sensible_btu: float | None = None
    central_cooling_coil_latent_btu: float | None = None
    central_cooling_coil_heating_sensible_btu: float | None = None

    central_heating_coil_sensible_btu: float | None = None
    central_heating_coil_latent_btu: float | None = None
    central_heating_coil_heating_sensible_btu: float | None = None

    total_conditioning_sensible_btu: float | None = None
    total_conditioning_latent_btu: float | None = None
    total_conditioning_heating_sensible_btu: float | None = None

    # ==========================================
    # Table 2 - Zone Heat Balance
    # ==========================================

    wall_btu: float | None = None
    wall_sqft: float | None = None
    wall_watts: float | None = None
    wall_heating_sensible_btu: float | None = None

    roof_btu: float | None = None
    roof_sqft: float | None = None
    roof_watts: float | None = None
    roof_heating_sensible_btu: float | None = None

    window_btu: float | None = None
    window_sqft: float | None = None
    window_watts: float | None = None
    window_heating_sensible_btu: float | None = None

    skylight_btu: float | None = None
    skylight_sqft: float | None = None
    skylight_watts: float | None = None
    skylight_heating_sensible_btu: float | None = None

    door_btu: float | None = None
    door_sqft: float | None = None
    door_watts: float | None = None
    door_heating_sensible_btu: float | None = None

    floor_btu: float | None = None
    floor_sqft: float | None = None
    floor_watts: float | None = None
    floor_heating_sensible_btu: float | None = None

    interior_wall_btu: float | None = None
    interior_wall_sqft: float | None = None
    interior_wall_watts: float | None = None
    interior_wall_heating_sensible_btu: float | None = None

    ceiling_btu: float | None = None
    ceiling_sqft: float | None = None
    ceiling_watts: float | None = None
    ceiling_heating_sensible_btu: float | None = None

    overhead_lighting_btu: float | None = None
    overhead_lighting_sqft: float | None = None
    overhead_lighting_watts: float | None = None
    overhead_lighting_heating_sensible_btu: float | None = None

    task_lighting_btu: float | None = None
    task_lighting_sqft: float | None = None
    task_lighting_watts: float | None = None
    task_lighting_heating_sensible_btu: float | None = None

    equipment_btu: float | None = None
    equipment_sqft: float | None = None
    equipment_watts: float | None = None
    equipment_heating_sensible_btu: float | None = None

    people_sensible_btu: float | None = None
    people_latent_btu: float | None = None
    people_heating_sensible_btu: float | None = None

    infiltration_sensible_btu: float | None = None
    infiltration_latent_btu: float | None = None

    misc_equipment_sensible_btu: float | None = None
    misc_equipment_latent_btu: float | None = None

    air_energy_change_sensible_btu: float | None = None
    air_energy_change_latent_btu: float | None = None

    total_zone_sensible_btu: float | None = None
    total_zone_latent_btu: float | None = None

    # ==========================================
    # Misc Details
    # ==========================================

    people_count: float | None = None
    infiltration_cfm: float | None = None
    ventilation_cfm: float | None = None
    return_fan_cfm: float | None = None
    supply_fan_cfm: float | None = None
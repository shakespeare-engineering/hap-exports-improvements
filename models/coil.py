from dataclasses import dataclass


@dataclass
class Coil:
    """
    Represents a heating/cooling coil.
    """

    total_load_mbh: float | None = None
    sensible_load_mbh: float | None = None
    latent_load_mbh: float | None = None

    airflow_cfm: float | None = None
    max_airflow_cfm: float | None = None

    water_flow_gpm: float | None = None

    peak_time: str | None = None

    entering_db_f: float | None = None
    entering_wb_f: float | None = None

    leaving_db_f: float | None = None
    leaving_wb_f: float | None = None
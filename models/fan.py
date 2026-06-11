from dataclasses import dataclass


@dataclass
class Fan:
    """
    Represents a fan.
    """

    airflow_cfm: float | None = None

    fan_bhp: float | None = None
    fan_kw: float | None = None

    static_pressure_inwg: float | None = None

    cfm_per_sqft: float | None = None

    peak_time: str | None = None
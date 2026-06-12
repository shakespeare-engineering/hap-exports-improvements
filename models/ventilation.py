from dataclasses import dataclass


@dataclass
class Ventilation:
    """
    Outdoor air ventilation data.
    """

    outdoor_airflow_cfm: float | None = None

    cfm_per_sqft: float | None = None
    cfm_per_person: float | None = None

    percent_outdoor_air: float | None = None

    # PDF ventilation report
    design_oa_cfm: float | None = None
    corrected_oa_cfm: float | None = None
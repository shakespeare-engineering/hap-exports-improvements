import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from models.air_system import AirSystem
from extractors.heat_balance_pdf import extract_heat_balance_pdf


# System and PDF used for the test fixture.
TEST_SYSTEM_NAME: str = "HP-101-FITNESS"

EXAMPLE_PDF: Path = (
    Path(__file__).resolve().parent.parent
    / "Hap Examples"
    / "2026-05-29_HeatBalance.pdf"
)


def build_test_systems() -> dict[str, AirSystem]:
    """
    Build a systems dict containing only the test system.

    Returns:
        dict[str, AirSystem]: One entry keyed by TEST_SYSTEM_NAME.
    """

    return {
        TEST_SYSTEM_NAME: AirSystem(name=TEST_SYSTEM_NAME)
    }


def check(label: str, actual, expected) -> bool:
    """
    Compare one value and print a PASS/FAIL line.

    Args:
        label (str): Name of the value being checked.
        actual: Value produced by the extractor.
        expected: Value expected from the PDF.

    Returns:
        bool: True if actual equals expected.
    """

    passed: bool = actual == expected

    status: str = "PASS" if passed else "FAIL"

    print(f"  [{status}] {label}: got {actual}, expected {expected}")

    return passed


def main() -> None:
    """
    Extract the heat balance and verify heating (and a few cooling)
    values for the test system.
    """

    if not EXAMPLE_PDF.exists():
        raise FileNotFoundError(
            f"Example PDF not found:\n{EXAMPLE_PDF}"
        )

    systems: dict[str, AirSystem] = build_test_systems()

    extract_heat_balance_pdf(str(EXAMPLE_PDF), systems)

    heat = systems[TEST_SYSTEM_NAME].heat_balance

    all_passed: bool = True

    # ==========================================
    # Heating sensible values (the new feature)
    # ==========================================

    print("\nHeating sensible values:")

    heating_checks = [
        ("zone_conditioning", heat.zone_conditioning_heating_sensible_btu, 6686),
        ("ventilation", heat.ventilation_heating_sensible_btu, 16850),
        ("supply_fan", heat.supply_fan_heating_sensible_btu, -1801),
        ("total_system", heat.total_system_heating_sensible_btu, 21735),
        ("central_heating_coil", heat.central_heating_coil_heating_sensible_btu, 21807),
        ("total_conditioning", heat.total_conditioning_heating_sensible_btu, 21807),
        ("wall", heat.wall_heating_sensible_btu, 438),
        ("ceiling", heat.ceiling_heating_sensible_btu, 1227),
        ("overhead_lighting", heat.overhead_lighting_heating_sensible_btu, 0),
        ("people", heat.people_heating_sensible_btu, 0),
    ]

    for label, actual, expected in heating_checks:
        if not check(label, actual, expected):
            all_passed = False

    # ==========================================
    # Cooling values unchanged (regression guard)
    # ==========================================

    print("\nCooling values (regression guard):")

    cooling_checks = [
        ("zone_conditioning_sensible", heat.zone_conditioning_sensible_btu, 21897),
        ("ventilation_sensible", heat.ventilation_sensible_btu, 10721),
        ("wall_btu", heat.wall_btu, 697),
        ("ceiling_btu", heat.ceiling_btu, 4412),
    ]

    for label, actual, expected in cooling_checks:
        if not check(label, actual, expected):
            all_passed = False

    # ==========================================
    # Result
    # ==========================================

    print()

    if all_passed:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()

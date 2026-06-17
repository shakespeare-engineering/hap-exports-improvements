from pathlib import Path
import sys

from split_hap_pdf import split_hap_pdf
from hap_exports_loader import load_hap_exports
from checksum_excel_export import export_system_checksums


def main() -> None:
    """
    Main entry point for HAP Export Generator.
    """

    print("=" * 60)
    print("HAP Export Generator")
    print("=" * 60)

    print()
    print("Instructions:")
    print("1. Export the combined PDF from HAP.")
    print("2. Drag the PDF onto this program.")
    print("3. The program will split the PDF.")
    print("4. The program will generate checksum reports.")
    print()

    # ======================================
    # Drag-and-drop support
    # ======================================

    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]

    else:
        input_pdf = input(
            "Enter path to HAP PDF (or drag file here): "
        )

    input_pdf = input_pdf.strip()

    if input_pdf.startswith("&"):
        input_pdf = input_pdf[1:].strip()

    input_pdf = input_pdf.strip('"').strip("'")

    pdf_path = Path(input_pdf)

    if not pdf_path.exists():

        print()
        print("ERROR: PDF not found.")

        input(
            "\nPress Enter to exit..."
        )

        return

    project_directory = str(
        pdf_path.parent
    )

    try:

        # ======================================
        # Split PDF
        # ======================================

        print()
        print("Splitting HAP PDF...")

        split_hap_pdf(
            str(pdf_path)
        )

        # ======================================
        # Load HAP Exports
        # ======================================

        print(
            "Loading HAP exports..."
        )

        hap_exports_folder = (
            pdf_path.parent
            / "HAP Exports"
        )

        systems = load_hap_exports(
            str(pdf_path.parent)
        )

        # ======================================
        # Generate checksum workbook
        # ======================================

        print(
            "Generating checksum workbook..."
        )

        export_system_checksums(
            systems,
            str(hap_exports_folder)
        )

        print()
        print(
            "HAP Export Generation Complete."
        )

    except Exception as error:

        print()
        print("=" * 60)
        print("ERROR")
        print("=" * 60)
        print()

        print(error)

        print()
        print(
            "The export process was not completed."
        )

    input(
        "\nPress Enter to exit..."
    )


if __name__ == "__main__":
    main()
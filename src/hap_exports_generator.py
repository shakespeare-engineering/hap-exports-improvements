from pathlib import Path
import sys

from split_hap_pdf import split_hap_pdf
from hap_exports_loader import load_hap_exports
from checksum_excel_export import export_system_checksums


# Debug flag: delete the combined PDF and the source spreadsheets
# after a successful run. The split PDFs and generated workbook are kept.
# TODO: expose this as a user option in the executable.
DELETE_SOURCE_FILES: bool = True

# Glob patterns for the spreadsheets the loader parses.
# These mirror the patterns in hap_exports_loader.find_file().
SOURCE_EXCEL_PATTERNS: tuple[str, ...] = (
    "*SysSizingSummary.xlsx",
    "*ZoneSizingSummary.xlsx",
)


def delete_file(file_path: Path) -> None:
    """
    Delete a single file, reporting the result.

    Args:
        file_path (Path): File to delete.

    Returns:
        None
    """

    try:
        file_path.unlink()
        print(f"  Deleted: {file_path.name}")

    except OSError as error:
        print(f"  Could not delete {file_path.name}: {error}")


def delete_source_files(combined_pdf_path: Path, project_directory: Path) -> None:
    """
    Delete the source files consumed by the export process.

    Removes the combined input PDF and the two sizing spreadsheets.
    The split PDFs and the generated workbook are left in place.

    Args:
        combined_pdf_path (Path): The combined HAP PDF that was split.
        project_directory (Path): Folder containing the source spreadsheets.

    Returns:
        None
    """

    print("\nDeleting source files...")

    # Combined input PDF
    if combined_pdf_path.exists():
        delete_file(combined_pdf_path)

    # Sizing spreadsheets
    for pattern in SOURCE_EXCEL_PATTERNS:

        excel_matches: list[Path] = list(project_directory.glob(pattern))

        if not excel_matches:
            print(f"  No file matching {pattern} found.")
            continue

        delete_file(excel_matches[0])


def main() -> None:
    """
    Main entry point for HAP Export Generator.
    """

    print("=" * 60)
    print("HAP Export Generator")
    print("=" * 60)

    print()
    print("Instructions:")
    print()
    print("1. In HAP, export the COMBINED report PDF that")
    print("   contains all required report sections.")
    print("   and the excel files associated with")
    print("   system sizing and zone sizing.")
    print("   Make sure those files are in the same directory.")
    print()
    print("2. Easiest method:")
    print("   Drag the PDF file directly onto the")
    print("   HAP Export Generator.exe icon.")
    print()
    print("3. Alternative method:")
    print("   Run the program and either type the full")
    print("   file path or drag the PDF into this")
    print("   console window and press Enter.")
    print()
    print("4. The program will automatically:")
    print("   - Split the combined PDF")
    print("   - Create a HAP Exports folder")
    print("   - Parse all HAP reports")
    print("   - Generate the System Checksums workbook")
    print()
    print("5. All generated files will be placed in")
    print("   the project directory.")
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

        # Clean up consumed source files (toggle via DELETE_SOURCE_FILES)
        if DELETE_SOURCE_FILES:
            delete_source_files(pdf_path, pdf_path.parent)

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
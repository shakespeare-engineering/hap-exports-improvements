from ast import keyword
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import sys


# ==========================================================
# HAP PDF Splitter
# Splits HAP load reports into separate PDFs by report type
# Supports file drag-and-drop
# ==========================================================

# Keywords Dictionary used to classify pages.  Key is report type, value is text to search for in page header.
REPORT_TYPE_KEYWORDS: dict[str, str] = {
    "system_sizing": "Air System Sizing Summary",
    "zone_sizing": "Zone Sizing Summary",
    "ventilation_sizing": "Ventilation Sizing Summary",
    "heat_balance": "Air System Heat Balance Summary",
}


def detect_report_type(text: str) -> str | None:
    """
    Determine which report type a page belongs to.
    """
    text_lower = text.lower()

    for report_type, search_text in REPORT_TYPE_KEYWORDS.items():
        if search_text.lower() in text_lower:
            return report_type

    return None


def split_hap_pdf(pdf_path_str: str) -> None:
    """
    Split a HAP summary PDF into separate PDFs by report type.

    Reads a HAP-generated PDF and classifies pages into:
    - Air System Sizing Summary
    - Zone Sizing Summary
    - Ventilation Sizing Summary
    - Air System Heat Balance Summary

    Each report type is exported to its own PDF file
    inside the output directory.

    Multi-page report sections are supported by tracking
    the current detected report type across pages.

    Args:
        pdf_path_str (str):
            File path to the HAP PDF to process.

    Returns:
        None
    """

    pdf_path: Path = Path(pdf_path_str)

    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        return

    print(f"\nProcessing: {pdf_path.name}")

    reader: PdfReader = PdfReader(pdf_path_str)

    # Create PDF writers
    writers: dict[str, PdfWriter] = {
        "system_sizing": PdfWriter(),
        "zone_sizing": PdfWriter(),
        "ventilation_sizing": PdfWriter(),
        "heat_balance": PdfWriter(),
    }

    # Track unknown pages
    unknown_pages: list[int] = []

    # Used for multi-page reports
    current_report_type: str | None = None

    # enumerate makes it easy to track page numbers for logging.  start=1 makes page numbers 1-based instead of 0-based.
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text: str = page.extract_text()

            #TODO: Remove
            print(repr(text))
            if not text:
                text = ""

            # Only inspect first chunk of text for speed
            header_text = text[:2000]

            detected_type = detect_report_type(header_text)

            # If we found a report type, update current section
            if detected_type:
                current_report_type = detected_type

            # Add page to active report type
            if current_report_type:
                writers[current_report_type].add_page(page)

                print(
                    f"Page {page_num:>3} → "
                    f"{current_report_type.replace('_', ' ').title()}"
                )
            else:
                unknown_pages.append(page_num)
                print(f"Page {page_num:>3} → UNKNOWN")

        except Exception as e:
            print(f"Page {page_num} ERROR: {e}")
            unknown_pages.append(page_num)

    # Create output folder
    output_dir = pdf_path.parent / "HAP Exports"
    output_dir.mkdir(exist_ok=True)

    output_files = {
        "system_sizing":
            output_dir / f"{pdf_path.stem}_SystemSizingSummary.pdf",

        "zone_sizing":
            output_dir / f"{pdf_path.stem}_ZoneSizingSummary.pdf",

        "ventilation_sizing":
            output_dir / f"{pdf_path.stem}_VentilationSizingSummary.pdf",

        "heat_balance":
            output_dir / f"{pdf_path.stem}_HeatBalanceSummary.pdf",
    }

    # Save PDFs
    for report_type, writer in writers.items():
        if len(writer.pages) > 0:
            output_file = output_files[report_type]

            with open(output_file, "wb") as f:
                writer.write(f)

            print(f"Saved: {output_file.name}")

    # Log unknown pages
    if unknown_pages:
        log_file = output_dir / "unknown_pages.txt"

        with open(log_file, "w") as f:
            f.write("Pages not classified:\n")
            for page in unknown_pages:
                f.write(f"{page}\n")

        print(
            f"\nWARNING: {len(unknown_pages)} page(s) "
            f"could not be classified."
        )
        print(f"See: {log_file.name}")

    print("\nDone!")


if __name__ == "__main__":

    # Drag-and-drop support
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]

    else:
        input_pdf = input(
            "Enter path to HAP PDF (or drag file here): "
        ).strip().strip('"')

    split_hap_pdf(input_pdf)
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import sys


# ==========================================================
# HAP PDF Splitter
# Splits HAP load reports into separate PDFs by report type
# ==========================================================

# Keywords used to classify pages
REPORT_TYPES = {
    "system_sizing": "Air System Sizing Summary",
    "zone_sizing": "Zone Sizing Summary",
    "ventilation_sizing": "Ventilation Sizing Summary",
    "heat_balance": "Air System Heat Balance Summary",
}


def detect_report_type(text):
    """
    Determine which report type a page belongs to.
    """
    text_lower = text.lower()

    for report_name, keyword in REPORT_TYPES.items():
        if keyword.lower() in text_lower:
            return report_name

    return None


def split_hap_pdf(pdf_path):
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        return

    print(f"\nProcessing: {pdf_path.name}")

    reader = PdfReader(str(pdf_path))

    # Create PDF writers
    writers = {
        "system_sizing": PdfWriter(),
        "zone_sizing": PdfWriter(),
        "ventilation_sizing": PdfWriter(),
        "heat_balance": PdfWriter(),
    }

    # Track unknown pages
    unknown_pages = []

    # Used for multi-page reports
    current_report_type = None

    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()

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
# ==========================================================
# Imports
# ==========================================================

# Path handling for files/folders.
# Used instead of raw strings for safer path operations.
from pathlib import Path

# PDF reading/writing utilities.
# PdfReader -> reads existing PDFs
# PdfWriter -> creates output PDFs
from pypdf import PdfReader, PdfWriter

# In-memory binary stream.
# Used for temporary PDF overlays without
# creating physical temp files on disk.
from io import BytesIO

# Used to draw graphics/text onto PDFs.
# Needed for replacing HAP page numbering.
from reportlab.pdfgen import canvas

# Used for date/time operations.
from datetime import datetime

# Access to command-line arguments.
# Used for drag-and-drop file support.
import sys

# Regular expressions.
# Used to parse the project name from the report header.
import re


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

    Returns:
        None if no report type is detected, otherwise returns the report type key.
    """
    text_lower = text.lower()

    for report_type, search_text in REPORT_TYPE_KEYWORDS.items():
        if search_text.lower() in text_lower:
            return report_type

    return None


# Header line format: "Project: <name> MM/DD/YYYY"
# The trailing date is tabbed to the right of the page and is used
# only as a boundary marker; it is not part of the captured name.
PROJECT_NAME_PATTERN: str = r"Project:\s+(.+?)\s+\d{2}/\d{2}/\d{4}"


def extract_project_name(text: str) -> str | None:
    """
    Parse the HAP project name from a page's text.

    Args:
        text (str): Extracted text from a single PDF page.

    Returns:
        str | None: The project name if found, otherwise None.
    """

    project_match = re.search(PROJECT_NAME_PATTERN, text)

    if not project_match:
        return None

    project_name: str = project_match.group(1).strip()

    return project_name


def clean_filename_component(name: str) -> str:
    """
    Make a string safe to embed in a filename.

    Replaces characters that are invalid in Windows filenames
    and removes all whitespace (e.g. "St George" -> "StGeorge").

    Args:
        name (str): Raw text to sanitize.

    Returns:
        str: Sanitized filename component.
    """

    invalid_chars: str = '<>:"/\\|?*'

    cleaned_name: str = name

    for char in invalid_chars:
        cleaned_name = cleaned_name.replace(char, "-")

    cleaned_name = "".join(cleaned_name.split())

    return cleaned_name


def add_page_numbers(writer: PdfWriter) -> None:
    """
    Replace HAP footer page numbers with
    correct numbering for the split PDF.
    """

    total_pages: int = len(writer.pages)

    for page_num, page in enumerate(writer.pages, start=1):

        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        # Create temporary PDF overlay
        # We use an in-memory BytesIO stream to avoid creating temporary files on disk.
        # Temporary PDF will contain a white rectangle to cover old page number and new page number text.
        overlay_stream: BytesIO = BytesIO()

        overlay_canvas = canvas.Canvas(overlay_stream, pagesize=(page_width, page_height))

        # Set fill color to white
        overlay_canvas.setFillColorRGB(1, 1, 1)

        # White rectangle to cover old footer
        overlay_canvas.rect(
            page_width - 96,     # x
            20,                     # y
            60,                     # width
            30,                    # height
            fill=1,
            stroke=0
        )

        # Set text color to black
        overlay_canvas.setFillColorRGB(0, 0, 0)

        # New page number
        overlay_canvas.drawString(
            page_width - 166,        # x (adjust as needed for alignment)
            20,                     # y (adjust as needed for alignment)
            f"Page {page_num} of {total_pages}"
        )

        overlay_canvas.save()

        # Move stream position to the beginning so it can be read by PdfReader
        overlay_stream.seek(0)

        overlay_pdf = PdfReader(overlay_stream)
        overlay_page = overlay_pdf.pages[0]

        # Merge overlay onto page
        page.merge_page(overlay_page)

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

    # Project name parsed from the report header (used for filenames)
    project_name: str | None = None

    # Loop through pages and classify them.  Pages are added to the appropriate writer based on their content.
    # enumerate makes it easy to track page numbers for logging.  start=1 makes page numbers 1-based instead of 0-based.
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text: str = page.extract_text()

            #  Print the text for debugging purposes
            #  print(repr(text))

            if not text:
                text = ""

            # Capture project name once for output filenames
            if project_name is None:
                project_name = extract_project_name(text)

            # Only inspect first chunk of text for speed
            header_text = text[:200]

            detected_type: str | None = detect_report_type(header_text)

            # If we found a report type, update current section
            if detected_type:
                current_report_type = detected_type

            # Add page to active report type
            if current_report_type:
                writers[current_report_type].add_page(page)

                # Note: "{page_num:>3}" formats page number right-aligned with width of 3 (e.g. "  1", " 10", "100")
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
    today_date: str = datetime.today().strftime("%Y-%m-%d")
    output_dir = pdf_path.parent / f"{today_date}_HAP Exports"    # Note: exist_ok=True allows the directory to be created if it doesn't exist and does nothing if it already exists, preventing errors.
    output_dir.mkdir(exist_ok=True)

    # Build filename prefix: system date + project name.
    # The system date is used (same source as the folder name above),
    # not the report date parsed from the PDF header.
    if project_name:
        clean_project_name: str = clean_filename_component(project_name)
        filename_prefix: str = f"{today_date}_{clean_project_name}"
    else:
        filename_prefix = pdf_path.stem
        print(
            "\nWARNING: Project name not found in PDF; "
            "using PDF filename for output names."
        )

    output_files: dict[str, Path] = {
        "system_sizing":
            output_dir / f"{filename_prefix}_SystemSizingSummary.pdf",

        "zone_sizing":
            output_dir / f"{filename_prefix}_ZoneSizingSummary.pdf",

        "ventilation_sizing":
            output_dir / f"{filename_prefix}_VentilationSizingSummary.pdf",

        "heat_balance":
            output_dir / f"{filename_prefix}_HeatBalanceSummary.pdf",
    }

    # Save PDFs
    for report_type, writer in writers.items():
        if len(writer.pages) > 0:
            # Fix page numbering
            add_page_numbers(writer)

            output_file: Path = output_files[report_type]

            # Note: "wb" (write binary) mode is required for writing binary PDF files.
            # Note: with open() is used to ensure the file is properly closed after writing. 
            with open(output_file, "wb") as file:
                writer.write(file)

            print(f"Saved: {output_file.name}")

    # Log unknown pages. Not properly tested.
    if unknown_pages:
        # Note: "w" (write) mode is used for text files.
        log_file = output_dir / "unknown_pages.txt"

        with open(log_file, "w") as file:
            file.write("Pages not classified:\n")
            for unknown_page_num in unknown_pages:
                file.write(f"{unknown_page_num}\n")

        print(
            f"\nWARNING: {len(unknown_pages)} page(s) "
            f"could not be classified."
        )
        print(f"See: {log_file.name}")

    print("\nDone!")


if __name__ == "__main__":

    try:
        # Drag-and-drop support
        if len(sys.argv) > 1:
            input_pdf = sys.argv[1]

        else:
            input_pdf = input(
                "Enter path to HAP PDF (or drag file here): "
            ).strip().strip('"')

        split_hap_pdf(input_pdf)

    finally:
        input("\nPress Enter to close...")
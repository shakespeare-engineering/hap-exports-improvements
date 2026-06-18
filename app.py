import os
import sys
import tempfile
import shutil
import zipfile
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, send_file, jsonify

sys.path.insert(0, os.path.dirname(__file__))

from split_hap_pdf import split_hap_pdf
from hap_exports_loader import load_hap_exports
from checksum_excel_export import export_system_checksums

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    pdf_file = request.files.get('pdf')
    sys_excel = request.files.get('sys_excel')
    zone_excel = request.files.get('zone_excel')

    if not pdf_file or not sys_excel or not zone_excel:
        return jsonify({'error': 'All three files are required.'}), 400

    temp_dir = tempfile.mkdtemp()

    try:
        # Save uploaded files preserving original names
        pdf_path = os.path.join(temp_dir, pdf_file.filename)
        sys_path = os.path.join(temp_dir, sys_excel.filename)
        zone_path = os.path.join(temp_dir, zone_excel.filename)

        pdf_file.save(pdf_path)
        sys_excel.save(sys_path)
        zone_excel.save(zone_path)

        # Step 1: Split the PDF
        split_hap_pdf(pdf_path)

        # Step 2: Load HAP exports
        systems = load_hap_exports(temp_dir)

        # Step 3: Find the generated HAP Exports folder
        hap_folders = [
            f for f in Path(temp_dir).iterdir()
            if f.is_dir() and f.name.endswith('_HAP Exports')
        ]

        if not hap_folders:
            return jsonify({'error': 'HAP Exports folder was not created. Check that your PDF contains the expected report sections.'}), 500

        hap_exports_folder = max(hap_folders, key=lambda f: f.stat().st_mtime)

        # Step 4: Generate checksum workbook
        export_system_checksums(systems, str(hap_exports_folder))

        # Step 5: Zip with folder structure
        # Result will be:
        #   ProjectName - HAP Exports.zip
        #   ├── 2026-06-18_HAP Exports/
        #   │   ├── project_SystemSizingSummary.pdf
        #   │   ├── project_ZoneSizingSummary.pdf
        #   │   ├── project_VentilationSizingSummary.pdf
        #   │   └── project_HeatBalanceSummary.pdf
        #   └── ProjectName - System Checksums.xlsx

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Split PDFs inside their dated folder
            for file in hap_exports_folder.iterdir():

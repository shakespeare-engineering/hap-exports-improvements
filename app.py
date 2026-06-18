import os
import sys
import tempfile
import shutil
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

        hap_exports_folder = str(
            max(hap_folders, key=lambda f: f.stat().st_mtime)
        )

        # Step 4: Generate checksum workbook
        export_system_checksums(systems, hap_exports_folder)

        # Step 5: Find the output xlsx file
        output_files = list(Path(hap_exports_folder).glob('* - System Checksums.xlsx'))

        if not output_files:
            output_files = list(Path(temp_dir).glob('* - System Checksums.xlsx'))

        if not output_files:
            return jsonify({'error': 'Output file was not generated. The process may have completed with errors.'}), 500

        output_path = output_files[0]
        output_name = output_path.name

        # Read into memory so we can clean up temp dir safely
        with open(output_path, 'rb') as f:
            file_data = BytesIO(f.read())
        file_data.seek(0)

        return send_file(
            file_data,
            as_attachment=True,
            download_name=output_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except FileNotFoundError as e:
        return jsonify({'error': f'Required file not found: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

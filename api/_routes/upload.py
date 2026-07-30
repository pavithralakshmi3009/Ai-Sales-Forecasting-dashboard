# pyrefly: ignore [missing-import]
from flask import Blueprint
import os
import sys
import io
import csv
import logging
from flask import jsonify, request

# Removed sys.path modification to avoid ModuleNotFoundError on Vercel

from _services.config import SECRET_KEY, CORS_ORIGINS
from _services.validation import validate_csv_header
from _services.database import log_uploaded_dataset, save_dataset_rows
from _services.auth_service import require_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)


@upload_bp.route('/api/upload', methods=['POST'])
@upload_bp.route('/api/upload-csv', methods=['POST'])  # Backward compatibility
@upload_bp.route('/upload', methods=['POST'])
@upload_bp.route('/upload-csv', methods=['POST'])  # Backward compatibility
@require_auth
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')

        if len(lines) < 3:
            return jsonify({'error': 'CSV must have a header and at least 2 data rows'}), 400

        if not validate_csv_header(lines[0]):
            return jsonify({'error': 'CSV must have "Month" and "Sales" columns'}), 400

        # Parse CSV rows
        reader = csv.DictReader(io.StringIO(content))
        rows = []
        for row in reader:
            try:
                month_val = int(row.get('Month', row.get('month', '')))
                sales_val = float(row.get('Sales', row.get('sales', '')))
                rows.append({'month': month_val, 'sales': sales_val})
            except (ValueError, TypeError):
                continue  # Skip rows with invalid data

        if len(rows) < 2:
            return jsonify({'error': 'CSV must contain at least 2 valid data rows'}), 400

        record_count = len(rows)

        # Store dataset rows into database
        save_dataset_rows(rows)

        # Log upload metadata
        log_uploaded_dataset(file.filename, record_count)

        return jsonify({
            'success': True,
            'message': f'CSV uploaded and validated. {record_count} records stored in database.',
            'rows': record_count
        })
    except Exception as e:
        logger.error(f"CSV upload error: {e}")
        return jsonify({'error': f'Failed to process CSV: {str(e)}'}), 500



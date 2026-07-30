# pyrefly: ignore [missing-import]
from flask import Blueprint, jsonify, request
import logging

from _services.auth_service import require_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

predict_bp = Blueprint("predict", __name__)


@predict_bp.route('/api/predict', methods=['POST'])
@predict_bp.route('/predict', methods=['POST'])
@require_auth
def predict():
    data = request.get_json() or {}
    month = data.get('month')

    if month is None:
        return jsonify({'error': 'Month is required'}), 400

    try:
        m = int(month)
        if m <= 0:
            return jsonify({'error': 'Month must be greater than 0'}), 400

        # Lazy import of forecast/predict_sales to prevent early sklearn/pandas import
        from _services.forecast import predict_sales
        prediction = predict_sales(m)
        return jsonify({
            'month': m,
            'predicted_sales': prediction
        })
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@predict_bp.route('/api/predict/transaction', methods=['POST'])
@predict_bp.route('/predict/transaction', methods=['POST'])
@require_auth
def predict_transaction():
    data = request.get_json() or {}
    try:
        date = data.get('date')
        product = data.get('product')
        category = data.get('category')
        quantity = int(data.get('quantity', 1))
        price = float(data.get('price', 0))

        total = quantity * price
        # Simple heuristic: predict 20% profit margin as a baseline if ML doesn't have it
        predicted_profit = round(total * 0.20, 2)

        # Save to forecast_history table (JSONB)
        from _services.database import get_db_connection
        import json
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                payload = json.dumps({
                    "date": date,
                    "product": product,
                    "category": category,
                    "quantity": quantity,
                    "price": price,
                    "total": total,
                    "predicted_profit": predicted_profit
                })
                cursor.execute(
                    "INSERT INTO forecast_history (forecast_data) VALUES (%s)",
                    (payload,)
                )
            conn.commit()

        return jsonify({
            'success': True,
            'total': total,
            'predicted_profit': predicted_profit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

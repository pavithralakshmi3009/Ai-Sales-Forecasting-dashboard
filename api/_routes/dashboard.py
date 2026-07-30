# pyrefly: ignore [missing-import]
from flask import Blueprint, jsonify
import logging

import _services.database as database
from _services.auth_service import require_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route('/api/stats', methods=['GET'])
@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    try:
        sales_list = database.view_sales()
        total_sales = sum(float(s['total']) for s in sales_list)
        total_profit = sum(float(s['profit']) for s in sales_list)
        total_orders = len(sales_list)
        return jsonify({
            'total_sales': round(total_sales, 2),
            'total_profit': round(total_profit, 2),
            'total_orders': total_orders
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

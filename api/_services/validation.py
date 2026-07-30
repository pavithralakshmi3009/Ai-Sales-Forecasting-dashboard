def validate_sale_input(date, product, category, quantity, price):
    """Validate sale record inputs."""
    if not all([date, product, category, quantity, price]):
        return False, 'All fields are required'
    
    try:
        qty = int(quantity)
        prc = float(price)
        if qty <= 0 or prc <= 0:
            return False, 'Quantity and Price must be positive numbers'
        return True, (qty, prc)
    except (ValueError, TypeError):
        return False, 'Quantity and Price must be numeric'

def validate_csv_header(header_line: str) -> bool:
    """Validate CSV header contains required columns."""
    header = header_line.strip().lower()
    return 'month' in header and 'sales' in header

def format_money(amount):
    """12.5 -> 'EUR 12.50'"""
    return f"EUR {amount:.2f}"


def total(prices):
    return sum(prices)

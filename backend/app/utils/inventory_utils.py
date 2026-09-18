def calculate_stock_status(available_stock: int, reorder_level: int) -> str:
    """
    Automatically determine stock status.
    """

    if available_stock == 0:
        return "Out of Stock"

    if available_stock <= reorder_level:
        return "Low Stock"

    return "In Stock"
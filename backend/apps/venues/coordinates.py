from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

# Venue.latitude/longitude: max_digits=9, decimal_places=6
COORD_QUANT = Decimal("0.000001")


def normalize_coordinate(value) -> Decimal:
    try:
        coord = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Некоректне число координати.") from exc
    return coord.quantize(COORD_QUANT, rounding=ROUND_HALF_UP)


def coordinate_to_str(value) -> str:
    if value is None or value == "":
        return ""
    return format(normalize_coordinate(value), "f")

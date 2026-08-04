from decimal import Decimal

DEMO_LATITUDE = Decimal("50.450100")
DEMO_LONGITUDE = Decimal("30.523400")
COORD_TOLERANCE = Decimal("0.00001")

NON_KYIV_ADDRESS_MARKERS = (
    "львів",
    "lviv",
    "одес",
    "odesa",
    "харків",
    "kharkiv",
    "дніпр",
    "dnipro",
    "запоріж",
    "zaporizh",
)


def coords_match_demo_defaults(latitude: Decimal, longitude: Decimal) -> bool:
    return (
        abs(latitude - DEMO_LATITUDE) <= COORD_TOLERANCE
        and abs(longitude - DEMO_LONGITUDE) <= COORD_TOLERANCE
    )


def address_suggests_non_kyiv(address: str) -> bool:
    normalized = (address or "").lower()
    return any(marker in normalized for marker in NON_KYIV_ADDRESS_MARKERS)

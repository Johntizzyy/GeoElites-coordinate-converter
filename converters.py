from pyproj import Transformer, CRS
import re

# Define CRS Definitions
crs_wgs84 = CRS.from_epsg(4326)
crs_minna = CRS.from_epsg(4263)

# --- 1. SMART INPUT PARSER (DMS or Decimal -> Decimal Float) ---
def parse_dms(value):
    """
    Parses inputs like "8.5", "8 30 15", or "8° 30' 15"" into decimal degrees.
    """
    if not value: return 0.0
    # Clean string: replace symbols with space
    val_str = str(value).strip().replace('°', ' ').replace("'", ' ').replace('"', ' ')

    # Split by non-number characters
    parts = re.split(r'[^\d\.-]+', val_str)
    parts = [p for p in parts if p] # Remove empty strings

    try:
        # Case A: Decimal Degrees (e.g., "8.5")
        if len(parts) == 1:
            return float(parts[0])

        # Case B: DMS (e.g., "8 30 15")
        elif len(parts) >= 3:
            d = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            # Handle negative degrees for DMS
            sign = -1 if d < 0 else 1
            return d + (sign * m / 60) + (sign * s / 3600)

        # Case C: DM (e.g., "8 30")
        elif len(parts) == 2:
            d = float(parts[0])
            m = float(parts[1])
            sign = -1 if d < 0 else 1
            return d + (sign * m / 60)

    except:
        return 0.0
    return 0.0

# --- 2. OUTPUT HELPER (Decimal -> DMS String) ---
def to_dms(deg, is_lat=True):
    direction = 'N' if is_lat else 'E'
    if deg < 0:
        direction = 'S' if is_lat else 'W'
        deg = abs(deg)

    d = int(deg)
    m_float = (deg - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60

    return f"{d}° {m}' {s:.4f}\" {direction}"

# --- 3. CONVERSION LOGIC ---

def wgs84_to_minna(lat, lon):
    transformer = Transformer.from_crs(crs_wgs84, crs_minna, always_xy=True)
    m_lon, m_lat = transformer.transform(lon, lat)
    return m_lat, m_lon

def minna_to_wgs84(lat, lon):
    transformer = Transformer.from_crs(crs_minna, crs_wgs84, always_xy=True)
    w_lon, w_lat = transformer.transform(lon, lat)
    return w_lat, w_lon

def minna_to_utm(lat, lon):
    # AUTO DETECT ZONE (Nigeria Logic)
    if lon <= 6: zone = 31
    elif lon <= 12: zone = 32
    else: zone = 33

    epsg = 26300 + zone
    transformer = Transformer.from_crs(crs_minna, CRS.from_epsg(epsg), always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return zone, easting, northing, epsg

def utm_to_wgs84(easting, northing, zone):
    epsg = 26300 + int(zone)
    transformer = Transformer.from_crs(CRS.from_epsg(epsg), crs_wgs84, always_xy=True)
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

from flask import Flask, render_template, request, jsonify
from converters import wgs84_to_minna, minna_to_wgs84, minna_to_utm, utm_to_wgs84, to_dms, parse_dms

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    conv_type = data.get("type")

    try:
        # 1. WGS84 -> MINNA
        if conv_type == "wgs_to_minna":
            lat = parse_dms(data["lat"])
            lon = parse_dms(data["lon"])
            
            m_lat, m_lon = wgs84_to_minna(lat, lon)
            return jsonify({
                "success": True, 
                "lat": round(m_lat, 6), "lon": round(m_lon, 6),
                "lat_dms": to_dms(m_lat, True), "lon_dms": to_dms(m_lon, False)
            })

        # 2. WGS84 -> UTM (Auto Zone)
        elif conv_type == "wgs_to_utm":
            lat = parse_dms(data["lat"])
            lon = parse_dms(data["lon"])
            
            # WGS -> Minna -> UTM
            m_lat, m_lon = wgs84_to_minna(lat, lon)
            zone, e, n, epsg = minna_to_utm(m_lat, m_lon)
            
            return jsonify({
                "success": True, 
                "zone": zone, 
                "easting": round(e, 3), "northing": round(n, 3)
            })

        # 3. MINNA (Geographic) -> WGS84
        elif conv_type == "minna_to_wgs":
            lat = parse_dms(data["lat"])
            lon = parse_dms(data["lon"])
            
            w_lat, w_lon = minna_to_wgs84(lat, lon)
            return jsonify({
                "success": True, 
                "lat": round(w_lat, 6), "lon": round(w_lon, 6),
                "lat_dms": to_dms(w_lat, True), "lon_dms": to_dms(w_lon, False)
            })

        # 4. UTM (Minna) -> WGS84
        elif conv_type == "utm_to_wgs":
            e = float(data["easting"])
            n = float(data["northing"])
            zone = int(data["zone"])
            
            lat, lon = utm_to_wgs84(e, n, zone)
            
            return jsonify({
                "success": True, 
                "lat": round(lat, 6), "lon": round(lon, 6),
                "lat_dms": to_dms(lat, True), "lon_dms": to_dms(lon, False)
            })

        # 5. NEW: MINNA (Geographic) -> MINNA UTM
        elif conv_type == "minna_to_utm":
            lat = parse_dms(data["lat"])
            lon = parse_dms(data["lon"])
            
            # A. Math: Convert Geographic to UTM
            zone, e, n, epsg = minna_to_utm(lat, lon)
            
            # B. Map Accuracy: We must also convert to WGS84 just for the map pin
            w_lat, w_lon = minna_to_wgs84(lat, lon)
            
            return jsonify({
                "success": True, 
                "zone": zone, 
                "easting": round(e, 3), "northing": round(n, 3),
                "map_lat": w_lat, "map_lon": w_lon
            })

        return jsonify({"success": False, "error": "Unknown Type"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
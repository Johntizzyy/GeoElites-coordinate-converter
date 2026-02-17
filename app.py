from flask import Flask, render_template, request, jsonify
from converters import wgs84_to_minna, minna_to_wgs84, minna_to_utm, utm_to_wgs84, to_dms, parse_dms

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    if not request.json:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    data = request.json
    conv_type = data.get("type")

    if not conv_type:
        return jsonify({"success": False, "error": "Conversion type not specified"}), 400

    try:
        # 1. WGS84 -> MINNA
        if conv_type == "wgs_to_minna":
            if "lat" not in data or "lon" not in data:
                return jsonify({"success": False, "error": "Latitude and longitude are required"}), 400
            
            try:
                lat = parse_dms(data["lat"])
                lon = parse_dms(data["lon"])
            except ValueError as e:
                return jsonify({"success": False, "error": str(e)}), 400
            
            if not (-90 <= lat <= 90):
                return jsonify({"success": False, "error": "Latitude must be between -90 and 90 degrees"}), 400
            if not (-180 <= lon <= 180):
                return jsonify({"success": False, "error": "Longitude must be between -180 and 180 degrees"}), 400
            
            m_lat, m_lon = wgs84_to_minna(lat, lon)
            return jsonify({
                "success": True, 
                "lat": round(m_lat, 6), "lon": round(m_lon, 6),
                "lat_dms": to_dms(m_lat, True), "lon_dms": to_dms(m_lon, False)
            })

        # 2. WGS84 -> UTM (Auto Zone)
        elif conv_type == "wgs_to_utm":
            if "lat" not in data or "lon" not in data:
                return jsonify({"success": False, "error": "Latitude and longitude are required"}), 400
            
            try:
                lat = parse_dms(data["lat"])
                lon = parse_dms(data["lon"])
            except ValueError as e:
                return jsonify({"success": False, "error": str(e)}), 400
            
            if not (-90 <= lat <= 90):
                return jsonify({"success": False, "error": "Latitude must be between -90 and 90 degrees"}), 400
            if not (-180 <= lon <= 180):
                return jsonify({"success": False, "error": "Longitude must be between -180 and 180 degrees"}), 400
            
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
            if "lat" not in data or "lon" not in data:
                return jsonify({"success": False, "error": "Latitude and longitude are required"}), 400
            
            try:
                lat = parse_dms(data["lat"])
                lon = parse_dms(data["lon"])
            except ValueError as e:
                return jsonify({"success": False, "error": str(e)}), 400
            
            if not (-90 <= lat <= 90):
                return jsonify({"success": False, "error": "Latitude must be between -90 and 90 degrees"}), 400
            if not (-180 <= lon <= 180):
                return jsonify({"success": False, "error": "Longitude must be between -180 and 180 degrees"}), 400
            
            w_lat, w_lon = minna_to_wgs84(lat, lon)
            return jsonify({
                "success": True, 
                "lat": round(w_lat, 6), "lon": round(w_lon, 6),
                "lat_dms": to_dms(w_lat, True), "lon_dms": to_dms(w_lon, False)
            })

        # 4. UTM (Minna) -> WGS84
        elif conv_type == "utm_to_wgs":
            if "easting" not in data or "northing" not in data or "zone" not in data:
                return jsonify({"success": False, "error": "Easting, northing, and zone are required"}), 400
            
            try:
                e = float(data["easting"])
                n = float(data["northing"])
                zone = int(data["zone"])
            except (ValueError, TypeError):
                return jsonify({"success": False, "error": "Invalid numeric values for easting, northing, or zone"}), 400
            
            if zone not in [31, 32, 33]:
                return jsonify({"success": False, "error": "Zone must be 31, 32, or 33"}), 400
            
            if e < 0 or e > 1000000:
                return jsonify({"success": False, "error": "Easting must be between 0 and 1,000,000 meters"}), 400
            if n < 0 or n > 10000000:
                return jsonify({"success": False, "error": "Northing must be between 0 and 10,000,000 meters"}), 400
            
            lat, lon = utm_to_wgs84(e, n, zone)
            
            return jsonify({
                "success": True, 
                "lat": round(lat, 6), "lon": round(lon, 6),
                "lat_dms": to_dms(lat, True), "lon_dms": to_dms(lon, False)
            })

        # 5. MINNA (Geographic) -> MINNA UTM
        elif conv_type == "minna_to_utm":
            if "lat" not in data or "lon" not in data:
                return jsonify({"success": False, "error": "Latitude and longitude are required"}), 400
            
            try:
                lat = parse_dms(data["lat"])
                lon = parse_dms(data["lon"])
            except ValueError as e:
                return jsonify({"success": False, "error": str(e)}), 400
            
            if not (-90 <= lat <= 90):
                return jsonify({"success": False, "error": "Latitude must be between -90 and 90 degrees"}), 400
            if not (-180 <= lon <= 180):
                return jsonify({"success": False, "error": "Longitude must be between -180 and 180 degrees"}), 400
            
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

        return jsonify({"success": False, "error": "Unknown conversion type"}), 400

    except ValueError as e:
        return jsonify({"success": False, "error": f"Invalid input format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Conversion error: {str(e)}"}), 500

@app.route('/google55a2acf473e746de.html')
def google_verification():
    return "google-site-verification: google55a2acf473e746de.html"

if __name__ == "__main__":
    app.run(debug=True)


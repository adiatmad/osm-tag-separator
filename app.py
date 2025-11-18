import streamlit as st
import json
import html
from xml.etree.ElementTree import Element, SubElement, tostring

st.set_page_config(page_title="OSM GeoJSON Refiner", layout="wide")

st.title("🗂️ OSM GeoJSON Refiner + Map Preview + OSM Export")

uploaded_file = st.file_uploader("Upload GeoJSON", type=["geojson", "json"])

if uploaded_file:
    data = json.load(uploaded_file)

    if "features" not in data:
        st.error("Invalid GeoJSON.")
        st.stop()

    st.success("GeoJSON loaded!")

    # -------------------------
    # FLATTEN TAGS
    # -------------------------
    for f in data["features"]:
        props = f.get("properties", {})
        refined = {}

        for k, v in props.items():
            if isinstance(v, dict):
                for subk, subv in v.items():
                    if subv not in [None, "", " ", "null", "NULL"]:
                        refined[subk] = subv
            else:
                if v not in [None, "", " ", "null", "NULL"]:
                    refined[k] = v

        f["properties"] = refined

    st.write("### Example flattened properties")
    st.json(data["features"][0]["properties"])

    # -------------------------
    # MAP PREVIEW (Leaflet iframe)
    # -------------------------

    st.write("## 🗺️ Map Preview")

    geojson_str = html.escape(json.dumps(data))

    leaflet_html = f"""
    <html>
    <head>
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <style>html, body, #map {{ height: 100%; margin: 0; }}</style>
    </head>
    <body>
      <div id="map"></div>
      <script>
        var data = JSON.parse("{geojson_str}");
        var map = L.map('map');

        var layer = L.geoJSON(data).addTo(map);
        map.fitBounds(layer.getBounds());
      </script>
    </body>
    </html>
    """

    st.components.v1.html(leaflet_html, height=500)

    # -------------------------
    # DOWNLOAD OPTIONS
    # -------------------------

    st.write("---")
    st.write("## ⬇️ Download Refined Files")

    # GEOJSON Download
    out_geojson = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        "📥 Download as GeoJSON",
        out_geojson,
        "refined.geojson",
        "application/geo+json"
    )

    # OSM XML Download
    osm_root = Element("osm", version="0.6", generator="Streamlit-OSM-Refiner")

    node_id = -1
    for f in data["features"]:
        geom = f["geometry"]

        if geom["type"] == "Point":
            lon, lat = geom["coordinates"]
            node = SubElement(osm_root, "node", id=str(node_id),
                              lon=str(lon), lat=str(lat))

            for k, v in f["properties"].items():
                SubElement(node, "tag", k=str(k), v=str(v))

            node_id -= 1

    osm_xml = tostring(osm_root, encoding="utf-8")

    st.download_button(
        "📥 Download as .OSM XML",
        osm_xml,
        "refined.osm",
        "text/xml"
    )

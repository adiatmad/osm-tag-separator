import streamlit as st
import json
from folium import Map, GeoJson
from streamlit_folium import st_folium
from xml.etree.ElementTree import Element, SubElement, tostring

st.set_page_config(page_title="OSM GeoJSON Refiner", layout="wide")

st.title("🗂️ OSM GeoJSON Refiner + Map Preview + OSM Export")
st.write("Upload a GeoJSON → flatten tag maps → remove empty tags → preview on map → download as GeoJSON or .OSM XML.")

uploaded_file = st.file_uploader("Upload GeoJSON", type=["geojson", "json"])

if uploaded_file:
    # Load GeoJSON
    data = json.load(uploaded_file)

    if "features" not in data:
        st.error("Invalid GeoJSON.")
        st.stop()

    st.success("GeoJSON loaded successfully!")

    # ============================
    # FLATTEN TAGS
    # ============================

    new_features = []

    for feature in data["features"]:
        props = feature.get("properties", {})
        refined = {}

        for k, v in props.items():
            # Expand nested dict: "tags": {...}
            if isinstance(v, dict):
                for subkey, subval in v.items():
                    # Drop blank/empty values
                    if subval not in [None, "", " ", "null", "NULL"]:
                        refined[subkey] = subval
            else:
                # Drop blank/empty values
                if v not in [None, "", " ", "null", "NULL"]:
                    refined[k] = v

        # Replace properties
        feature["properties"] = refined
        new_features.append(feature)

    data["features"] = new_features

    st.write("### ✔ Flattened Properties Example")
    st.json(new_features[0]["properties"])

    # ============================
    # MAP PREVIEW
    # ============================

    st.write("## 🗺️ Map Preview")

    # Determine map center from first feature
    try:
        coords = data["features"][0]["geometry"]["coordinates"]
        # For Point geometry
        if data["features"][0]["geometry"]["type"] == "Point":
            lon, lat = coords
        else:
            # For Polygon / LineString: get first coord
            lon, lat = coords[0][0]
    except:
        lon, lat = (0, 0)

    m = Map(location=[lat, lon], zoom_start=14)
    GeoJson(data, name="geojson").add_to(m)

    st_folium(m, width=700, height=500)

    # ============================
    # DOWNLOAD OPTIONS
    # ============================

    st.write("---")
    st.write("## ⬇️ Download Refined Files")

    # ---- GeoJSON download ----
    out_geojson = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Download as GEOJSON",
        data=out_geojson,
        file_name="refined.geojson",
        mime="application/geo+json",
    )

    # ---- OSM XML Export ----

    # Build <osm> root
    osm_root = Element("osm", version="0.6", generator="Streamlit-OSM-Refiner")

    node_id = -1

    for feature in data["features"]:
        geom = feature["geometry"]
        props = feature["properties"]

        if geom["type"] == "Point":
            lon, lat = geom["coordinates"]
            node = SubElement(osm_root, "node", id=str(node_id), lon=str(lon), lat=str(lat))

            for k, v in props.items():
                SubElement(node, "tag", k=str(k), v=str(v))

            node_id -= 1

        # (Lines & polygons could be supported later if you want)

    osm_xml_string = tostring(osm_root, encoding="utf-8", method="xml")

    st.download_button(
        label="📥 Download as .OSM XML",
        data=osm_xml_string,
        file_name="refined.osm",
        mime="text/xml",
    )

    st.success("Conversion complete!")
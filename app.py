import streamlit as st
import json

st.set_page_config(page_title="OSM GeoJSON Tag Separator", layout="wide")

st.title("🗂️ OSM GeoJSON Tag Separator")
st.write("Upload a GeoJSON containing OSM features, and this app will explode tag maps into individual key=value properties.")

uploaded_file = st.file_uploader("Upload GeoJSON", type=["geojson", "json"])

if uploaded_file:
    # Read GeoJSON
    data = json.load(uploaded_file)

    if "features" not in data:
        st.error("Not a valid GeoJSON file.")
        st.stop()

    st.success("GeoJSON loaded!")

    st.write("### First 1–2 raw properties")
    st.json(data["features"][0]["properties"])

    new_features = []

    for feature in data["features"]:
        props = feature.get("properties", {})

        # This detects nested OSM tags such as:
        # "tags": {"building": "yes", "name": "shop"}
        refined = {}

        for k, v in props.items():
            if isinstance(v, dict):
                # Expand map → flatten
                for subkey, subval in v.items():
                    refined[subkey] = subval
            else:
                refined[k] = v

        # Assign back
        feature["properties"] = refined
        new_features.append(feature)

    data["features"] = new_features

    st.write("### Refined (flattened) properties")
    st.json(new_features[0]["properties"])

    # Save output
    out_json = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button(
        label="⬇️ Download Refined GeoJSON",
        data=out_json,
        file_name="refined.geojson",
        mime="application/geo+json"
    )

    st.success("Refined GeoJSON ready for download!")

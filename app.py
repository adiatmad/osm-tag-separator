import streamlit as st
import geopandas as gpd
import pandas as pd
import tempfile
import os
import json

st.set_page_config(page_title="OSM Tag Exploder", layout="wide")

st.title("🗺️ OSM Tag Exploder (Flatten OSM Tags Into Key=Value Fields)")
st.write("Upload an OSM dataset and produce a clean GeoJSON where all tags become separate fields.")

uploaded_file = st.file_uploader("Upload a GeoJSON, GPKG, or Shapefile (.zip)", type=["geojson", "gpkg", "zip"])

if uploaded_file:
    temp_dir = tempfile.mkdtemp()

    # --- Load file ---
    if uploaded_file.name.endswith(".zip"):
        zip_path = os.path.join(temp_dir, uploaded_file.name)
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp_dir)

        shp_files = [f for f in os.listdir(temp_dir) if f.endswith(".shp")]
        if not shp_files:
            st.error("No .shp file found inside ZIP.")
            st.stop()

        gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))

    else:
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        gdf = gpd.read_file(temp_path)

    st.success("File loaded successfully!")
    st.write("### Preview")
    st.dataframe(gdf.head())

    st.write("---")

    # --- Identify tag-like columns ---
    # Skip non-tag metadata columns
    non_tag_fields = {"geometry", "id", "osm_id", "timestamp", "changeset", "version", "osm_type"}

    potential_tags = [c for c in gdf.columns if c not in non_tag_fields]

    # Some exports store everything inside “tags” or “other_tags” as dict/map
    map_columns = [c for c in potential_tags if gdf[c].apply(lambda x: isinstance(x, dict)).any()]

    st.write("### Detected Map-Based OSM Tag Fields")
    st.code(", ".join(map_columns) if map_columns else "None found")

    # --- Explode each map field ----
    for col in map_columns:
        st.write(f"Processing tag map: `{col}` …")
        # Expand map → multiple fields
        expanded = gdf[col].apply(pd.Series)

        # Add prefix so fields don't conflict
        expanded = expanded.add_prefix(col + "_")

        # Merge into GeoDataFrame
        for newcol in expanded.columns:
            gdf[newcol] = expanded[newcol]

        # Drop original tag map
        gdf = gdf.drop(columns=[col])

    st.success("Tags expanded into individual fields!")

    st.write("### Flattened Fields")
    st.dataframe(gdf.head())

    # --- Export ---
    output_path = os.path.join(temp_dir, "refined.geojson")
    gdf.to_file(output_path, driver="GeoJSON")

    with open(output_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Refined GeoJSON",
            data=f,
            file_name="refined.geojson",
            mime="application/geo+json"
        )

    st.success("Refined GeoJSON ready!")


# OSM GeoJSON Tag Separator

A small Streamlit utility for flattening nested OSM tag objects in GeoJSON properties into individual properties.

## What it does

Upload a GeoJSON file containing OSM features. For each feature, nested dictionary properties are expanded so entries such as:

```json
{"tags": {"building": "yes", "name": "shop"}}
```

can be represented as individual properties.

The processed GeoJSON can then be downloaded as `refined.geojson`.

## Requirements

Python 3 and the packages listed in `requirements.txt`.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## License

See [LICENSE](LICENSE).

## AI-Assisted Development

This project was developed and/or maintained with AI assistance. AI was used to support parts of the design, implementation, documentation, and/or maintenance workflow. The human maintainer remains responsible for reviewing, validating, and approving the project's code and outputs.

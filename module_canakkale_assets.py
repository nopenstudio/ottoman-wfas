import os

# Enable only for builds deployed with the matching BRF installed.
custom_magazine_reload = os.environ.get("WFAS_MAGAZINE_BRF") == "1"

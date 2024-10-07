import re
def normalize_amenity(amenity):
    """Lowercase and optionally strip special characters like hyphens."""
    return re.sub(r'[^a-zA-Z0-9]', '', amenity.lower())
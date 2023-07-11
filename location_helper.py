from enum import Enum
import project_properties

class Location(Enum):
    Richmond = "RICHMOND"
    Mangalore = "MANGALORE"

def get_location_dict():
    return project_properties.locations[project_properties.location_name.value]
import haversine as hs
from geographiclib.geodesic import Geodesic
from haversine import Unit

def get_distance_to_my_address(aircraft_lat, aircraft_lon, home_lat, home_lon):
    loc1 = (home_lat,home_lon)
    loc2= (aircraft_lat, aircraft_lon)
    dist = hs.haversine(loc1,loc2,unit=Unit.MILES)
    return dist
    #return 10

def get_bearing(aircraft_lat, aircraft_lon, home_lat, home_lon):
    bearing = Geodesic.WGS84.Inverse(home_lat,home_lon, aircraft_lat, aircraft_lon)['azi1']
    return get_direction_from_bering(bearing)

def get_direction_from_bering(bearing):
    if bearing < -157.5:
        return 'S'
    if bearing < -112.5:
        return 'SW'
    if bearing < -67.5:
        return 'W'
    if bearing < -22.5:
        return 'NW'
    if bearing < 22.5:
        return 'N'
    if bearing < 67.5:
        return 'NE'
    if bearing < 112.5:
        return 'E'
    if bearing < 157.5:
        return 'SE'
    else:
        return 'S'

def get_direction_from_heading(heading):
    if heading < 22.5:
        return 'N'
    if heading < 67.5:
        return 'NE'
    if heading < 112.5:
        return 'E'
    if heading < 157.5:
        return 'SE'
    if heading < 202.5:
        return 'S'
    if heading < 247.5:
        return 'SW'
    if heading < 292.5:
        return 'W'
    if heading < 337.5:
        return 'NW'
    else:
        return 'N'
import secrets
import location_helper

city_names = {'OMDB':'Dubai, UAE','VOCI':'Kochi, India','OMSJ':'Sharjah, UAE','EDDF':'Frankfurt, Germany','UUWW':'Moscow, Russia','EGCC':'Manchester, UK','UUDD':'Moscow, Russia', 'EGKK':'London Gatwick','EGLL':'London Heathrow'}
airline_names = {'VTI':'Vistara','IAD':'Air Asia India','JZR':'Jazeera Airways','FDB':'FlyDubai','ABY':'Air Arabia','MEA':'Middle East Airlines','FLA':'Flair Airlines'}

FA_API_KEY = secrets.FA_API_KEY
OS_USERNAME = secrets.OS_USERNAME
OS_PASSWORD = secrets.OS_PASSWORD
REST_DB_URL = secrets.REST_DB_URL
CUSTOM_LOCATIONS = secrets.CUSTOM_LOCATIONS
RESTDB_XAPI_KEY= secrets.RESTDB_XAPI_KEY
dummy_data_mode = False

use_local_config = True
location_city_or_airport = 'RICHMOND'
location_boundary_box_from_center = 1
filter_by_destination = True
filter_by_origin = False


import secrets
import location_helper

city_names = {'OMDB':'Dubai, UAE','VOCI':'Kochi, India','OMSJ':'Sharjah, UAE'}
airline_names = {'VTI':'Vistara','IAD':'Air Asia India','JZR':'Jazeera Airways','FDB':'FlyDubai','ABY':'Air Arabia','MEA':'Middle East Airlines','FLA':'Flair Airlines'}

FA_API_KEY = secrets.FA_API_KEY
OS_USERNAME = secrets.OS_USERNAME
OS_PASSWORD = secrets.OS_PASSWORD
REST_DB_URL = secrets.REST_DB_URL
CUSTOM_LOCATIONS = secrets.CUSTOM_LOCATIONS
RESTDB_XAPI_KEY= secrets.RESTDB_XAPI_KEY

use_local_config = False
location_city_name = location_helper.Location.Richmond
#location_airport_code = 'HOU'
location_boundary_box_from_center = 1


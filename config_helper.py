import project_properties
import requests
import gui

def get_config_from_restio():
    print('Counter: ', gui.counter)
    if (gui.config_cache == None) | (gui.counter>5):
        gui.counter = 0
        print('Config is NONE, getting CONFIG +++++++++++++')
        config_dict = {}
        response = requests.get(project_properties.REST_DB_URL, headers = {'x-apikey': project_properties.RESTDB_XAPI_KEY})
        config_keys = response.json()
        for item in config_keys:
            config_dict[item['Key']] = item['Val']
        gui.config_cache = config_dict
        return config_dict
    else:
        gui.counter = gui.counter + 1
        print('Config exists')
        return gui.config_cache

def get_config_from_project_properties():
    return {'City':project_properties.location_city_name.value,'Width':1}

def get_config():
    if project_properties.use_local_config == True:
        return get_config_from_project_properties()
    try:
        config = get_config_from_restio()
        return config
    except Exception as e:
        print('Error fetching config: ', e)
        return get_config_from_project_properties()
import project_properties
import requests
import gui

def get_config_from_restio():
    print('Counter: ', gui.counter)
    if (gui.config_cache == None) | (gui.counter>5):
        gui.counter = 0
        print('Config is NONE, getting CONFIG +++++++++++++')
        config_dict = {}
        if project_properties.dummy_data_mode == True:
            print('CONFIG DUMMY DUMMY DUMMY DUMMY DUMMY')
            config_keys = get_dummy_config()
        else:
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

def get_dummy_config():
    return [{'_id': '64a9fc0ea1ce302000095f1c', 'Key': 'Width', 'Val': '1'}, {'_id': '649dc81aa1ce302000089012', 'Key': 'City', 'Val': 'Richmond'}]

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

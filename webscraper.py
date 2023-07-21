import requests
from bs4 import BeautifulSoup
import json, re
from datetime import datetime
import project_properties

page_url = 'https://flightaware.com/live/flight/'

def get_flight_info(flight_no):
    if project_properties.dummy_data_mode != True:
        page = requests.get(page_url + flight_no)
        soup = BeautifulSoup(page.content, "html.parser")
        try:
            destination = soup.find("meta", attrs={"name": "destination"}).get("content")
            origin = soup.find("meta", attrs={"name": "origin"}).get("content")
            aircraft_type = soup.find("meta", attrs={"name": "aircrafttype"}).get("content")
            airline = soup.find("meta", attrs={"name": "airline"}).get("content")
            scripts = soup.find_all('script')
            for script in scripts:
                if 'trackpollBootstrap' in str(script):
                    str_start = (str(script).find('{'))
                    str_end = (str(script).rfind('}'))
                    str_sliced = str(script)[str_start:str_end+1]
                    json_str = json.loads(str_sliced)
                    result = list(json_str['flights'].values())[0]
                    return {"origin":origin, "destination":destination, "aircraft_type":aircraft_type, "airline_code":airline,"airline_name":result['airline']['shortName'],"origin_city":result['origin']['friendlyLocation'],"destination_city":result['destination']['friendlyLocation'],"update_time":datetime.now() }
        except:
            raise Exception()
    else:
        print('WEBSCRAPE DUMMY DUMMY DUMMY DUMMY DUMMY')
        return {"origin":"IAH", "destination":"ORD", "aircraft_type":"737", "airline_code":"UAL","airline_name":"United","origin_city":"Houston","destination_city":"Chicago","update_time": datetime(2025, 7, 17, 18, 5, 14, 699062)}



#print(get_flight_info('UAL2629'))
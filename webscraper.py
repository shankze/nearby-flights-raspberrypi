import requests
from bs4 import BeautifulSoup
import json, re
from datetime import datetime

page_url = 'https://flightaware.com/live/flight/'

def get_flight_info(flight_no, dummy_data):
    if dummy_data== False:
        page = requests.get(page_url + flight_no)
        soup = BeautifulSoup(page.content, "html.parser")
        #print(soup)
        try:
            destination = soup.find("meta", attrs={"name": "destination"}).get("content")
            origin = soup.find("meta", attrs={"name": "origin"}).get("content")
            aircraft_type = soup.find("meta", attrs={"name": "aircrafttype"}).get("content")
            airline = soup.find("meta", attrs={"name": "airline"}).get("content")
            #print(origin, destination, aircraft_type, airline)

            #meta_tags = soup.find_all("meta")
            #for tag in meta_tags:
            #    print(tag.get("content"))
            #    print(tag)
            #    print('---')
            #vars = [json.loads(m.group(1)) for m in re.finditer(r'var trackpollBootstrap.+ = ({.*})', page.text)]

            scripts = soup.find_all('script')
            for script in scripts:
                if 'trackpollBootstrap' in str(script):
                    #print(str(script))
                    #print("-------------")
                    #jsonScript = json.loads(str(script))
                    str_start = (str(script).find('{'))
                    str_end = (str(script).rfind('}'))
                    str_sliced = str(script)[str_start:str_end+1]
                    json_str = json.loads(str_sliced)
                    result = list(json_str['flights'].values())[0]
                    #print(result['origin']['friendlyLocation'])
                    #print(result['destination']['friendlyLocation'])
                    return {"origin":origin, "destination":destination, "aircraft_type":aircraft_type, "airline_code":airline,"airline_name":result['airline']['shortName'],"origin_city":result['origin']['friendlyLocation'],"destination_city":result['destination']['friendlyLocation'],"update_time":datetime.now() }
        except:
            raise Exception()
    else:
        return {"origin":"IAH", "destination":"ORD", "aircraft_type":"737", "airline_code":"UAL","airline_name":"United","origin_city":"Houston","destination_city":"Chicago"}



#print(get_flight_info('UAL2629'))
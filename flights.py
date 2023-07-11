import json
import requests
import airport_helper
import geographic_helper
import operator_helper
import project_properties
import webscraper

dnp_equipment_codes = ['C68A','EC45','GLF4','FA20','E55P']
call_list = []
skip_airline_list = ['LIF','EJA','JSX','FFL','LXJ','DVY']
skip_equipment_list = ['C550','CL60','LJ34','LJ45','B350','SW4','H25B','E55P','C680','LJ60','C208']
flightid_skip_list = []

def get_from_flightaware(print_results=False):
    headers= {'x-apikey':project_properties.FA_API_KEY}
    query_string = "\" " + str(project_properties.SEARCH_AREA_MIN_LAT) + " " +  str(project_properties.SEARCH_AREA_MIN_LON) + " " + str(project_properties.SEARCH_AREA_MAX_LAT) + " " + str(project_properties.SEARCH_AREA_MAX_LON) + "\""
    payload = {'query':'-latlong ' + query_string + ' -filter airline','max_pages':1}
    response = requests.get("https://aeroapi.flightaware.com/aeroapi/flights/search",params=payload,headers=headers)
    if response.status_code == 200:
        flights = response.json()['flights']
        print(response.json()['links'])
        #print(len(flights))

        filtered_flights = []
        skipped_flights = []
        for flight in flights:
            if flight['ident'] == '':
                skipped_flights.append(flight['ident'])
                continue
            if flight['ident'][0] == '0':
                skipped_flights.append(flight['ident'])
                continue
            if flight['aircraft_type'] is None or flight['aircraft_type'] in dnp_equipment_codes:
                skipped_flights.append(flight['ident'])
                continue
            if flight['ident'][0] == 'N' and (flight['ident'][1]).isdigit():
                skipped_flights.append(flight['ident'])
                continue
            filtered_flights.append(flight)
        #print(len(filtered_flights))
        print(skipped_flights)

        for flight in filtered_flights:
            dist = geographic_helper.get_distance_to_my_address(flight['last_position']['latitude'],flight['last_position']['longitude'])
            flight['distance'] = dist
        sortedFlights = sorted(filtered_flights, key =lambda x:x['distance'])
        
        number_to_display = 5
        counter=0
        flights_with_data = []
        for flight in sortedFlights:
            #print(flight)
            operator_name= operator_helper.get_operator(flight['ident'],call_list)
            bearing = geographic_helper.get_bearing(flight['last_position']['latitude'],flight['last_position']['longitude'])
            origin = flight['origin']['code'] if flight['origin'] else 'NA'
            destination = flight['destination']['code'] if flight['destination'] else 'NA'
            origin_airport_name = airport_helper.get_airport_name(origin, call_list)
            destination_airport_name = airport_helper.get_airport_name(destination, call_list)
            origin_airport_text = origin + " (" + origin_airport_name + ")"
            destination_airport_text = destination + " (" + destination_airport_name + ")"
            flight_with_data = {
                "id":flight['ident'],
                "operator_name":operator_name,
                "equipment":flight['aircraft_type'],
                "origin":origin,
                "origin_city":origin_airport_name,
                "destination":destination,
                "destination_city":destination_airport_name, 
                "altitude":(flight['last_position']['altitude'])*100,
                "climb_descend":flight['last_position']['altitude_change'], 
                "distance":"{:.2f}".format(flight['distance']),
                "bearing":bearing
            }
            flights_with_data.append(flight_with_data)
            print("{:<8}".format(flight['ident']),"{:<15}".format(operator_name),"{:<40}".format(origin_airport_text),"{:<40}".format(destination_airport_text),"{:<5}".format(flight['aircraft_type']),
                "{:<8}".format((flight['last_position']['altitude'])*100),"{:<4}".format(flight['last_position']['altitude_change']),"{:.2f}".format(flight['distance']),bearing)
            counter +=1
            if counter >= number_to_display:
               break
        if print_results:
            for call in call_list:
                print(call)
        return flights_with_data

def get_city_name(airport_code,city_name):
    if airport_code in project_properties.city_names:
        return project_properties.city_names[airport_code]
    else:
        return city_name

def override_operator_if_empty(flight_id):
    if flight_id[:3] in project_properties.airline_names:
        print('Operator overriden for ', flight_id)
        return project_properties.airline_names[flight_id[:3]]
    else:
        print('No Operator override for ', flight_id)
        return None

def get_airport_info_from_json(location_code):
    with open('data/airport-info.json', 'r') as f:
        airport_info = json.load(f)
        if location_code in airport_info:
            return airport_info[location_code]
        else:
            return project_properties.CUSTOM_LOCATIONS[location_code]

def generate_url_for_opensky(location_info, to_add):
    opensky_url = "https://opensky-network.org/api/states/all?lamin=" + str(location_info['Latitude']-to_add) + "&lomin=" + str(
        location_info['Longitude']-to_add) + "&lamax=" + str(location_info['Latitude']+to_add) + "&lomax=" + str(location_info['Longitude']+to_add)
    return opensky_url

def get_from_opensky(flight_aware_cache_dict, config):
    location_info = get_airport_info_from_json(config['City'].upper())
    opensky_url = generate_url_for_opensky(location_info, float(config['Width']))
    response = requests.get(opensky_url, auth=(project_properties.OS_USERNAME,project_properties.OS_PASSWORD))
    flights = response.json()["states"]
    filtered_flights =[]
    if flights is None:
        return []
    for flight in flights:
        if flight[8] == True: #on-ground
            print('ON GROUND')
            continue
        if flight[1] == '':
            continue
        if flight[1][0] == '0':
            continue
        if flight[1][0] == 'N' and (flight[1][1]).isdigit():
            continue
        if flight[1][0:3] in skip_airline_list :
            print('Airline in Skip List')
            continue
        flight_with_data = {
            "id": flight[1],
            "altitude": int(flight[7]* 3.2808),
            "climb_descend": '-' if ((flight[11] == None) | (flight[11]==0)) else 'D' if flight[11] < 0 else 'C',
            "distance": round(geographic_helper.get_distance_to_my_address(flight[6],flight[5],location_info['Latitude'],location_info['Longitude']), 2),
            "bearing": geographic_helper.get_bearing(flight[6], flight[5],location_info['Latitude'],location_info['Longitude']),
            "flight_heading": geographic_helper.get_direction_from_heading(flight[10])
        }
        filtered_flights.append(flight_with_data)
    #print(filtered_flights)
    sortedFlights = sorted(filtered_flights, key =lambda x:x['distance'])
    counter = 0
    flight_data = []
    for flight in sortedFlights:
        try:
            if flight['id'] in flight_aware_cache_dict:
                print('IN CACHE: ',flight['id'])
                airline_details_from_fa = flight_aware_cache_dict[flight['id']]
            else:
                print('NOT IN CACHE: ', flight['id'])
                airline_details_from_fa = webscraper.get_flight_info(flight['id'], dummy_data=False)
                if airline_details_from_fa['airline_name'] == None:
                    airline_name_override = override_operator_if_empty(flight['id'])
                    if airline_name_override != None:
                        airline_details_from_fa['airline_name'] = airline_name_override
                flight_aware_cache_dict[flight['id']] = airline_details_from_fa
        except Exception as e:
            print('Error fetching info for ' + flight['id'])
            continue
        if airline_details_from_fa['airline_name'] == None:
            print('No operator for ',flight['id'])
            continue
        if airline_details_from_fa['aircraft_type'] in skip_equipment_list:
            print('Aircraft in skip list')
            continue
        flight['operator_name'] = airline_details_from_fa['airline_name']
        flight['operator_code'] = airline_details_from_fa['airline_code']
        flight['equipment'] = airline_details_from_fa['aircraft_type']
        flight['origin'] = airline_details_from_fa['origin']
        flight['origin_city'] = get_city_name(airline_details_from_fa['origin'],airline_details_from_fa['origin_city'])
        flight['destination'] = airline_details_from_fa['destination']
        flight['destination_city'] = get_city_name(airline_details_from_fa['destination'],airline_details_from_fa['destination_city'])
        flight_data.append(flight)
        counter = counter+1
        if counter>5:
            print('breaking loop---')
            break
    return flight_data



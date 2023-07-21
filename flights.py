import json
import requests
import airport_helper
import geographic_helper
import operator_helper
import project_properties
import webscraper

dnp_equipment_codes = ['C68A','EC45','GLF4','FA20','E55P'] # Not Used
call_list = []
skip_airline_list = ['LIF','EJA','JSX','FFL','LXJ','DVY','EJM','JRE','JTL','FWK']
skip_equipment_list = ['C550','CL60','LJ34','LJ45','B350','SW4','H25B','E55P','C680','LJ60','C208','GALX','C750','C56X','F2TH']
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
    if project_properties.dummy_data_mode == True:
        print('OPENSKY DUMMY DUMMY DUMMY DUMMY DUMMY')
        flights = get_dummy_opensky_response()
    else:
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
            print('Airline in Skip List: ', flight[1][0:3])
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
                airline_details_from_fa = webscraper.get_flight_info(flight['id'])
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

def get_dummy_opensky_response():
    response = [['a5999c', 'N460AA  ', 'United States', 1689649160, 1689649166, -95.2969, 29.7827, 601.98, False, 60.75, 97.79, -1.3, None, 609.6, '3020', False, 0], ['346390', 'EVE862  ', 'Spain', 1689649341, 1689649341, -96.5368, 29.6563, 11887.2, False, 253.83, 52.99, 0, None, 12580.62, '2601', False, 0], ['a33243', 'DAL1708 ', 'United States', 1689649340, 1689649341, -96.1922, 30.0902, 5623.56, False, 198.69, 280.29, 8.13, None, 6004.56, None, False, 0], ['a3b028', 'DAL1345 ', 'United States', 1689649341, 1689649341, -95.869, 29.9127, 8442.96, False, 245.03, 243.97, -5.2, None, 9006.84, '2023', False, 0], ['a385be', 'ASH6333 ', 'United States', 1689649341, 1689649341, -95.1318, 30.4788, 5958.84, False, 182.35, 24.32, 8.78, None, 6362.7, '2465', False, 0], ['a85011', 'N6348J  ', 'United States', 1689649273, 1689649341, -95.4453, 29.8262, 762, False, 57.23, 305.12, -0.65, None, 815.34, None, False, 0], ['abdc78', 'SWA836  ', 'United States', 1689649340, 1689649340, -95.4145, 29.746, 693.42, False, 92.86, 99.57, -1.63, None, 731.52, '2364', False, 0], ['a6aaba', 'DAL867  ', 'United States', 1689649340, 1689649341, -95.4103, 30.4896, 10995.66, False, 229.94, 280.83, 0, None, 11666.22, '6505', False, 0], ['ad526c', 'AAL2476 ', 'United States', 1689649340, 1689649341, -94.6979, 30.5234, 7315.2, False, 230.16, 240.4, 0, None, 7802.88, '1476', True, 0], ['a8fc72', 'UAL1528 ', 'United States', 1689649323, 1689649323, -95.1694, 30.2258, 3703.32, False, 166.98, 39.62, 4.55, None, 3749.04, None, False, 0], ['abfd39', 'SWA939  ', 'United States', 1689649341, 1689649341, -95.575, 30.0689, 8534.4, False, 245.15, 241.55, 0, None, 9098.28, '5717', False, 0], ['a0a837', 'UPS787  ', 'United States', 1689649341, 1689649341, -96.2024, 30.2982, 9525, False, 248.18, 94.4, 9.1, None, 10134.6, '2533', False, 0], ['a33a56', 'N307LJ  ', 'United States', 1689649275, 1689649275, -95.3176, 29.6777, 243.84, False, 59.3, 135.35, -3.25, None, 259.08, '4615', False, 0], ['a6a688', 'N5279F  ', 'United States', 1689649290, 1689649333, -95.4792, 29.7706, 152.4, False, 52.41, 13.63, 0, None, 160.02, '1200', False, 0], ['a298ff', 'N267AA  ', 'United States', 1689649285, 1689649338, -95.7857, 29.6698, 3200.4, False, 75.88, 349.45, -0.33, None, 3398.52, '2556', False, 0], ['abfdd1', 'AAL997  ', 'United States', 1689649340, 1689649340, -94.8186, 29.197, 11277.6, False, 260.36, 149.48, 0, None, 11971.02, '6221', False, 0], ['a56c19', 'AAL2289 ', 'United States', 1689649340, 1689649341, -94.77, 30.0787, 9761.22, False, 238.99, 282.81, 0.33, None, 10386.06, '3770', False, 0], ['a30017', 'N2926E  ', 'United States', 1689649340, 1689649341, -95.4409, 30.4854, 7315.2, False, 222.1, 222.56, 0.33, None, 7802.88, '1646', False, 0], ['ac0448', 'SWA3187 ', 'United States', 1689649341, 1689649341, -96.0063, 30.0509, 3139.44, False, 165.6, 120.63, -4.88, None, 3368.04, '3140', False, 0], ['a58a19', 'LIFE6   ', 'United States', 1689649029, 1689649029, -95.3947, 29.7145, 99.06, False, 11.93, 172.57, -4.55, None, 121.92, '0115', False, 0], ['a448d1', 'UAL8138 ', 'United States', 1689649341, 1689649341, -95.7602, 30.0045, 3208.02, False, 171.69, 283.87, 1.3, None, 3421.38, None, False, 0], ['a00f3f', 'N1025X  ', 'United States', 1689649340, 1689649341, -95.3824, 29.7941, 487.68, False, 55.08, 92.14, 0.65, None, 495.3, None, False, 0]]
    return response


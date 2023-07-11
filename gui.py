import logging
import sys
from datetime import datetime
from inspect import getsourcefile
from os.path import abspath
from os.path import exists
from guizero import *
import config_helper
import flights

counter = 0

def do_nothing():
    return 0

flight_aware_cache = {}
config_cache = None

def exception_hook(exc_type, exc_value, exc_traceback):
   logging.error(
       "Uncaught exception",
       exc_info=(exc_type, exc_value, exc_traceback)
   )
   sys.exit()

def set_up_logger():
    date_time_obj = datetime.now()
    timestamp_str = date_time_obj.strftime("%d-%b-%Y_%H_%M_%S")
    filename = './Log/crash-{}.log'.format(timestamp_str)
    logging.basicConfig(filename=filename)
    sys.excepthook = exception_hook

def display_row_in_box(flight_line, airline_name, airline_code, equipment,  origin_code,origin_city,destination_code, destination_city, altitude,climb_descend, distance,direction,flight_heading):
    flight_line.visible = True
    #flight_line = Box(app, layout="grid", border=False ,height=100,width=900, align="top")
    airline_identifier = airline_code[:3]
    airline_logo = ('./images/logos/' + airline_identifier + '.png') if exists('./images/logos/' + airline_identifier + '.png') else './images/logos/default.png'
    #airline_logo = ('C:/Repo/NearestFlightDisplay/images/logos/' + airline_identifier + '.png') if exists(
    #    './images/logos/' + airline_identifier + '.png') else './images/logos/default.png'
    airline_box = Box(flight_line,border=False,height=90,width=120,align="left",grid=[0,0])
    Text(airline_box, text=" ", align="top", size=10)
    wi_airline_logo = Picture(airline_box, image =airline_logo,align="top",width=36,height=36)
    wi_airline_name = Text(airline_box, text=airline_name,align="top", size=10)
    wi_airline_code = Text(flight_line, text=airline_code, grid=[2,0],width=8)
    wi_equipment = Text(flight_line, text=equipment, grid=[4,0],width=6)
    Text(flight_line, text=" ", grid=[5,0])
    origin_box = Box(flight_line,border=False,height=90,width=150,grid=[6,0])
    Text(origin_box, text=" ", align="top", size=12)
    wi_origin_name = Text(origin_box, text=origin_code, align="top", size=12)
    wi_origin_city = Text(origin_box, text=origin_city, align="top", size=10)
    destination_box = Box(flight_line,border=False,height=90,width=150,grid=[10,0])
    Text(destination_box, text=" ", align="top", size=12)
    wi_destination_name = Text(destination_box, text=destination_code, align="top", size=12)
    wi_destination_city = Text(destination_box, text=destination_city, align="top", size=10)
    wi_heading = Picture(flight_line, image='./images/' + flight_heading + '.png', height=35, width=40,
                               grid=[15, 0])
    wi_altitude = Text(flight_line, text=f'{round(altitude,-2):,}' , grid=[16, 0], width=8)
    wi_climb_descend = Picture(flight_line, image ='./images/'+climb_descend+'.png',height=35,width=40, grid=[18,0])
    Text(flight_line, text="    ", grid=[20, 0])
    wi_distance_direction = Text(flight_line, text=str(distance),width=12, grid=[22,0])
    wi_direction = Picture(flight_line, image='./images/D' + direction + '.png', height=35, width=40,
                               grid=[24, 0])

    return flight_line


def display_top_padding(app):
    padding_box = Box(app, align="top", width="fill", height=5)
    return padding_box

flights_list = [
    {
        "id":"UAL1",
        "operator_name":"United",
        "equipment":"B738",
        "origin":"KIAH",
        "origin_city":"Houston",
        "destination":"KAUS",
        "destination_city":"Austin", 
        "altitude":"7800",
        "climb_descend":"C", 
        "distance":"17.8",
        "bearing":"N"
    },
    {
        "id":"SWA1",
        "operator_name":"Southwest",
        "equipment":"B738",
        "origin":"KHOU",
        "origin_city":"Houston",
        "destination":"KLAX",
        "destination_city":"Los Angeles", 
        "altitude":"7800",
        "climb_descend":"-", 
        "distance":"17.8",
        "bearing":"N"
    }]


def display_flights():
    #global counter
    #counter = counter + 1
    #print('Counter: ', counter)
    #flights_list = flights.get_from_flightaware()
    print('------')
    config = config_helper.get_config()
    flights_list = flights.get_from_opensky(flight_aware_cache,config)
    box_list = [flight_line_1,flight_line_2,flight_line_3,flight_line_4,flight_line_5,flight_line_6]
    #index=0
    #for w in box_list[index].children:
    #    w.destroy()
    print('No of rows to be displayed: ', len(flights_list))
    #for flight in flights_list:
    for i in range(6):
        if i >= len(flights_list):
            box_list[i].visible = False
            continue
        flight = flights_list[i]
        display_row_in_box(box_list[i], flight["operator_name"], flight["id"], flight["equipment"],
                    flight["origin"], flight["origin_city"], flight["destination"], flight["destination_city"],
                    flight["altitude"], flight["climb_descend"], flight["distance"], flight["bearing"],flight["flight_heading"])
        #index = index+1
        #display_top_padding(app)
    """
        for flight in flights_list:
        display_row_in_box(box_list[index], flight["operator_name"], flight["id"], flight["equipment"],
                    flight["origin"], flight["origin_city"], flight["destination"], flight["destination_city"],
                    flight["altitude"], flight["climb_descend"], flight["distance"], flight["bearing"],flight["flight_heading"])
        index = index+1
        #display_top_padding(app)"""
    clear_flight_aware_cache()

def clear_flight_aware_cache():
    remove_from_cache_list = []
    for flight_id in flight_aware_cache:
        delta = datetime.now() - flight_aware_cache[flight_id]['update_time']
        if delta.total_seconds() > 500:
            remove_from_cache_list.append(flight_id)
    for flight_id in remove_from_cache_list:
        flight_aware_cache.pop(flight_id)

def say_hi():
    app.repeat(30000,display_flights)

if __name__ == '__main__':
    #set_up_logger()
    # now we will Create and configure logger

    """
    logging.basicConfig(filename="std.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    # Let us Create an object
    logger = logging.getLogger()
    # Now we are going to Set the threshold of logger to DEBUG
    logger.setLevel(logging.DEBUG)
    logger.critical("The Internet is not working....")
    """
    print(abspath(getsourcefile(lambda:0)))

    #location_dict = project_properties.locations[location]

    app = App(title="Nearby Flights", height=600, width=1000)
    app.bg = "white"
    flight_line_1 = Box(app, layout="grid", border=False, height=100, width=940, align="top")
    padding_box_1 = Box(app, align="top", width="fill", height=2)
    flight_line_2 = Box(app, layout="grid", border=False, height=100, width=940, align="top")
    padding_box_2 = Box(app, align="top", width="fill", height=2)
    flight_line_3 = Box(app, layout="grid", border=False, height=100, width=940, align="top")
    padding_box_3 = Box(app, align="top", width="fill", height=2)
    flight_line_4 = Box(app, layout="grid", border=False, height=100, width=940, align="top")
    padding_box_4 = Box(app, align="top", width="fill", height=2)
    flight_line_5 = Box(app, layout="grid", border=False, height=100, width=940, align="top")
    padding_box_5 = Box(app, align="top", width="fill", height=2)
    flight_line_6 = Box(app, layout="grid", border=False, height=100, width=940, align="top")
    padding_box_6 = Box(app, align="top", width="fill", height=2)

    display_flights()




    app.after(10000, say_hi)
    app.display()








'''
flight_one = Box(app, layout="grid", border=True ,height=100,width=900, align="top")
airline_name = Text(flight_one, text="UA", grid=[0,0])
airline_code = Text(flight_one, text="UA1", grid=[1,0])
origin_name = Text(flight_one, text='IAH', grid=[2,0])
destination_name = Text(flight_one, text='AUS', grid=[3,0])

top_pad = Box(app, align="top", width="fill", height=5)

flight_two = Box(app, layout="grid", border=True ,height=100,width=900, align="top")
airline_name = Text(flight_two, text="UA", grid=[0,0])
airline_code = Text(flight_two, text="UA2", grid=[1,0])
origin_name = Text(flight_two, text='IAH', grid=[2,0])
destination_name = Text(flight_two, text='AUS', grid=[3,0])

top_pad = Box(app, align="top", width="fill", height=5)

flight_three = Box(app, layout="grid", border=True ,height=100,width=900, align="top")
airline_name = Text(flight_three, text="UA", grid=[0,0])
airline_code = Text(flight_three, text="UA3", grid=[1,0])
origin_name = Text(flight_three, text='IAH', grid=[2,0])
destination_name = Text(flight_three, text='AUS', grid=[3,0])
'''
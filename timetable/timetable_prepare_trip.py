import orjson, csv

def list_to_dict(headers, list):
    return_dict = dict()
    for i in range(len(list)):
        return_dict[headers[i]] = list[i]
    return return_dict

def get_gtfs_stop_times(path):

    trips = dict()

    f = open(path + "/stop_times.txt", "r", encoding="UTF8")
    stop_time_rows = list(csv.reader(f))
    for stop_time_row in stop_time_rows:
        if stop_time_row == stop_time_rows[0]:
            headers = stop_time_row
        else:
            stop_time = list_to_dict(headers, stop_time_row)
            if stop_time["trip_id"] not in trips:
                trips[stop_time["trip_id"]] = list()
            trips[stop_time["trip_id"]].append(stop_time)
            
    return trips

def get_gtfs_routes(path):

    routes = dict()

    f = open(path + "/routes.txt", "r", encoding="UTF8")
    route_rows = list(csv.reader(f))
    for route_row in route_rows:
        if route_row == route_rows[0]:
            headers = route_row
        else:
            route = list_to_dict(headers, route_row)
            routes[route["route_id"]] = route
        
    return routes

def get_gtfs_agencies(path):

    agencies = dict()

    f = open(path + "/agency.txt", "r", encoding="UTF8")
    agency_rows = list(csv.reader(f))
    for agency_row in agency_rows:
        if agency_row == agency_rows[0]:
            headers = agency_row
        else:
            agency = list_to_dict(headers, agency_row)
            agencies[agency["agency_id"]] = agency
        
    return agencies

def get_gtfs_trips(path):

    trips = list()

    f = open(path + "/trips.txt", "r")
    trip_rows = list(csv.reader(f))
    for trip_row in trip_rows:
        if trip_row == trip_rows[0]:
            headers = trip_row
        else:
            trips.append(list_to_dict(headers, trip_row))


    return trips

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

trips = get_gtfs_trips("data/gtfs")

routes = get_gtfs_routes("data/gtfs")

for trip in trips:
    trip["route"] = routes[trip["route_id"]]
del routes

print("routes added")

agencies = get_gtfs_agencies("data/gtfs")

for trip in trips:
    trip["agency"] = agencies[trip["route"]["agency_id"]]
del agencies

print("agencies added")

stop_times = get_gtfs_stop_times("data/gtfs")

for trip in trips:
    trip["stops"] = stop_times[trip["trip_id"]]
    export = open(f"timetable/trip/trip_{trip["trip_id"]}.json", 'wb')
    export.write(orjson.dumps(trip, default=set_default))
    print(trip["trip_id"] + " has been exported")
    del trip
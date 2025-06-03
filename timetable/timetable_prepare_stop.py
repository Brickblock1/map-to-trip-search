import json, csv

def list_to_dict(headers, list):
    return_dict = dict()
    for i in range(len(list)):
        return_dict[headers[i]] = list[i]
    return return_dict

def get_gtfs_stops(path):

    stops = dict()

    f = open(path + "/stop_times.txt", "r")
    stop_time_rows = list(csv.reader(f))
    for stop_time_row in stop_time_rows:
        if stop_time_row == stop_time_rows[0]:
            headers = stop_time_row
        else:
            stop_time = list_to_dict(headers, stop_time_row)
            if stop_time["stop_id"] not in stops:
                stops[stop_time["stop_id"]] = dict()
            if "pickup" not in stops[stop_time["stop_id"]]:
                stops[stop_time["stop_id"]]["pickup"] = set()
            if "drop_off" not in stops[stop_time["stop_id"]]:
                stops[stop_time["stop_id"]]["drop_off"] = set()
            if stop_time["pickup_type"] != "1":
                stops[stop_time["stop_id"]]["pickup"].add(stop_time["trip_id"])
            if stop_time["drop_off_type"] != "1":
                stops[stop_time["stop_id"]]["drop_off"].add(stop_time["trip_id"])
            
    return stops 

stops = get_gtfs_stops("data/gtfs")

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


for stop in stops.items():
    export = open(f"timetable/stop/lines_stop_{stop[0]}.json", 'w', encoding="UTF8")
    json.dump(stop[1], export, indent=2, default=set_default)
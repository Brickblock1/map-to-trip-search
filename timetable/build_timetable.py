import orjson, argparse

parser = argparse.ArgumentParser(description='Build a timetable', add_help=True)

parser.add_argument("stop1", help="Rikshållplatsnummer of orgin stop")
parser.add_argument("stop2", help="Rikshållplatsnummer of destination stop")

args = parser.parse_args()

if len(args.stop1) != 9 and args.stop1.startswith("74"):
    raise ValueError("stop1 is not a rikshållplats")

if len(args.stop2) != 9 and args.stop1.startswith("74"):
    raise ValueError("stop2 is not a rikshållplats")

stop_1_file = open(f"timetable/stop/lines_stop_{args.stop1}.json", "r", encoding="UTF8")
stops_1 = orjson.loads(stop_1_file.read())["pickup"]


stop_2_file = open(f"timetable/stop/lines_stop_{args.stop2}.json", "r", encoding="UTF8")
stops_2 = orjson.loads(stop_2_file.read())["drop_off"]

shared_trips = list()

for trip in stops_1:
    if trip in stops_2:
        shared_trips.append(trip)

# We make sure that the secound stop isn't first as that would mean having the trip backwards

trip_list = list()

for trip in shared_trips:
    trip_file = open(f"timetable/trip/trip_{trip}.json", "r", encoding="UTF8")
    trip_data = orjson.loads(trip_file.read())
    for stop in trip_data["stops"]:
        if stop["stop_id"] == args.stop2:
            break
        if stop["stop_id"] == args.stop1:
            trip_list.append(trip_data)
            break

# we sort departures so that it looks right

def sort_time(trip):
    for stop in trip["stops"]:
        if stop["stop_id"] == args.stop1:
            return int(stop["departure_time"].replace(":", ""))
        
    Exception("could not find stop1 in trip")

trip_list.sort(key=sort_time)

header_stops = list()

for trip in trip_list:
    trip_start = False
    for stop in trip["stops"]:
        if stop["stop_id"] not in header_stops:
            if stop["stop_id"] == args.stop2:
                break
            elif trip_start == True:
                header_stops.append(stop["stop_id"])
            elif stop["stop_id"] == args.stop1:
                trip_start = True
                header_stops.append(stop["stop_id"])

header_stops.append(args.stop2)

def build_stops_header(header_stops):
    string = ""
    for stop in header_stops:
        string = string + f"<th>{stop}</th>"

    return string


table = f"<tr><th>Fordon</th><th>Linje</th><th>Mot</th><th>Dag</th>{build_stops_header(header_stops)}</tr>\n"

for trip in trip_list:
    if trip["route"]["route_long_name"] != "":
        route_name = trip["route"]["route_long_name"]
    else:
        route_name = f"<a href='{trip["agency"]["agency_url"]}' target='_blank'>{trip["agency"]["agency_name"]}</a> {trip["route"]["route_short_name"]}"

    stops = ""


    for stop_header in header_stops:
        stop_time = None
        for stop_trip in trip["stops"]:
            if stop_header == stop_trip["stop_id"]:
                stop_time_split = stop_trip["departure_time"].split(":")
                if int(stop_time_split[0]) >= 24:
                    stop_time = f"{str(int(stop_time_split[0]) - 24)}:{stop_time_split[1]}:{stop_time_split[2]}"
                else:
                    stop_time = stop_trip["departure_time"]

        if stop_time == None:
            stop_time = "-"

        stops = stops + f"<td>{stop_time}</td>"

        if int(trip["route"]["route_type"]) in range(100, 199):
            vehicle = "Tåg"
        elif int(trip["route"]["route_type"]) in range(200, 299):
            vehicle = "Långdistansbuss"
        elif int(trip["route"]["route_type"]) in range(400, 499):
            vehicle = "Tunnelbana"
        elif int(trip["route"]["route_type"]) in range(700, 799):
            vehicle = "Buss"
        elif int(trip["route"]["route_type"]) in range(800, 899):
            vehicle = "Trådbuss"
        elif int(trip["route"]["route_type"]) in range(900, 999):
            vehicle = "Spårvagn"
        elif int(trip["route"]["route_type"]) in range(1000, 1099) or range(1200, 1299):
            vehicle = "Båt"
        elif int(trip["route"]["route_type"]) in range(1100, 1199):
            vehicle = "Flyg"
        elif int(trip["route"]["route_type"]) in range(1300, 1399):
            vehicle = "Kabinbana"
        elif int(trip["route"]["route_type"]) in range(1400, 1499):
            vehicle = "Bergbana"
        elif int(trip["route"]["route_type"]) in range(1500, 1599):
            vehicle = "Taxi"
        elif int(trip["route"]["route_type"]) in range(1700, 1799):
            vehicle = "Annat"

    table = table + f"<tr><td>{vehicle}</td><td>{route_name}</td><td>{trip["trip_headsign"]}</td><td>Okänt</td>{stops}</tr>\n"


html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timetable builder</title>
    <link rel="stylesheet" href="timetable.css">
</head>
<body>
<h1>Tidtabel {args.stop1} -> {args.stop2}</h1>
<table>
{table}
</table>
</body>
</html>"""

export_html = open("timetable_export.html", "w", encoding="UTF8")
export_html.write(html)


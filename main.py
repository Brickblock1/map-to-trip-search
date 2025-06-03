import os, xmltodict, json, csv

import get_data
import util.stopplace as sp
import util.quays as qy

data_source = True

print("Started")

def extend_id(id):
    x = id.find("_")
    if x != -1:
        for i in range(6 - x):
            id = "0" + id
        a = id.split("_")
        id = "9021050" + a[0] + "000_" + a[1]
    else:
        id = int(id) +  9021050000000
        id = str(id) + "000"

    return id

def convert_extra_stopplaces(stopplaces):
    extra_stopplace_dict = {}
    print("converting stopplaces")
    for stopplace in stopplaces:
        id = stopplace["@id"]
        #pos = id.rfind(":")
        #id = id[pos+1:]
        #id = extend_id(id)
        extra_stopplace_dict[id] = stopplace

    return extra_stopplace_dict

def add_stops(file, extra_file=None):

    print("fetching stops from: " + file)
    filtered_stops = list()
    stopplace_dict = {}

    # open the main file and convert it to a dict

    with open(file, "r", encoding="UTF8") as file:
        data = file.read()
    data = xmltodict.parse(data)

    # get its stopplaces

    stopplaces = data["PublicationDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]

    # if avaliable open the extra file and convert it to a dict
    
    if extra_file != None:
        with open(extra_file, "r", encoding="UTF8") as file:
            extra_data = file.read()
        extra_data = xmltodict.parse(extra_data)

        # get its stopplaces

        extra_stopplaces = extra_data["PublicationDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]

        extra_stopplace_dict = convert_extra_stopplaces(extra_stopplaces)
    else:
        extra_stopplace_dict = None

    # do this for every stopplace

    for s in range(0, len(stopplaces)):
        if s % 100 == 0:
            print(s)
        stopplace = stopplaces[s]
        id = stopplace["@id"]
        pos = id.rfind(":")
        id = id[pos+1:]
        stopplace_dict[id] = sp.Stopplace(stopplace, used_quays, extra_stopplace_dict = extra_stopplace_dict)

        # make the parent station inuse if a child is and add all transport modes since Östgötatrafiken are dumb.

        if stopplace_dict[id].parentsiteref != None:
            transportmode = stopplace_dict[stopplace_dict[id].parentsiteref].transportmode + stopplace_dict[id].transportmode
            stopplace_dict[stopplace_dict[id].parentsiteref].transportmode = transportmode
            if stopplace_dict[stopplace_dict[id].parentsiteref].inuse == False:
                stopplace_dict[stopplace_dict[id].parentsiteref].inuse = stopplace_dict[id].inuse

    for stopplace in stopplace_dict.values():
        if stopplace.parentsiteref == None:    
            filtered_stops.append(stopplace.toJSON())

    return filtered_stops

class Main:

    def __init__(self, data_folder):
        self.data_folder = data_folder

    def add_stops(self):

        self.stopplaces = add_stops(self.data_folder + "/_stops.xml", self.data_folder + "/_stops.xml")
        
        print("stops have been added")

    def save_quays(self):

        print("writing used stops")

        f = open("quays.json", "w", encoding="utf-8")
        f.write(json.dumps(list(self.quays)))

    def get_saved_quays(self):
        f = open("quays.json", "r", encoding="utf-8")
        data = f.read()
        self.quays = set(json.loads(data))

    def get_quays(self, folder):
        self.quays = qy.get_lines(folder)

        self.save_quays()

    def get_gtfs_stops(self, gtfs_path):
        gtfs_stops = list()
        f = open(gtfs_path + "/stop_times.txt", "r")
        stop_ref_rows = list(csv.reader(f))
        for stop_ref_row in stop_ref_rows:
            if stop_ref_row == stop_ref_rows[0]:
                pos = stop_ref_row.index("stop_id")
            else:
                gtfs_stops.append(stop_ref_row[pos])
        self.gtfs_stops =  gtfs_stops

    def write_stops_data(self):
        f =  open("stops.json", "w", encoding="utf-8")
        f.write(json.dumps(self.stopplaces, indent=1))

if False:
    get_data.getData("")

resplus = Main("data/netex")
resplus.add_stops()
resplus.write_stops_data()
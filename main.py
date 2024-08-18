import os, xmltodict

#Define coordinates of where we want to center our map
start_coords = [59.6060, 17.7786]
data_source = True

print("Started")

def get_quays(routes):
    inusequays = set()

    if type(routes) != dict:
        for route in routes:
            pointsonroute = route["pointsInSequence"]["PointOnRoute"]
            for p in pointsonroute:
                quay = p["RoutePointRef"]["@ref"]
                pos = quay.rfind(":")
                pos = len(quay) - pos + 1
                quay = quay[pos:]
                inusequays.add(quay)
    else:
        pointsonroute = routes["pointsInSequence"]["PointOnRoute"]
        for p in pointsonroute:
            quay = p["RoutePointRef"]["@ref"]
            pos = quay.rfind(":")
            pos = len(quay) - pos + 1
            quay = quay[pos:]
            inusequays.add(quay)
    return inusequays

def get_lines(folder):
    removefromfiles = []
    returnset = set() 

    files = os.listdir("NeTex_data/" + folder) #list all files
    for filename in files:
        substrings = filename.split("_")
        if substrings[0] != "line": #check if file is a line
            removefromfiles.append(filename)

    for f in removefromfiles: #remove files without line from list
        files.remove(f)

    for filename in files:
        print("fetching lines from: " + filename)
        with open("NeTex_data/" + folder + "/" + filename, 'r', encoding="UTF8") as file:
            data = file.read()
        data = xmltodict.parse(data)
        routes = data["PublicationDelivery"]["dataObjects"]["CompositeFrame"]["frames"]["ServiceFrame"]["routes"]["Route"]
        returnset = returnset | get_quays(routes)
    
    return returnset

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

def get_extra_data(add, extra_stopplace_dict):
    global data_source
    if extra_stopplace_dict != None:
        try:
            keylist = extra_stopplace_dict[add.id]["keyList"]
        except:
            if data_source == True: 
                print("data-source does not contain keylist data")
                data_source = False
        else:
            keyvalue = keylist["KeyValue"]
            for key in keyvalue:
                if key["Key"] == "sellable":
                    add.sellable = key["Value"]
                if key["Key"] == "owner":
                    add.owner = str(key["Value"])
                if key["Key"] == "rikshallplats":
                    add.rikshallplats = key["Value"]
                if key["Key"] == "uicCode":
                    add.rikshallplats = key["Value"]
    
    return add

def convert_extra_stopplaces(stopplaces):
    extra_stopplace_dict = {}
    print("converting stopplaces")
    for stopplace in stopplaces:
        id = stopplace["@id"]
        pos = id.rfind(":")
        id = id[pos+1:]
        id = extend_id(id)
        extra_stopplace_dict[id] = stopplace

    return extra_stopplace_dict

class Stopplace:
    def __init__(self, stopplace, used_quays, extra_stopplace_dict=None):
        global data_source

        id = stopplace["@id"]
        pos = id.rfind(":")
        self.id = id[pos+1:]

        # get name regardless of language

        self.name = stopplace["Name"]
        if type(self.name) == dict:
            self.name = self.name["#text"]

        # get location

        self.lat = stopplace["Centroid"]["Location"]["Latitude"]
        self.long = stopplace["Centroid"]["Location"]["Longitude"]

        # get weighting if it exists

        try: 
            self.weighting = stopplace["Weighting"]
        except:
            self.weighting = None

        # get the parent if it exists 

        try:
            self.parentsiteref = stopplace["ParentSiteRef"]["@ref"]
        except:
            self.parentsiteref = None
        else:
            pos = self.parentsiteref.rfind(":")
            self.parentsiteref = self.parentsiteref[pos+1:]

        #data avaliable from the extra file

        self.rikshallplats = None
        self.owner = None
        self.sellable = "false"

        # get the data from the extra file

        get_extra_data(self, extra_stopplace_dict)
        
        # test if data from said file exists

        if self.owner == None:
            self.owner = 'inget'
        if self.rikshallplats == None:
            self.rikshallplats = '0'
        if self.weighting == "preferredInterchange":
            self.group_id = self.weighting
        elif self.owner == "50":
            self.group_id = "Utland"
        else:
            self.group_id = self.owner

        # check if stop is used by any line

        self.inuse = False
        quays = []
        try:
            stop_quays = stopplace["quays"]["Quay"]
        except:
            stop_quays = None
        else:
            if type(stop_quays) == list:
                for q in stop_quays:
                    quay = q["@id"]
                    pos = quay.rfind(":")
                    quay = quay[pos+1:]
                    quays.append(quay)
            else:
                    quay = stop_quays["@id"]
                    pos = quay.rfind(":")
                    quay = quay[pos+1:]
                    quays.append(quay)

        self.quays = quays

        if len(used_quays) != 0:
            for q in quays:
                if q in used_quays:
                    self.inuse = True
        else:
                    self.inuse = True
    
    def __str__(self):
        return self.name, self.owner, self.inuse, self.id

def add_stops(file, used_quays, extra_file=None):

    print("fetching stops from: " + file)
    map_script = ""
    group_ids = set()
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
        stopplace_dict[id] = Stopplace(stopplace, used_quays, extra_stopplace_dict = extra_stopplace_dict)

        # make the parent station inuse if a child is

        if stopplace_dict[id].parentsiteref != None and stopplace_dict[stopplace_dict[id].parentsiteref].inuse == False:
            stopplace_dict[stopplace_dict[id].parentsiteref].inuse = stopplace_dict[id].inuse
            id = stopplace_dict[id].parentsiteref

        if stopplace_dict[id].parentsiteref == None and stopplace_dict[id].inuse == True and stopplace_dict[id].rikshallplats != "0":

             # create layer from group_id if it doesn't exist alredy

            if stopplace_dict[id].group_id not in group_ids:
                if stopplace_dict[id].group_id == "preferredInterchange":
                    map_script = map_script + "\n\tvar o_" + stopplace_dict[id].group_id + " = L.layerGroup([]).addTo(map);\n\tlayerControl.addOverlay(o_" + stopplace_dict[id].group_id + ", '" + stopplace_dict[id].group_id + "');"
                else:
                    map_script = map_script + "\n\tvar o_" + stopplace_dict[id].group_id + " = L.markerClusterGroup({disableClusteringAtZoom: 13,});\n\tlayerControl.addOverlay(o_" + stopplace_dict[id].group_id + ", '" + stopplace_dict[id].group_id + "');"
                group_ids.add(stopplace_dict[id].group_id)

            # create the marker with colour based on sellable status

            phtml = """<h5>""" + stopplace_dict[id].name +  """</h5><h6>""" + """</h6><p onclick=\\"set_orgin('""" + stopplace_dict[id].name + "','" + stopplace_dict[id].rikshallplats + """')\\" ><a>res från</a></p><p onclick=\\"set_destination('""" + stopplace_dict[id].name + "','" + stopplace_dict[id].rikshallplats + """')\\"><a>res till</a></p>"""

            if stopplace_dict[id].sellable == "true":
                map_script = map_script + "\n\tvar marker = L.marker([" + stopplace_dict[id].lat + ", " + stopplace_dict[id].long + "], {icon: greendot}).addTo(o_" + stopplace_dict[id].group_id + "); marker.bindPopup(\"" + phtml + "\");"
            else:
                map_script = map_script + "\n\tvar marker = L.marker([" + stopplace_dict[id].lat + ", " + stopplace_dict[id].long + "], {icon: reddot}).addTo(o_" + stopplace_dict[id].group_id + "); marker.bindPopup(\"" + phtml + "\");"

    return map_script

def write_stops_data(from_folder, used_quays, extra_file=None):
    data = add_stops("NeTex_data/" + from_folder + "/_stops.xml", used_quays, extra_file=extra_file)
    with open(from_folder + ".js", "w", encoding="utf-8") as f2:
        f2.write(data)

with open("header.html", "r") as h:
    header = h.read()

with open("header_script.html", "r") as hs:
    header_script = hs.read()

headtobody = """
</head>
<body>
"""

with open("navbar.html", "r") as n:
    body = n.read()

bodytoscript = """
</body>
<script>
"""

map_script = "\tvar map = L.map('map', {\n\t\tcenter: " + str(start_coords) + ",\n\t\tzoom: 10,\n\t\tworldCopyJump: true}); \n\tL.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19, attribution: '&copy; <a href=\"http://www.openstreetmap.org/copyright\">OpenStreetMap</a>'}).addTo(map); \n\tvar greendot = L.icon({iconUrl: 'green_dot.png', iconSize: [16, 16],}); \n\tvar reddot = L.icon({iconUrl: 'red_dot.png', iconSize: [16, 16],});\n\tvar layerControl = L.control.layers({},{},{sortLayers: true},).addTo(map);\n\tset_trip();"
htmlend = """
</script>
<script src="sweden.js"></script>
</html>
"""

#<script src="sj.js"></script>

folder = "Sweden"
#used_quays = get_lines(folder)

#with open("quays.txt", "w", encoding="utf-8") as f:
#    f.write(str(used_quays))

with open("quays.txt", "r", encoding="UTF8") as file:
    used_quays = file.read()
used_quays = used_quays.replace("{", "")
used_quays = used_quays.replace("}", "")
used_quays = used_quays.replace("'", "")
used_quays = used_quays.split(", ")
used_quays = set(used_quays)

write_stops_data(folder, used_quays, extra_file="NeTex_data/Stops/extra_stops.xml")
print("stops have been added")

full_html = header +  header_script + headtobody + body + bodytoscript + map_script + htmlend
# write html file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

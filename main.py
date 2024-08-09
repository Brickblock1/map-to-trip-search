import folium, numpy
from folium.utilities import JsCode
from folium import *
import pandas as pd
import os, xmltodict

#Define coordinates of where we want to center our map
start_coords = [59.6060, 17.7786]

print("Started")

def add_stops_new(file, map_script):

    print("fetching stops from: " + file)

    with open(file, "r", encoding="UTF8") as file:
        data = file.read()

    adict = {}
    data = xmltodict.parse(data)
    data = data["PublicationDelivery"]
    data = data["dataObjects"]
    siteframe = data["SiteFrame"]
    stopplaces = siteframe["stopPlaces"]
    stopplaces = stopplaces["StopPlace"]
    for s in range(0, len(stopplaces)):
        if s % 100 == 0:
            print(s)
        stopplace = stopplaces[s]
        name = stopplace["Name"]
        if type(name) == dict:
            name = name["#text"]
        centroid = stopplace["Centroid"]
        try: 
            weighting = stopplace["Weighting"]
        except:
            weighting = None
        try:
            parentsiteref = stopplace["ParentSiteRef"]
            parentsiteref = parentsiteref["@ref"]
        except:
            parentsiteref = None
        location = centroid["Location"]
        lat = location["Latitude"]
        long = location["Longitude"]
        rikshallplats = None
        owner = None
        sellable = "false"
        try:
            keylist = stopplace["keyList"]
        except:
            print("data-source does not contain keylist data")
        else:
            keyvalue = keylist["KeyValue"]
            for k in range(0, len(keyvalue)):
                key = keyvalue[k]
                if key["Key"] == "sellable":
                    sellable = key["Value"]
                if key["Key"] == "owner":
                    owner = str(key["Value"])
                if key["Key"] == "rikshallplats":
                    rikshallplats = key["Value"]
                if key["Key"] == "uicCode":
                    rikshallplats = key["Value"]
        
        if owner == None:
            owner = 'inget'
        if rikshallplats == None:
            rikshallplats = '0'
        if weighting == "preferredInterchange" or weighting == "recomendedInterchange":
            group_id = weighting
        elif owner == "50":
            group_id = "Utland"
        else:
            group_id = owner
        
        phtml = """<p onclick=\\"set_orgin('""" + name + "','" + rikshallplats + """')\\" ><a>res från</a></p><p onclick=\\"set_destination('""" + name + "','" + rikshallplats + """')\\"><a>res till</a></p>"""

        if parentsiteref == None:
            try:
                str(adict[group_id])
            except:
                if group_id == "prefeeredInterchange":
                    map_script = map_script + "\n\tvar o_" + group_id + " = L.layerGroup([]).addTo(map);"
                else:
                    map_script = map_script + "\n\tvar o_" + group_id + " = L.layerGroup([]);\n\tlayerControl.addOverlay(o_" + group_id + ", '" + group_id + "');"
                adict[group_id] = True
            finally: 
                if sellable == "true":
                    map_script = map_script + "\n\tvar marker = L.marker([" + lat + ", " + long + "], {icon: greendot}).addTo(o_" + group_id + "); marker.bindPopup(\"" + phtml + "\");"
                else:
                    map_script = map_script + "\n\tvar marker = L.marker([" + lat + ", " + long + "], {icon: reddot}).addTo(o_" + group_id + "); marker.bindPopup(\"" + phtml + "\");"
    return map_script

zoom_func = JsCode(
    """
    function zoom() {
        if (map.getZoom() <10){
            map.removeLayer();
        }
        else {
            map.addLayer();
        }
    }
"""
)

with open("header.html", "r") as h:
    header = h.read()


with open("header_script.html", "r") as hs:
    header_script = hs.read()

#test = str(my_map.get_root().render())

headtobody = """
</head>
<body>
"""

body = """
    <div class=\"flex-container\" style=\"height: 100%; flex-direction: column;\">
        <div class=\"flex-container\" style=\"flex-wrap: wrap; height: auto;\">
            <h1>Brickblock1\'s map to trip search</h1>
            <a title=\"Sök resa hos Vy\" class=\"navbar\" type=\"button\", onclick=\"redirect_vy()\">Vy<span><img src=\"https://www.vy.se/images/favicon.png\"></span></a>
            <a title=\"Sök resa hos Resrobot\" class=\"navbar\" type=\"button\", onclick=\"redirect_resrobot()\">Resrobot<span><img src=\"https://resrobot.se/favi.ico\"></span></a>
            <p id=\"trip\"></p>
        </div>
        <div id="map"></div>
    </div>
"""

bodytoscript = """
</body>
<script>
"""

map_script = "\tvar map = L.map('map', {\n\t\tcenter: " + str(start_coords) + ",\n\t\tzoom: 10,\n\t\tworldCopyJump: true}); \n\tL.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19, attribution: '&copy; <a href=\"http://www.openstreetmap.org/copyright\">OpenStreetMap</a>'}).addTo(map); \n\tvar greendot = L.icon({iconUrl: 'green_dot.png', iconSize: [16, 16],}); \n\tvar reddot = L.icon({iconUrl: 'red_dot.png', iconSize: [16, 16],});\n\tvar layerControl = L.control.layers().addTo(map);"

htmlend = """
</script>
</html>
"""

map_script = add_stops_new("_stops.xml", map_script)
map_script = add_stops_new("tiamat-export-Current-202407132300011943.xml", map_script)
print("stops have been added")

full_html = header +  header_script + headtobody + body + bodytoscript + map_script + htmlend
# write file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

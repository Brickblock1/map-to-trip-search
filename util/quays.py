import os, xmltodict

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

    files = os.listdir(folder) #list all files
    for filename in files:
        substrings = filename.split("_")
        if substrings[0] != "line": #check if file is a line
            removefromfiles.append(filename)

    for f in removefromfiles: #remove files without line from list
        files.remove(f)

    for filename in files:
        print("fetching lines from: " + filename)
        with open(folder + "/" + filename, 'r', encoding="UTF8") as file:
            data = file.read()
        data = xmltodict.parse(data)
        routes = data["PublicationDelivery"]["dataObjects"]["CompositeFrame"]["frames"]["ServiceFrame"]["routes"]["Route"]
        returnset = returnset | get_quays(routes)
    
    return returnset
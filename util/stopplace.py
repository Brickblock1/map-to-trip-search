class Stopplace:
    def __init__(self, stopplace, used_quays, extra_stopplace_dict=None):

        self.id = stopplace["@id"]

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

        # get transportmode if it exists

        try: 
            self.transportmode = [stopplace["TransportMode"]]
        except:
            self.transportmode = None

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
        self.sellable = False

        # get the data from the extra file

        self.get_extra_data(extra_stopplace_dict)

        # check if stop is used by any line

        self.inuse = False
        quays = []
        try:
            stop_quays = stopplace["quays"]["Quay"]
        except:
            stop_quays = list()
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

        if self.netex_inuse(used_quays):
            self.inuse = True
    
    def __str__(self):
        return self.name, self.owner, self.inuse, self.id
    
    def toJSON(self):
        return {"name": self.name, "id": self.id, "rikshallplats": self.rikshallplats, "weight": self.weighting, "transportmode": self.transportmode, "owner": self.owner, "inuse": self.inuse, "sellable": self.sellable, "lat": self.lat, "long": self.long, }

    def netex_inuse(self, used_quays):
        for quay in self.quays:
            if quay in used_quays:
                return True
            else:
                return False
            
    def get_extra_data(self, extra_stopplace_dict):
        if extra_stopplace_dict != None:
            try:
                keylist = extra_stopplace_dict[self.id]["keyList"]
            except:
                raise Exception("Data-source does not contain keylist data")
            else:
                keyvalue = keylist["KeyValue"]
                for key in keyvalue:
                    if key["Key"] == "sellable":
                        self.sellable = key["Value"]
                    if key["Key"] == "owner":
                        self.owner = str(key["Value"])
                    if key["Key"] == "rikshallplats":
                        self.rikshallplats = key["Value"]
                    if key["Key"] == "rikshallplatsNummer":
                        self.rikshallplats = key["Value"]
                    if key["Key"] == "uicCode":
                        self.rikshallplats = key["Value"]
        
        return self

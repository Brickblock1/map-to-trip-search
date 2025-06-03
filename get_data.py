import os, requests, zipfile, io

#apikey = open("key", "r", encoding="utf8").read()

#data_url = f"https://opendata.samtrafiken.se/netex-access/samtrafikensales_latest.zip?key={apikey}"

#data_dir = "data/netex"

class getData:

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def deleteold(self):

        #remove old files in case some route has disapered

        for file in os.listdir(self.data_dir):
            os.remove(f"{self.data_dir}/{file}")

        print("Removed old files")

    def get(self, data_url):

        print("Downloading feed")

        response = requests.get(data_url)

        if response.status_code != 200:
            raise Exception("Status-code was not 200")

        print("Data downloaded successfully")

        #Save zipfile contents to memory 

        zip_file = io.BytesIO(response.content)

        self.unzip(zip_file)

    def unzip(self, zip_file):

        self.deleteold()

        #Extract it to the data dir

        zipfile.ZipFile(zip_file, "r").extractall(self.data_dir)

        print("Extracted files")

#getData("").unzip("timetable_prepare_stop.zip")






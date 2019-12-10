import urllib.request
from bs4 import BeautifulSoup, element
import requests

class CarScraper:

    GENERIC_CAR_SEARCH_URL = "https://www.citymotorgroup.co.nz/cars/?VehicleType=0&Make=0&Model=0&YearMin=2006&YearMax=2019&PriceMin=0&PriceMax=60985&Keywords={0}&OdometerMin=0&OdometerMax=220001&Colour=0&Doors=0&Fuel=0&Transmission=0&Sort=AZ" 

    GENERIC_COMMERCIAL_SEARCH_URL = "https://www.citymotorgroup.co.nz/commercials/?VehicleType=0&Make=0&Model=0&YearMin=2006&YearMax=2019&PriceMin=0&PriceMax=60985&Keywords={0}&OdometerMin=0&OdometerMax=220001&Colour=0&Doors=0&Fuel=0&Transmission=0&Sort=AZ"

    def get_photo(self, soup, name):
        container = soup.find_all("img")

        imgsrc = "nonefound"
        
        for img in container:
            if img["src"].startswith("/assets/Vehicles/_resampled/"):
                imgsrc = img["src"]
                break

        if imgsrc != "nonefound":
            try:
                full_url = "https://www.citymotorgroup.co.nz" + imgsrc
                print(full_url)
                print()
                urllib.request.urlretrieve(full_url, name + imgsrc[-3:])
            except urllib.error.HTTPError:
                print("Couldn't get Car URL: Forbidden")

    def get_name(self, soup):
        container = soup.find_all("div", class_ = "vehicle-page__text__title-container")
        name = container[0].h1.text
        return name


    def get_total_price(self, soup):
        container = soup.find_all("span", class_ = "vehicle-page__text__price-container__price")
        price = container[0].text

        price = price.replace("*", "")

        return price

    def get_weekly_price(self, soup):
        container = soup.find_all("span", class_ = "vehicle-page__text__price-container__weekly")
        
        texts = []
        for item in container[0].children:
            if isinstance(item, element.NavigableString):
               texts.append(item) 

        # This may not work on other Weekly Prices!
        price = texts[0]

        price = price.replace("*", "")
        price = price.replace("\n", "")

        return price

    def get_details(self, soup):
        container = soup.find_all("div", class_="vehicle-specs__specification")
        
        for spec in container:
            text = spec.dl.dt.text
            value = spec.dl.dd.text
            if "Odometer" in text:
                odometer = value.replace("\n", "")

            if "CCs" in text:
                ccs = value.replace("\n", "")

            if "Fuel Type" in text:
                fuel_type = value.replace("\n","")

            if "Transmission" in text:
                trans = value.replace("\n", "")

        return odometer, ccs, fuel_type, trans

    def scrape_car(self, url):
        response = requests.get(url)

        html_soup = BeautifulSoup(response.text, 'html.parser')

        name                            = self.get_name(html_soup)
        total_price                     = self.get_total_price(html_soup)
        weekly_price                    = self.get_weekly_price(html_soup)
        odometer, ccs, fuel_type, trans = self.get_details(html_soup)

        vehicle_row = [name, total_price, weekly_price, ccs, fuel_type, odometer, trans, url]

        print(vehicle_row)
        
        v = Vehicle(vehicle_row)

        return vehcile_row

    def search_page(self, generic_search_url, id_number):
        ''' 
            This takes from the generic search page and find the associated car page for the id.
        '''
        search_url = generic_search_url.format(id_number)

        print("Requesting Page...")
        response = requests.get(search_url)

        soup = BeautifulSoup(response.text, 'html.parser')

        container = soup.find("article", class_ = "vehicle-preview FavouriteObject")

        return container

    def convert_search(self, id_number):
        # First search for cars:
        print("Checking CARS Search Page...")
        container = self.search_page(self.GENERIC_CAR_SEARCH_URL, id_number)

        # If not found, check the Commercial Vehicles
        if container == None:
            print("\n>>> !No matching cars.\nSearching COMMERCIAL VEHICLES")
            container = self.search_page(self.GENERIC_COMMERCIAL_SEARCH_URL, id_number)

        # If it is still not found, print so and give up.
        if container == None:
            print("\n>>> !No matching Commercials with ID: {0}.".format(id_number))
            return "ID: {0} Not Found".format(id_number) 

        print("Vehicle Found. Getting Vehicle Page URL")
        # Else we have found it and we can strip it.
        vehicle_ref = ""

        a = container.find("a", href=True)

        vehicle_ref = a["href"]

        generic_vehicle_url = "https://www.citymotorgroup.co.nz{0}"

        vehicle_url = generic_vehicle_url.format(vehicle_ref)

        return vehicle_url

    
class HTMLFormatter:
    '''
    Transfers the Car details into the Email Template.
    @param vehicle_rows a list of lists, containing car details.
    '''
    def __init__(self, vehicle_rows):
        self.vehicle_rows = vehicle_rows
        
        # Index of which s3copyX each detail is.
        index = {
            "CCs": 5,
            "Fuel Type": 6,
            "Odo": 7,
            "Trans": 8,
            "Price per Week": 9
        }
        
    def 
        

import csv
import datetime as dt

vehicle_ids = str(input("File with car IDs. > "))
print("Reading urls from file...")

urls = []

cs = CarScraper()

with open(vehicle_ids, "r") as open_file:
    reader = csv.reader(open_file)

    for id in reader:
        # Every row is a list, and the first item is the ID
        id = id[0]
        print("ID: {0}".format(id))
        url = cs.convert_search(id)
        urls.append(url)

car_csvs = "car-details-{0}.csv".format(
    dt.datetime.now().strftime("%x").replace("/", "-")
)

print("Writing car rows to {0}".format(car_csvs))

with open(car_csvs, "w") as open_file:
    writer = csv.writer(open_file)

    for url in urls:
        if url.startswith("ID: "): # This is the start of the string that says the ID wasn't found.
            writer.writerow(url)
        else:
            writer.writerow(cs.scrape_car(url))

print("done")

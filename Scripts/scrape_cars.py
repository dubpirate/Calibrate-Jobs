import csv
import urllib.request
from bs4 import BeautifulSoup, element
import requests

def get_photo(soup, name):
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
            print("Forbidden")

def get_name(soup):
    container = soup.find_all("div", class_ = "vehicle-page__text__title-container")
    name = container[0].h1.text
    return name


def get_total_price(soup):
    container = soup.find_all("span", class_ = "vehicle-page__text__price-container__price")
    price = container[0].text

    price = price.replace("*", "")

    return price

def get_weekly_price(soup):
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

def get_details(soup):
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

def scrape_car(url):
    response = requests.get(url)

    html_soup = BeautifulSoup(response.text, 'html.parser')

    name = get_name(html_soup)
    total_price = get_total_price(html_soup)
    weekly_price = get_weekly_price(html_soup)
    odometer, ccs, fuel_type, trans = get_details(html_soup)

    car_row = [name, total_price, weekly_price, ccs, fuel_type, odometer, trans, url]

    print(car_row)

    return car_row

# Script begins

urls = []

print("Reading urls from urls.csv")
with open("urls.csv", "r") as open_file:
    reader = csv.reader(open_file)

    for row in reader:
        print(row)
        urls.append(row[0])

print("Writing car rows to cars.csv")
with open("cars.csv", "w") as open_file:
    writer = csv.writer(open_file)
    
    for url in urls:
        writer.writerow(scrape_car(url))

print("done")

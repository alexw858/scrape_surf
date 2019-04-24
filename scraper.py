from splinter import Browser
from bs4 import BeautifulSoup
import pymongo
import datetime
import random
import time

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Initialize headless browser
def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser('chrome', **executable_path, headless=False)

def scraper():

    surf_spots = {}

    browser = init_browser()

    url = "https://www.surfline.com/surf-reports-forecasts-cams/costa-rica/3624060"
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    '''Grab surf spot name, wave height and link from the main overview page'''
    # surf_spots["name"] = soup.find_all("h3", class_="sl-spot-details__name")
    # surfline updated their class names
    surf_spots["name"] = soup.find_all("h3", class_="quiver-spot-details__name")
    surf_spots["waves"] = soup.find_all("span", class_="quiver-surf-height")
    surf_spots["link"] = soup.find_all("a", class_="sl-cam-list-link")

    '''Check if 'surf_db' already exists.  If it does, drop it'''
    dbnames = client.database_names()
    if 'surf_db' in dbnames:
        client.drop_database('surf_db')

    # Declare the 'surf_db' database
    db = client.surf_db
    # Declare the 'surf_summary' collection
    collection = db.surf_summary

    '''Loop through each element and gather text one at a time.  Surf spot name, wave size and the link can be found in the area overview page. The rest is spot-specific'''
    posts = []
    for x in range(len(surf_spots["name"])):
        # added
        # print("spot:", surf_spots["name"][x], "sets:", surf_spots["waves"][x].get_text().split('-')[0])
        # check to see if surf conditions have at least two values (eg. is not "Flat")
        if len(surf_spots["waves"][x].get_text().split('-')) >= 2:
            posts.append({
                'name' : surf_spots["name"][x].get_text(), 
                'small_sets' : surf_spots["waves"][x].get_text().split('-')[0]+'FT', 
                'big_sets' : surf_spots["waves"][x].get_text().split('-')[1], 
                # the link to the surf spot's page. This will be used both to navigate to the page to grab spot-specific water and air temp, as well as providing the user
                # a link to visit the page on the dashboard if they want more information (also worth noting that I had a multi-line comment here with triple quotes and that
                # broke my code)
                'link' : "https://www.surfline.com" + surf_spots["link"][x].get("href"), 
                # 'date' : datetime.datetime.utcnow()
                # get the current time in the format year, month, day, hour, minute
                'date' : datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
        # run if surf conditions have only one value ("Flat")
        else:
            posts.append({
                'name' : surf_spots["name"][x].get_text(), 
                'small_sets' : surf_spots["waves"][x].get_text().split('-')[0], 
                # also adding info into big_sets entry, since removing it doesn't remove the whole entry
                'big_sets' : surf_spots["waves"][x].get_text().split('-')[0], 
                'link' : "https://www.surfline.com" + surf_spots["link"][x].get("href"), 
                # 'date' : datetime.datetime.utcnow()
                'date' : datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })

    '''loop through each url stored in posts, visit the url, grab the water and air temps, 
    add the data into each dictionary'''
    for item in posts:
    # for testing purposes use this to just loop through the first 3 links:
    # for item in posts[:3]:
        # this is where I will try adding a time.sleep line:
        a=(random.random()+1) * 5
        print("Waiting on overview page for", a, "seconds")
        time.sleep(a)
        browser.visit(item["link"])
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        # this section is the next on my list to fix: air and water temps not returning correct values
        # print("water temps: ",soup.find("div", class_="sl-wetsuit-recommender__conditions__water").get_text().split(" "))
        # example: water temps:  ['Water', 'Temp84', '-', '86', 'ºF']
        # item["low_water_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__water").get_text().split(" ")[0]
        item["low_water_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__water").get_text().split(" ")[1][4:]
        # item["high_water_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__water").get_text().split(" ")[2]
        item["high_water_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__water").get_text().split(" ")[3]
        # item["air_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__weather").get_text().split(" ")[3][2:]
        # print("air temp[7:9]:", soup.find("div", class_="sl-wetsuit-recommender__conditions__weather").get_text()[7:9])
        # item["air_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__weather").get_text()[0]
        item["air_temp"] = soup.find("div", class_="sl-wetsuit-recommender__conditions__weather").get_text()[7:9]
        print("time:", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        # Will add code below to mimic a real user more closely
        # wait a second time to mimic the user looking at the spot-specific page
        b=(random.random()+1) * 5
        print("Waiting on spot page for", b, "seconds")
        time.sleep(b)
        # navigate back to the main overview page - there are no links to other nearby spots so this is likely what a real user would do
        browser.back()

    '''loop through each post (one per surf spot), upload one-by-one to MongoDB'''
    for post in posts:
        collection.insert_one(post)

def main():
    scraper()
    print("Finished running scraper.py")

main()
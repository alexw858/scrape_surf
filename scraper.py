from splinter import Browser
from bs4 import BeautifulSoup
import pymongo
import datetime

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

    surf_spots["name"] = soup.find_all("h3", class_="sl-spot-details__name")
    surf_spots["waves"] = soup.find_all("span", class_="quiver-surf-height")
    surf_spots["link"] = soup.find_all("a", class_="sl-cam-list-link")

# Check if 'surf_db' already exists.  If it does, drop it
    dbnames = client.database_names()
    if 'surf_db' in dbnames:
        client.drop_database('surf_db')

    # Declare the 'surf_db' database
    db = client.surf_db
    # Declare the 'surf_summary' collection
    collection = db.surf_summary

    '''loop through each element and gather text one at a time'''
    posts = []
    for x in range(len(surf_spots["name"])):
        posts.append({
            'name' : surf_spots["name"][x].get_text(), 
            'small_sets' : surf_spots["waves"][x].get_text().split('-')[0]+'FT', 
            'big_sets' : surf_spots["waves"][x].get_text().split('-')[1], 
            'link' : "https://www.surfline.com" + surf_spots["link"][x].get("href"), 
            'date' : datetime.datetime.utcnow()
        })
    '''loop through each url stored in posts, visit the url, grab the water and air temps, 
    add the data into each dictionary'''
    for item in posts:
        browser.visit(item["link"])
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        item["low_water_temp"] = soup.find("div", class_="sl-wetsuit-recommender__weather").get_text().split(" ")[0]
        item["high_water_temp"] = soup.find("div", class_="sl-wetsuit-recommender__weather").get_text().split(" ")[2]
        item["air_temp"] = soup.find("div", class_="sl-wetsuit-recommender__weather").get_text().split(" ")[3][2:]

    '''loop through each post (one per surf spot), upload one-by-one to MongoDB'''
    for post in posts:
        collection.insert_one(post)

def main():
    scraper()
    print("Finished running scraper.py")

main()
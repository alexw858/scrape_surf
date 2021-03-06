from flask import Flask, render_template, redirect
import pymongo

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# create instance of Flask app
app = Flask(__name__)

# connect to surf database, created with scraper.py
# db= getattr(client, surf_db)
db=client.surf_db
collection = db.surf_summary

@app.route("/")
def home():

    # Find data
    reports = collection.find({})

    # return template and data
    return render_template("index.html", reports=reports)

if __name__ == "__main__":
    # app.config.update(DEBUG=True, TEMPLATES_AUTO_RELOAD=True)
    app.run(debug=True)
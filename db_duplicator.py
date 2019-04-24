# duplicating and even renaming databases in Mongo is very difficult, I will just make another one with a new name
# it's also unclear where I would even run these commands.  I thought at first I could run using PyMongo 
# some say run in mongo shell, some say run in command prompt.  neither worked for me

# import pymongo

# conn = 'mongodb://localhost:27017'
# client = pymongo.MongoClient(conn)

# Depricated, no longer works
# db = client.surf_db
# db.copyDatabase("surf_db", "surf_db_legacy", "localhost")

# dumps all collections in the surf_db database
mongodump -d surf_db -o mongodump/

# mongorestore
#     --host localhost:27017
#     --db surf_db dump/surf_db_legacy

mongorestore -d surf_db_legacy mongodump/surf_db

# mongorestore --nsInclude 'surf_db.*' --nsFrom 'surf_db.*' --nsTo 'surf_db_legacy'
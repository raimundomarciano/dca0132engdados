import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["newdatabase"]
mycol = mydb["newcollection"]

x = mycol.find_one()

print(x) 
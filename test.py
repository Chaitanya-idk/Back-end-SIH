from pymongo import MongoClient


MONGO_URI = "mongodb+srv://gitftwsih:actkas@clustersih.snppid6.mongodb.net/"

client = MongoClient(MONGO_URI)


print("Databases:", client.list_database_names())


db = client["SIH"]


print("Collections in SIH:", db.list_collection_names())


main_collection = db["main"]
print("\nDocuments in 'main':")
for doc in main_collection.find():
    print(doc)

import googlemaps
from pymongo import MongoClient, GEO2D
from rest_framework.response import Response

from sean_backend.settings import MONGODB_CONNECTING_STRING, MONGODB_NAME


def get_mongodb_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = MONGODB_CONNECTING_STRING

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[MONGODB_NAME]


# def distance_google_map(pickup, destination):
#
#     # Requires API key
#     gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)
#     origin = pickup
#     destination = destination
#     # Requires cities name
#     my_dist = gmaps.distance_matrix(origin, destination, mode='driving')['rows'][0]['elements'][0]
#
#     # Printing the result
#     return my_dist

def update_location(user, latitude, longitude):
    try:
        user_id = user.id
        latitude = latitude
        longitude = longitude
        dbname = get_mongodb_database()
        collection_name = dbname["TestCollection"]
        list_index_check = list(collection_name.list_indexes())
        if len(list_index_check) == 0:
            collection_name.create_index([("TestCollection", GEO2D)])
        index_check = collection_name.index_information()
        if index_check:
            get_index = index_check.get('TestCollection_2d')
            if get_index is None:
                collection_name.create_index([("TestCollection", GEO2D)])

        user_found = collection_name.find({"user_id": user_id})
        user_in_db = list(user_found)
        if len(user_in_db) == 0:
            collection_name.insert_one({"user_id": user_id, "location": [float(latitude), float(longitude)]})
        else:
            myquery = user_in_db[0]
            new_values = {"$set": {"user_id": user_id, "location": [float(latitude), float(longitude)]}}
            collection_name.update_one(myquery, new_values)
    except Exception as e:
        error = {"status": False, "message": e.args[0]}
        return Response(error)

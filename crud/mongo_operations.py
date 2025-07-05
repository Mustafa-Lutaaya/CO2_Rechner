from pymongo.collection import Collection # Imports the type hint for MongoDB collection
from collections import defaultdict # Imports defaultdict to group data by category
from datetime import datetime # Imports date time Library for recording timestamps

# MONGO OPERATIONS
class MongoCRUD:
    # Initializes the MongoCRUD instance witj references to the MongoDB collection
    def __init__(self, co2: Collection, sos: Collection, logs: Collection):
        self.co2 = co2 # For item  data
        self.sos = sos # For session logs
        self.logs = logs # For user activity logs

    # Groups item records from the SQl into a structured category to send to MongoDB
    def group_data_by_category(self, items):
        grouped = defaultdict(list) # Creates a dictionary where each key is a category and the value is a list of items

        # Adds item details into the category group
        for item in items:
            grouped[item.category].append({
                "name": item.name,
                "base_co2": item.base_co2,
                "count": 0, # Default count value
                "co2": 0 # Default CO2 value
            })
        
        desired_order = ["UNTERTEILE", "OBERTEILE", "ACCESSORIES", "JACKEN", "EINTEILER & SCHUHE"]
        # Converts the grouped dictionary into a list of dictionaries
        return [
            {"category": category, "items": grouped[category]} 
                for category in desired_order
                if category in grouped
                ]
    
    # Inserts grouped category-item data inzo the MongoDB 'co2' collection
    def send_to_mongo(self, grouped_items):
        if grouped_items:
            self.co2.insert_many(grouped_items)
        return grouped_items

    # Updates a specific item's count & CO" value in Mongo DB by using $inc operator to increment values efficiently
    def update_item(self, category, item_name, count, co2):  
        self.co2.update_one(
            {"category": category, "items.name": item_name}, # Filters to find the correct category & item
            {"$inc": { # $inc is used to increment the values
                "items.$.count": count, # Increments the count by the specified value
                "items.$.co2": co2, # Increments the co2 by the specified value
            }}
        )
    
    # Retrieves all documents from the 'co2' collection to prepare them for display
    def get_updated_items(self):
        return list(self.co2.find())
    
    # Resets count & co2 fields to 0 in eachh category document to prepare for a new session
    def reset_counts(self, items):
        for category in items:
             # For each category, performs an update on the MongoDB collection
            self.co2.update_one(
                {"category": category["category"]}, # Filters the document based on category
                {"$set":{
                    "items":[ # Updates the 'items' field in the document
                        {**item, # Copies all key-value pairs from item then overwrites them.
                         "count":0,  # Reset 'count' to 0
                         "co2":0 # Resets 'co2' to 0
                         }  
                        for item in category["items"]  # Loops through each item in the category
                    ]
                }}
            )
    # Inserts a new exchange as a list inside a document into the 'Session' collection session into the 'sos' collection
    def insert_session(self, total_co2, equivalents, exc_items):
        session = {
            "timestamp": datetime.now(),  # Records the exact time of the exchange
            "ingesamt": round(total_co2, 2),  # Total CO2 value for this session
            "wieauto": round(equivalents['wieauto'], 2),  # Equivalent CO2 in car travel
            "wieflugzeug": round(equivalents['wieflugzeug'], 2),  # Equivalent CO2 in flight
            "wiebus": round(equivalents['wiebus'], 2),  # Equivalent CO2 in bus travel
            "exc_items": exc_items # Exchanged Items
        }
        self.sos.insert_one({"session": [session]}) 

    # Retrieves all session documents from the collection as a list
    def get_all_sessions(self):
        return list(self.sos.find())
    
    # Deletes all session documents in the 'sos' collection
    def clear_sessions(self):
        self.sos.delete_many({})

    # Inserts the events logs as a list inside a document into the 'Event_Logs' collection after capturing the timestamp, user identity, number of sessions, sorted item usage and CO2 totals.  
    def log_out(self,  sessions, sorted_items, total):
            logs = {
                "timestamp": datetime.now(),  # Records the exact time of logout
                "sessions": sessions, # Adds number of sessions
                "sorted_items": sorted_items, # Adds sorted items
                "total": total # Adds total as well
            }
            self.logs.insert_one({"Logs": [logs]})            
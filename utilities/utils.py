from operator import itemgetter # Sorts specific dictionary values by key.
from datetime import datetime #  Used to get the current date and time

class AppUtils:
    # Method to returns current date & time in selected format
    @staticmethod
    def current_time():
        return datetime.now().strftime('%Y-%m-%d %H:%M') 
    
    # Method to calculate CO2 equivalents for different modes of transport
    @staticmethod
    def calculate_equivalents(total_co2): 
        return{
            "wieauto": round(total_co2 / (170.65 / 1000), 2), # 0.2Kg CO2 per Km
            "wieflugzeug": round(total_co2 / (181.59 / 1000), 2), # 0.2Kg CO2 per Km
            "wiebus": round(total_co2 /(27.33 / 1000), 2) # 0.05Kg CO2 per Km
        }
    
    # Method to flatten nested MongoDB documents into a list of item dictionaries for simplified rendering
    @staticmethod
    def rearrange_updated_items(co2_docs:list):
        rearranged = []

        # Iterates over each document & its items list retrieved from MongoDB 
        for obj in co2_docs:
            for item in obj['items']:
                # Appends each item as a dictionary with only the relevant fields
                rearranged.append({
                    "name": item['name'],
                    "count":item['count'],
                    "co2": item.get("co2",0)
                })
        return rearranged 

    # Method to flatten and sort the fetched uodated items by 'count in descending order
    @staticmethod
    def sort_updated_items(updated_items): 
        return sorted(updated_items, key=itemgetter('count'), reverse=True)
    
    # Method to return calculated totals and session counts from documents
    @staticmethod
    def calculate_total(session_list):
        totals = {"ingesamt": 0, "wieauto": 0, "wieflugzeug": 0, "wiebus": 0}
        session_count = 0
        for doc in session_list:  # Loops through all stored sessions in the Database to calculate cumulative totals and number of sessions
                session = doc['session'][0]
                totals["ingesamt"] += session.get("ingesamt", 0)
                totals["wieauto"] += session.get("wieauto", 0)
                totals["wieflugzeug"] += session.get("wieflugzeug", 0)
                totals["wiebus"] += session.get("wiebus", 0)
                session_count += 1 # Each time the for loop finds a doc, the session count is increased by 1

        # Rounds off all totals to 2 decimal places before returning
        for key in totals:
            totals[key] = round(totals[key], 2)

        return totals, session_count
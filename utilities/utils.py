from datetime import datetime  # For timestamps
from sqlalchemy.orm import Session  # For database transactions
from fastapi import Request  # To extract request context 
from typing import Dict, Any, Optional  # For typing hints
from models.models import AuditLog  # Imports the AuditLog ORM model
from operator import itemgetter # Sorts specific dictionary values by key.
from datetime import datetime #  Used to get the current date and time

# Utility class for recording audit logs into the database
class AuditLogger:
    # Function to create an audit log entry and save it into the database
    @staticmethod
    def log_action(
        db: Session,
        action: str,  # Name of the action performed (e.g., "create_category", "delete_item")
        resource_type: str,  # Type of resource being modified (e.g., "Category", "Item")
        resource_id: str = None,  # ID of the resource (optional, if applicable)
        user_id: int = None,  # ID of the user performing the action
        admin_id: int = None,
        status: str = "success",  # Status of the action ("success" or "failure")
        details: Dict[str, Any] = None,  # Extra details about the operation in dictionary format
        error_message: str = None,  # Error message if action failed
        request: Optional[Request] = None  # Request object for extracting IP, headers, etc.
    ):
        # Collects request context if available
        ip_address = request.client.host if request else None  # Extracts client IP address
        user_agent = request.headers.get("user-agent") if request else None  # Extracts browser or client info
        endpoint = request.url.path if request else None  # Extracts request URL endpoint
        method = request.method if request else None  # Extracts HTTP method used (GET, POST, etc.)

        # Creates new audit log entry ORM object
        log = AuditLog(
            user_id=user_id,  # Stores user ID if provided
            action=action,  # Records the action performed
            resource_type=resource_type,  # Records the type of resource affected
            resource_id=str(resource_id) if resource_id else None,  # Stores resource ID if present
            ip_address=ip_address,  # Logs IP address from request
            user_agent=user_agent,  # Logs user agent string from headers
            method=method,  # Logs HTTP method (GET/POST/etc.)
            details=details or {},  # Logs additional details as JSON/dict
            status=status,  # Logs whether action was success or failure
            error_message=error_message,  # Logs error message if applicable
            timestamp=datetime.utcnow()  # Logs exact UTC time of the action
        )

        db.add(log)  # Adds the log to the current database session
        db.commit()  # Commits transaction to save permanently into the database
        db.refresh(log)  # Refreshes the log object with DB-generated values (like ID)
        return log  # Returns the created audit log object for reference


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
    
# Utility function to print debug messages to the console for development purposes
def debug_print(msg, value=None):
    # Prints a message with value if provided, otherwise prints only the message
    if value is not None:
        print(f"[DEBUG] {msg}: {value}")
    else:
        print(f"[DEBUG] {msg}")
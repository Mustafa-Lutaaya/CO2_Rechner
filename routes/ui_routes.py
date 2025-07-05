# FastAPI Components to build the web app.
from fastapi import APIRouter, Request, Form # Imports FastAPI , Request for handling HTTP requests & Form to accept data submitted via POST Requests
from fastapi.responses import HTMLResponse, RedirectResponse, Response # Specifies that a route returns HTML
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support

# Utilities & Database Connection Classes
from dotenv import load_dotenv # Loads secrets from .env.
from pathlib import Path # Provides object-oriented file system paths
from utilities.utils import AppUtils # Imports the data processing functions
from database.data import SessionLocal, Base, engine, Co2 # Imports SQLAlchemy engine connected to the database, dependency function to provide DB Session and declarative Base for models to create tables
from crud.local_operations import LocalCRUD
from crud.mongo_operations import MongoCRUD
from crud.sql_operations import SQLCRUD

# Creates tables using SQLAlchemy
Base.metadata.create_all(bind=engine)

# Loads enviroment variables from .env file to retrieve sensitive data securely
load_dotenv() # Loads secrets

# Initializes FastAPI Web Application
router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder

# Mongo DB Initialization
mongo_client = Co2()

# Initializes CRUD instances
local = LocalCRUD()
sql = SQLCRUD()
mongo = MongoCRUD(co2=mongo_client.co2, sos=mongo_client.sos, logs=mongo_client.logs)

# Loads items from the SQL Database
with SessionLocal() as db:
    items = sql.fetch_items_from_sql(db)

# Groups the items 
grouped_items = mongo.group_data_by_category(items)

# Inserts Items into Mongo DB co2 Database if documents empty
if mongo.co2.count_documents({}) == 0:
    mongo.send_to_mongo(grouped_items)

items = grouped_items

# DEMO PAGE ROUTES
# Route for the demopage ('/') that returns an HTML response displaying items
@router.get("/", response_class=HTMLResponse)
def demo(request: Request):

    # Calculates the total CO2 emission based on item's counts and CO2 per item
    total_co2 = sum(
        (item.get('co2', 0))
        for category in items
        for item in category['items'])
    
    equivalents = AppUtils.calculate_equivalents(total_co2)  # Calculates how mmuch C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "items": items,  # Passes items data to be rendered
        "equivalents": equivalents, # C02 equivalent in different modes of transport
        "total_co2": total_co2, # Total C02 emitted based on selected items
    }
    # Renders the response
    response = templates.TemplateResponse("demo.html", context)
    return response 

# Route to handle form submissions of incrementing & decrementing counts on demo page
@router.post("/", response_class=HTMLResponse)
def update_count(request: Request, action: str = Form(...), item_name: str = Form(...)): # request:Request accesses headers & cookies while the Form(...) tells FastAPI value must come from a form field
    local.update_item_count(items, item_name, action)
    return RedirectResponse(url="/", status_code=303) # Redirects back to homepage after form submission to display updated data & to prevent resubmission on refresh

# Route to reset all items locally
@router.post("/reset", response_class=HTMLResponse)
def renew(request: Request):
    local.reset_items(items)
    return RedirectResponse(url="/", status_code=303) # Redirects back to demo page

# MAIN PAGE ROUTES 
# Route for the homepage ('/main') that returns an HTML response displaying items
@router.get("/main", response_class=HTMLResponse)
def main(request: Request):

    global total_co2

    # Calculates the total CO2 emission based on item's counts and CO2 per item
    total_co2 = sum(
        (item.get('co2', 0))
        for category in items
        for item in category['items'])
    
    equivalents = AppUtils.calculate_equivalents(total_co2)  # Calculates how mmuch C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function
    totals, session_count = AppUtils.calculate_total(mongo.get_all_sessions()) # Gets All Sessions Function loops through all stored sessions in the Database, then passes them to AppUtils, calculates total function to calculate cumulative totals and number of sessions
    updated_items = mongo.get_updated_items() # Fetches the latest items data from the MongoDB database
    rearranged_items = AppUtils.rearrange_updated_items(updated_items)  # Single Lists MongoDB items
    sorted_items = AppUtils.sort_updated_items(rearranged_items) # Sorts items by 'count' in descending order with most used items coming first

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "items": items,  # Passes items data to be rendered
        "equivalents": equivalents, # C02 equivalent in different modes of transport
        "total_co2": total_co2, # Total C02 emitted based on selected items
        "totals": totals, # Cumulative totals of all sessions
        "session_count": session_count,  # Number of sessions stored
        "sorted_items": sorted_items, # Sorted list of updated items for display
    }
    # Renders the response
    return templates.TemplateResponse("main.html", context)

# Route to handle form submissions of incrementing & decrementing counts
@router.post("/main", response_class=HTMLResponse)
def update_count(request: Request, action: str = Form(...), item_name: str = Form(...)): # request:Request accesses headers & cookies while the Form(...) tells FastAPI value must come from a form field
    local.update_item_count(items, item_name, action)
    return RedirectResponse(url="main", status_code=303)  # Redirects back to homepage after form submission to display updated data & to prevent resubission on refresh

# Route to save items data to database and reset all items locally
@router.post("/main/reset", response_class=HTMLResponse)
def renew(request: Request):
    # Saves all items data from session to database before resetting
    try:
        exc_items = {} 

        # Update items and collects exchanged items
        for category in items:
            for item in category['items']:
                if item.get('count', 0) > 0 or item.get('co2', 0) > 0: # Tries to get 'CO2', if it doesn't exist, it returns 0 instead , to prevent crashes
                    mongo.update_item(category["category"], item["name"], item['count'], item['co2']) # Updates items count and CO2 by category using the MongoCO2 class defined function
                    
                    # Ensures a list exists for each category
                    if category['category'] not in exc_items:
                        exc_items[category["category"]] = []
                    
                    exc_items[category["category"]].append({
                        "name": item["name"],
                        "count": item["count"],
                        "co2": item["co2"]
                    })

        # Inserts session data if any CO2 was saved
        if total_co2 > 0:
            equivalents = AppUtils.calculate_equivalents(total_co2)  # Calculates how much C02 is equivalent to driving a car, riding a bus or flying in a plane using the AppUtils calculate session function
            mongo.insert_session(total_co2, equivalents, exc_items) # Inserts exchanged items and sessions for a participant

        # Resets locally displayed items
        local.reset_items(items)

    except Exception as e:
        print(f"Error in /reset: {e}")
        raise e
    
    return RedirectResponse(url="/UI/main", status_code=303) # Redirects back to mainpage


# Route to save events data to database and reset all items locally
@router.post("/main/logout", response_class=HTMLResponse)
def logout(request: Request):

    # Checks if there were actual calculations during sessions
    totals, session_count = AppUtils.calculate_total(mongo.get_all_sessions()) # Gets All Sessions Function loops through all stored sessions in the Database, then passes them to AppUtils, calculates total function to calculate cumulative totals and number of sessions

    # If data was exchanged during the event, then its collected and saved into the logs event collection
    if session_count > 0:
        updated_items = mongo.get_updated_items() # Fetches the latest items data from the MongoDB database
        rearranged_items = AppUtils.rearrange_updated_items(updated_items)  # Single Lists MongoDB items
        sorted_items = AppUtils.sort_updated_items(rearranged_items) # Sorts items by 'count' in descending order with most used items coming first
        mongo.log_out(sessions=session_count, sorted_items=sorted_items, total=totals)
        mongo.reset_counts(items) # Resets items database count 
        mongo.clear_sessions() # Deletes all documents inside the sessions collection

    # Prepares redirect response 
    return RedirectResponse(url="/UI", status_code=303) 

    
# SECURE ROUTES
# Route to reset item counts in database to zero
@router.get("/main/reset_DBS", response_class=HTMLResponse)
def reset_count(request: Request):
    mongo.reset_counts(items)
    return RedirectResponse(url="/UI/main", status_code=303) # Redirects back to homepage after resetting counts

# Route to clear all exchange sessions from the database
@router.get("/main/clear_SOS", response_class=HTMLResponse)
def clear_sessions(request: Request):
    mongo.clear_sessions() # Deletes all documents inside the sessions collection
    return RedirectResponse(url="/UI/main", status_code=303) # Redirects back to homepage after clearing sessions
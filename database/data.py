from sqlalchemy import create_engine # create_engine function creates the connection to interact with the database
from sqlalchemy.orm import sessionmaker, declarative_base # sessionmaker creates session objects which we use to interact with the database such as add, query, update, delete whilce declarative_base allows class definitions that map to databse tables
from pymongo import MongoClient # Imports the MongoClient class from the pymongo library.
from dotenv import load_dotenv # Loads secrets from .env.
import os # Accesses the environment variables.
import certifi # Imports the certifi library which is required by Atlas in terms of secure SSL/TLS connections

# Loads enviroment variables from .env file to retrieve sensitive data securely
load_dotenv() # Loads secrets 

DATABASE_URL = os.getenv("DATABASE_URL") # Initializes & Fetches Database URL

engine = create_engine(DATABASE_URL) # Creates database engine using SQLite
SessionLocal = sessionmaker(bind=engine, autoflush=False) # Creates a class called SessionLocal that creates database sessions like add(), delete() etc. autoflush ensures changes wont be automatically flushed to the DB until committed
Base = declarative_base() # Base class for ORM model classes from which ever model will inherit from

# Dependency function that creates and provides a new database session for each request
def get_db():
    db = SessionLocal() # Creates a new database session
    try:
        yield db # Makes the session available to the route
    finally:
        db.close() # Ensures the session is closed after the request

# Mongo Class 2 Be Used to interact with the Database
class Co2:
    def __init__(self): # Constructor method i creates an instance of co2 & setsup references to the necessary collections
        try:
            uri = os.getenv("uri") # Loads the MongoDB URI (connection string) from environment variables
            if not uri:
                raise EnvironmentError("MongoDB URI not found in environment variables.")
            
            self.client = MongoClient(uri, tlsCAFile=certifi.where())  # Initializes the MongoClient to establish a connection to MongoDB

            # Accesses the database and the co2, sos, collections plus Event Logs after sign out
            self.db = self.client["YoungCaritas"]
            self.co2 = self.db["co2"]
            self.sos = self.db["sessions"] 
            self.logs = self.db["Event_Logs"]

            print("Database Connected")

        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise # Re-raises the exception to stop the program
     
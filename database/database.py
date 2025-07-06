from sqlalchemy import create_engine # create_engine function creates the connection to interact with the database
from sqlalchemy.orm import sessionmaker, declarative_base # sessionmaker creates session objects which we use to interact with the database such as add, query, update, delete whilce declarative_base allows class definitions that map to databse tables
from dotenv import load_dotenv # Loads secrets from .env.
import os # Accesses the environment variables..

# Loads enviroment variables from .env file to retrieve sensitive data securely
load_dotenv() # Loads secrets 

DATABASE_URL = os.getenv("DATABASE_URL") # Initializes & Fetches Database URL
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set!")

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
from sqlalchemy import create_engine, text # create_engine function creates the connection to interact with the database
from sqlalchemy.orm import sessionmaker, declarative_base # sessionmaker creates session objects which we use to interact with the database such as add, query, update, delete whilce declarative_base allows class definitions that map to databse tables
from dotenv import load_dotenv # Loads secrets from .env.
import os # Accesses the environment variables..

# Loads enviroment variables from .env file to retrieve sensitive data securely
load_dotenv() # Loads secrets 

# Initializes & Fetches Database URL's
LOCAL_DB_URL = os.getenv("LOCAL_POSTGRES_URL")
DATABASE_URL = os.getenv("DATABASE_URL") 

# Tracks Postgres online & offline status
is_postgres_online = False
engine = None

# Tries to connect to the cloud first
try:
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1")) # Tests if database works before it connects to it
    print("Connected to Supabase")
    is_postgres_online = True

except Exception as e:
    print(f"Supabase connection failed: {e}")

    try:
        engine = create_engine(LOCAL_DB_URL, echo=True, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Supabase unavailable. Using local Postgres.")
        is_postgres_online = False

    except Exception as local_e:
        print(f"Local Postgres connection failed too: {local_e}")
        engine = None  
        is_postgres_online = False

 # Creates database engine using SQLite
SessionLocal = sessionmaker(bind=engine, autoflush=False) # Creates a class called SessionLocal that creates database sessions like add(), delete() etc. autoflush ensures changes wont be automatically flushed to the DB until committed
Base = declarative_base() # Base class for ORM model classes from which ever model will inherit from

# Dependency function that creates and provides a new database session for each request
def get_db():
    if not SessionLocal:
        raise RuntimeError("No database connection available.")
    db = SessionLocal() # Creates a new database session
    try:
        yield db # Makes the session available to the route
    finally:
        db.close() # Ensures the session is closed after the request
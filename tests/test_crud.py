import pytest # Testing framework to define and run test functions
from sqlalchemy import create_engine # SQLAlchemy function to create a connection to a test database
from sqlalchemy.exc import IntegrityError # Specific exception for duplicate entries
from sqlalchemy.orm import sessionmaker # A factory for creating database session instances
from pydantic import ValidationError # Exception raised when schema validation fails
from database.database import Base # Imports Base class from database to deinfe ORM models
from crud.operations import CRUD # Imports the CRUD Class from operations
from schemas.schemas import co2_createitem # Imports a request pydantic schema

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # Creates an in-memory Sqlite database for testing purposes to reset after each test run avoid writing to an actual file
engine = create_engine(SQLALCHEMY_DATABASE_URL) # Creates database engine using SQLite
TestingSessionLocal = sessionmaker(bind=engine) # Binds the engine to create session instances for testing
Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet existent

# Pytest fixture provides a fresh database session for each test function 
@pytest.fixture
def db_session():
    session = TestingSessionLocal() # Creates a new database session
    try:
        yield session # Provides the session to the test
    finally:
        session.close() # Ensures the session is closed after the request

# Unit test for the "create_item" function in the CRUD class. Verifies that the item is correctly created and its fields match the input
def test_create_item(db_session):
    crud = CRUD() # Initializes the CRUD class
    new_item = co2_createitem(name="T.shirt", category="OBERTEILE", base_co2=11.5)  # Creates a Pydantic schema instance representing the item to insert into the DB
    item = crud.create_item(db_session, new_item)  # Calls the create_item method to pass in the session and the new schema

    # Assertions to verify that the item was created correctly
    assert item.name == "T.shirt"  # Checky if name was saved correctly
    assert item.category == "OBERTEILE"  # Check if category was saved correctly
    assert item.base_co2 == 11.5  # Check if base_co2 was saved correctly

# Unit test for the "get_itemby_name" function in the CRUD class. Creates an item then checks if it can be found by its name
def test_get_itemby_item(db_session):
    crud = CRUD() # Initializes the CRUD class
    crud.create_item(db_session, co2_createitem(name="Hose", category="UNTERTEILE", base_co2=15.2))  # Calls the create_item method to reate a new item in the test database 
    item = crud.get_itemby_name(db_session, "Hose") # Tries to fetch the item back from the database using its name

    # Assertions to esnure item was successfully found
    assert item is not None # Checks that we got a result
    assert item.name == "Hose"  # Verifies the name matches what we inserted
    assert item.category == "UNTERTEILE"  # Verifies the right category
    assert item.base_co2 == 15.2 # Verifies the CO2 value matches what we inserted

# EXCEPTIONAL TEST CASES
# Test to ensure creating a duplicate item using the name raises a database error since names are unique
def test_create_duplicate_item_brings_error(db_session):
    crud = CRUD() # Initializes the CRUD class
    new_item = co2_createitem(name="Jeans", category="UNTERTEILE", base_co2=23.5)  # Creates a Pydantic schema instance representing the item to insert into the DB
    
    # Once first creation is successful
    crud.create_item(db_session, new_item)  # Calls the create_item method to pass in the session and the new schema

    # Second creation raises an IntegrityError
    with pytest.raises(IntegrityError):
        crud.create_item(db_session, new_item)

# Test to ensure that searching for a non-existent item returns None
def test_get_nonexistent_item_returns_none(db_session):
    crud = CRUD()  # Initializes the CRUD class
    item = crud.get_itemby_name(db_session, "NonExistentItem")  # Tries fetching an item that was never created
    
    # Assertions to esnure result is none since item doesnt exist
    assert item is None # Checks that we got no result

# Test to verify that missing required fields in schema raises a Pydantic ValidationError
def test_create_item_withmissing_orinvaliddata_raises_error():
    # Raises ValidationError because 'name' is required but set to None
    with pytest.raises(ValidationError):
        co2_createitem(name=None, category="OBERTEILE", base_co2=5.0)
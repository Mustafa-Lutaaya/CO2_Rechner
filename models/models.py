from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime # Defines columns and their data types in the database table
from database.database import Base  # Imports the declarative base from the database module
from datetime import datetime # imports datetime to handle date & time fields

# ORM Model representing a row in the "items" table
class CO2(Base):
    __tablename__ = "items" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    category = Column(String)  # Adds a Category column that stores strings
    name = Column(String, unique=True)  # Adds a Name column that stores strings & ensures its unique
    count = Column(Integer, default=0) # Adds a Count column which holds integers
    base_co2 = Column(Float) # Adds a Base_CO2 column which stores float numbers


# ORM Model representing a row in the "Users" table
class USER(Base):
    __tablename__ = "Users" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    name = Column(String)  # Adds a name column that stores strings
    email = Column(String, unique=True)  # Adds an email column that stores strings & ensures its unique
    is_verified = Column(Boolean, default=False)  # Determines verification status
    password = Column(String)  # Adds a password column that stores strings 
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp when user is created
    force_password_change = Column(Boolean, default=True) # Forces password changeon frits time login
from sqlalchemy import Column, Integer, String, Float # Defines columns and their data types in the database table
from database.data import Base  # Imports the declarative base from the database module
from pydantic import BaseModel, Field # Validates request body structure using schemas
from typing import List, Optional 

# ORM Model representing a row in the "items" table
class CO2(Base):
    __tablename__ = "items" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    category = Column(String)  # Adds a Category column that stores strings
    name = Column(String, unique=True)  # Adds a Name column that stores strings & ensures its unique
    count = Column(Integer, default=0) # Adds a Count column which holds integers
    base_co2 = Column(Float) # Adds a Base_CO2 column which stores float numbers    

# MONGO DB DATA MODEL
class Item(BaseModel): 
    name: str = Field(..., unique=True) # Item Name
    count: int = 0 # Item Quantity
    base_co2: Optional[float] = None #Base_CO2 emission value per item  
    co2: Optional[float] = None # EMission after calculation


class Category(BaseModel):
    category: str # Category name frouping the items 
    items: List[Item] # List of items in the category
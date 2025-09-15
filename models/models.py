from sqlalchemy import Column, Integer, String, Float, JSON, Text, Boolean, DateTime, ForeignKey # Defines columns and their data types in the database table
from sqlalchemy.orm import relationship  # Used to define relationships between ORM models 
from database.database import Base  # Imports the declarative base from the database module
from datetime import datetime # imports datetime to handle date & time fields
from pydantic import BaseModel, Field # Validates request body structure using schemas
from typing import List, Optional 

# ORM Model representing a row in the "items" table
class Item(Base):
    __tablename__ = "Items" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    category_id = Column(Integer, ForeignKey("Categories.id"), nullable=False) # Links to the category the item belongs to
    name = Column(String, unique=True)  # Adds a Name column that stores strings & ensures its unique
    count = Column(Integer, default=0) # Adds a Count column which holds integers
    base_co2 = Column(Float) # Adds a Base_CO2 column which stores float numbers

    @property
    def category_name(self):
        return self.category.name if self.category else None

    # One-to-many relationship with categories
    category = relationship("Category", back_populates="items") # Relationship back to the Item

# HIERACHY MODELS    
# ORM Model representing a row in the "Categories" table
class Category(Base):
    __tablename__ = "Categories" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    name = Column(String, nullable=False, unique=True)  # Adds a Main Name column that stores strings and is required
    description = Column(String, nullable=True) # Adds an optional description
    
    # One-to-many relationship with Items
    items = relationship("Item", back_populates="category") # Relationship back to the Item

# USER MANAGEMENT MODELS
# ORM Model representing a row in the "AdminUsers" table
class Admin(Base):
    __tablename__ = "AdminUsers" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    first_name = Column(String)  # Adds a first name column that stores strings
    last_name = Column(String)  # Adds a last name column that stores strings
    email = Column(String, unique=True)  # Adds an email column that stores strings & ensures its unique
    is_verified = Column(Boolean, default=False)  # Determines verification status
    password = Column(String)  # Adds a password column that stores strings 
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp when the admin is created
    force_password_change = Column(Boolean, default=True) # Forces password change on first time login

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="admin", cascade="all, delete-orphan") # Relationship back to audit logs

# ORM Model representing a row in the "Users" table
class User(Base):
    __tablename__ = "Users" # Table name in the database

    # Primary identification
    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index.
    first_name = Column(String)  # Adds a first name column that stores strings
    last_name = Column(String)  # Adds a last name column that stores strings
    email = Column(String, unique=True)  # Adds an email column that stores strings & ensures its unique
    
    # Security and access control
    password = Column(String)  # Password column as a string of characters
    user_type = Column(String, default="client")  # Distinguishes between "admin" and "client" users
    is_verified = Column(Boolean, default=False)  # Determines verification status
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp when user is created
    verified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Timestamp for when the user is verification

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan") 

# ORM Model representing a row in the "User Profiles" table 
class UserProfile(Base):
    __tablename__ = "user_profiles" # Table name in the database

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False, unique=True)

    # Basic Company Information
    name = Column(String, nullable=True)
    location = Column(String, nullable=True) # For industry-specific ESG metrics

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")    

# ORM Model representing a row in the "AuditLogs" table
class AuditLog(Base):
    __tablename__ = "audit_logs" # Table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary Key marks the id column as a unique identifier while index:True creates an index for faster searches
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=True) # Links to user (nullable for system events)
    admin_id = Column(Integer, ForeignKey("AdminUsers.id"), nullable=True) # Links to admin user if applicable
    
    # Event details
    action = Column(String, nullable=False) # Action performed such as login, logout, create_item and so on
    resource_type = Column(String, nullable=True) # Type of resource affected such as category, item, form and so on
    resource_id = Column(String, nullable=True) # ID of the affected resource if available
    
    # Request context
    ip_address = Column(String, nullable=True) # User's IP address at the time of action
    user_agent = Column(String, nullable=True) # Browser or client information
    method = Column(String, nullable=True) # HTTP method such as GET, POST and so on 
    
    # Event metadata
    details = Column(JSON, nullable=True) # Additional event-specific data stored in JSON format
    status = Column(String, default="success") # Indicates outcome of the action: success, failure or error
    error_message = Column(Text, nullable=True) # Stores error details if status is failure or error
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True) # Timestamp when the event occurred, indexed for fast querying
    
    # Relationships
    user = relationship("User", back_populates="audit_logs") # Relationship to regular user table
    admin = relationship("Admin", back_populates="audit_logs") # Relationship to admin user table

# MONGO DB DATA MODEL
class ItemSchema(BaseModel): 
    item_name: str = Field(..., unique=True) # Item Name
    count: int = 0 # Item Quantity
    base_co2: Optional[float] = None #Base_CO2 emission value per item  
    co2: Optional[float] = None # EMission after calculation


class CategorySchema(BaseModel):
    name: str # Category name frouping the items 
    items: List[ItemSchema] # List of items in the category
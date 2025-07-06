# FastAPI Components to build the web app.
from fastapi import APIRouter, HTTPException, Depends, Body # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses, and Depends for dependency injection tools such as getting DB Session
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data
from typing import List

# Internal Modules
from schemas.schemas import co2_createitem, co2_itemread, user, ver_user, read_user  # Imports request and response schemas respectively
from crud.operations import CRUD # Imports CRUD operations for database interaction
from database.database import get_db, engine, Base # Imports database configurations & dependency function to provide a database session for each request

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet present
router = APIRouter() #  Creates a router instance to group related routes
crud = CRUD() # Initializes CRUD class instance to perorm DB Operations

# Route to get all items from the database
@router.get("/items", response_model=List[co2_itemread]) # GET /items/ returns a list of items
def read_all(db: Session = Depends(get_db)): # Injects DB Session dependency
    try:
        return crud.get_all_items(db) # Calls Crud function to retrieve all items and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP 500

# Route to get single item by name
@router.get("/items/{name}", response_model=co2_itemread) # GET /items/{name} fetches one item
def getitem(name: str, db: Session = Depends(get_db)):
    item = crud.get_itemby_name(db, name) # Calls the CRUD function to get the item by name
    if not item:
        raise HTTPException(status_code=404, detail="Item not found") # Returns 404 if item doesn't exist
    return item  # Returns the found item

# Route to create a new item in the database
@router.post("/items", response_model=co2_itemread) # POST /items/ with repsonse using Pydantic schema
def createitem(item: co2_createitem, db: Session = Depends(get_db)): # Injects Db Session dependency
    exisiting = crud.get_itemby_name(db, item.name) # Checks if item already exists
    if exisiting:
        raise HTTPException(status_code=400, detail="Item already exists") # Prevents Duplicates
    try:
        return crud.create_item(db, item) # Calls crud function to add item and return created item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handles any unexpected database or logic errors

# Route to modify an exisiting item using the name
@router.put("/items/{name}", response_model=co2_itemread) # PUT /items/{name} updates an existing item
def updateitem(name: str, item: co2_createitem, db: Session = Depends(get_db)):
    updated_item = crud.update_item(db, name, item) # Calls crud update function that grabs a new item and tries to updated it 
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found to update") # Raises error if item isnt found
    return updated_item

# Route to delete an item identified by Name
@router.delete("/items/{name}", response_model=co2_itemread) # DELETE /items/{name} removes an item
def deleteitem(name: str, db: Session = Depends(get_db)): 
    deleted_item = crud.delete_item(db, name)  # Calls CRUD delete function that finds and deletes item
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Item not found for deletion") # Raises error if item isnt found
    return deleted_item # Returns the deleted item

# Route to get all users from the database
@router.get("/users", response_model=List[user]) # GET /users/ returns a list of all users
def show_users(db: Session = Depends(get_db)): # Injects DB Session dependency
    try:
        return crud.get_all_users(db) # Calls Crud function to retrieve all users and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP 500

# Route to get single pending user by email
@router.get("/user/{email}", response_model=read_user) # GET /user/{email} fetches one user
def get_user(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email) # Calls the CRUD function to get the user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found") # Returns 404 if user doesn't exist
    return user # Returns the found user

# Route to create a new user in the database
@router.post("/user", response_model=user) # POST /user/ with repsonse using Pydantic schema
def register_user(new_user: user, db: Session = Depends(get_db)): # Injects Db Session dependency
    
    exisiting = crud.get_user_by_email(db, new_user.email) # Checks if user already exists
    if exisiting:
        raise HTTPException(status_code=400, detail="User Account already exists") # One email should be used by one user
    
    try:
        return crud.register_user(db, new_user) # Calls crud function to register new user and add them to  database
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handles any unexpected database or logic errors

# Route to delete a user identified by email
@router.delete("/user/{email}", response_model=user) # DELETE /user/{email} removes a pending user 
def delete_user(email: str, db: Session = Depends(get_db)): 
    deleted_user = crud.delete_user(db, email)  # Calls CRUD delete function that finds and deletes user using email
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found for deletion") # Raises error if pending_user isnt found
    return deleted_user # Returns the deleted user

# Route to delete all pending users 
@router.delete("/users", response_model=List[user]) # DELETE /users/{email} removes all users 
def delete_all_users(db: Session = Depends(get_db)): 
    deleted_users = crud.delete_users(db)  # Calls CRUD delete function deletes all users
    if not deleted_users:
        raise HTTPException(status_code=404, detail="Users arent found for deletion") # Raises error if pending users aren't found
    return deleted_users # Returns the deleted user

# Route to verify user
@router.post("/verifyuser/{email}", response_model=ver_user) # POST /verifyuser/{email} verifies a pending user using the email
def verify_pending_user(email: str,  db: Session = Depends(get_db)):
    verification = crud.verify_user(db, email) # Calls CRUD verify function that verifies user 

    if not verification:
        raise HTTPException(status_code=404, detail="User not found") # Raises error if user isnt found
    
    verified_user = verification

    return verified_user  # Returns the verified user 

# Route to change password
@router.put("/verifieduser/{email}/change_pwd", response_model=ver_user) # PUT /verifieduser/{email}/change_pwd changes the password
def change_password(email: str, new_password: str = Body(..., embed=True), db: Session = Depends(get_db)):
    updated_user = crud.change_password(db, email, new_password) # Calls crud change password function
    if not updated_user:
        raise HTTPException(status_code=400, detail="User not found or password invalid") # Raises error if user isnt found
    return updated_user  # Returns the updated user

from fastapi import APIRouter, HTTPException, Depends, Body, Form, Request # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses
from fastapi.responses import RedirectResponse, HTMLResponse  # JSON response handling
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data
from database.database import get_db, engine, Base # Imports database configurations & dependency function to provide a database session for each request
from crud.operations import AdminUserCRUD, UserCRUD, CategoryCRUD, ItemCRUD # Imports CRUD operations for database interaction
from schemas.schemas import CreateCategory, ReadCategory, CreateUser, ReadUser, AdminUser, Create_AdminUser, Read_Adminuser, CreateItem, ReadItem # Imports schema models for request validation and response serialization
from typing import List # Imports typing for Type hinting support
from fastapi.templating import Jinja2Templates # Imports Jinja2Templates to enable server-side rendering of HTML templates with variables.

# Initializes CRUD operation classes
Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet present
router = APIRouter() # Router configuration for administrative endpoints
ccrud = CategoryCRUD() # Initializes Category class instance to perform DB Operations
ucrud = UserCRUD() # Initializes UserCRUD class instance to perform DB Operations
acrud = AdminUserCRUD() # Initializes AdminUserCRUD class instance to perform DB Operations
icrud = ItemCRUD() # Initializes Item CRUD class instance to perform DB Operations
templates = Jinja2Templates(directory="templates") # Initializes templates

# MAIN ROUTE
@router.get("/", response_class=HTMLResponse)
def root_page(request: Request, db: Session = Depends(get_db), msg: str = ""): # Injects DB Session dependency plus message to display back to user as a string
   
   categories = ccrud.get_all_categories(db)
   items = icrud.get_all_items(db)

   # Renders to the template
   return templates.TemplateResponse("index.html",
                                     {"request": request, 
                                        "categories": categories,
                                        "items": items,
                                        "msg": msg, 
                                        })


# ADMIN USER ROUTES
# Route to get all users from the database
@router.get("/admin_users", response_model=List[Read_Adminuser]) # GET /admin_users/ returns a list of all users
def get_admin_users(db: Session = Depends(get_db)): # Injects DB Session dependency
    try:
        return acrud.get_all_admin_users(db) # Calls Crud function to retrieve all admin users and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP 500

# Route to get single pending user by email
@router.get("/admin_user/{email}", response_model=Read_Adminuser) # GET /admin_user/{email} fetches one admin user
def get_admin_user(email: str, db: Session = Depends(get_db)):
    user = acrud.get_admin_user_by_email(db, email) # Calls the CRUD function to get the admin user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found") # Returns 404 if admin user doesn't exist
    return user # Returns the found  admin user

# Route to create a new admin user in the database
@router.post("/admin_user", response_model=AdminUser) # POST /admin_user/ with repsonse using Pydantic schema
def register_admin_user(new_user: AdminUser, db: Session = Depends(get_db)): # Injects Db Session dependency
    exisiting = acrud.get_admin_user_by_email(db, new_user.email) # Checks if user already exists
    if exisiting:
        raise HTTPException(status_code=400, detail="User Account already exists") # One email should be used by one user
    
    try:
        return acrud.register_admin_user(db, new_user) # Calls crud function to register new admin user and add them to  database
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handles any unexpected database or logic errors

# Route to delete an admin user identified by email
@router.delete("/admin_user/{email}", response_model=AdminUser) # DELETE /admin_user/{email} removes an admin user 
def delete_admin_user(email: str, db: Session = Depends(get_db)): 
    deleted_user = acrud.delete_admin_user(db, email)  # Calls CRUD delete function that finds and deletes admin user using email
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found for deletion") # Raises error if admin user isnt found
    return deleted_user # Returns the deleted user

# Route to delete all admin users 
@router.delete("/admin_users", response_model=List[AdminUser]) # DELETE /admin_users removes all admin users 
def delete_all_admin_users(db: Session = Depends(get_db)): 
    deleted_users = acrud.delete_admin_users(db)  # Calls CRUD delete function deletes all admin users
    if not deleted_users:
        raise HTTPException(status_code=404, detail="Users arent found for deletion") # Raises error if users aren't found
    return deleted_users # Returns the deleted user

# Route to verify admin user
@router.post("/verify_admin_user/{email}", response_model=Create_AdminUser) # POST /verify_admin_user/{email} verifies a pending admin user using the email
def verify_pending_user(email: str,  db: Session = Depends(get_db)):
    verification = acrud.verify_admin_user(db, email) # Calls CRUD verify function that verifies admin user 

    if not verification:
        raise HTTPException(status_code=404, detail="User not found") # Raises error if user isnt found
    
    verified_user = verification

    return verified_user  # Returns the verified user 

# Route to change password
@router.put("/verified_admin_user/{email}/change_pwd", response_model=Create_AdminUser) # PUT /verified_admin_user/{email}/change_pwd changes the password
def change_password(email: str, new_password: str = Body(..., embed=True), db: Session = Depends(get_db)):
    updated_user = acrud.change_password(db, email, new_password) # Calls crud change password function
    if not updated_user:
        raise HTTPException(status_code=400, detail="User not found or password invalid") # Raises error if user isnt found
    return updated_user  # Returns the updated user

# USER MANAGEMENT ROUTES
# Route to get all users from the database
@router.get("/users", response_model=list[ReadUser])  # GET /users/ returns a list of users
def get_all_users(db: Session = Depends(get_db)): # Injects DB Session dependency
    try: 
        return ucrud.get_all_users(db) # Calls Crud function to retrieve all users and returns them as a list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # Handles unexpected errors and returns HTTP 500

# Route to get single pending user by email
@router.get("/user/{email}", response_model=ReadUser) # GET /user/{email} fetches one user
def get_user(email: str, db: Session = Depends(get_db)):
    user = ucrud.get_user_by_email(db, email) # Calls the CRUD function to get the user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found") # Returns 404 if user doesn't exist
    return user # Returns the found user

# Route to form a new user in the database
@router.post("/register", response_model=ReadUser) # POST /register/ with reponse using pydantic chema
def register_user(new_user: CreateUser, db: Session = Depends(get_db)): # Injects Db Session dependency
    exisiting = ucrud.get_user_by_email(db, new_user.work_email) # Checks if user  already exists
    if exisiting:
        raise HTTPException(status_code=400, detail="User email already exists") # Prevents Duplicates
    try:
        return ucrud.create_user(db, new_user) # Calls crud function to add a new question and return it
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handles any unexpected database or logic errors
    
# Route to delete a user identified by email
@router.delete("/user/{email}", response_model=ReadUser) # DELETE /user/{email} removes a user 
def delete_user(work_email: str, db: Session = Depends(get_db)): 
    deleted_user = ucrud.delete_user(db, work_email)  # Calls CRUD delete function that finds and deletes user using email
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found for deletion") # Raises error if user isnt found
    return deleted_user # Returns the deleted user

# Route to verify a user 
@router.get("/verify")  # GET /verify verifiess a user 
def verify_user(email: str, db: Session = Depends(get_db)):
    user = ucrud.verify_user(db, email)  # Calls CRUD verify user function that finds user by email and verifies them
   
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # Raises error if user isnt found
    
    if user.is_verified:
        return {"message": "Email was already verified. You may now log in."} # Returns information message if user was already verified   
    return {"message": "Email successfully verified. You may now log in."} # Returns the deleted user

# CATEGORY UI ROUTES
# POST route at "/category" to handle form submissions to create a new category.
@router.post("/category")
def create_category(
    name: str = Form(...),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # Checks if a category with the same name already exists in the database.
    existing = ccrud.get_category_by_name(db, name)
    if existing:
        return RedirectResponse("/api?msg=category_exists", status_code=303)  # Redirect without creating duplicate
    
    # Wraps form data into Pydantic schema and creates the category.
    category = CreateCategory(name=name, description=description)
    ccrud.create_category(db, category)

    return RedirectResponse("/api?msg=category_created", status_code=303)  # Redirects after successful creation

# POST route at "/update-category" for updating an existing category.
@router.post("/update-category")
def update_category(
    original_name: str = Form(...),
    name: str = Form(...),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # Wraps updated data in Pydantic schema
    category_data = CreateCategory(name=name, description=description)
    updated = ccrud.update_category(db, original_name, category_data)

    if not updated:
        return RedirectResponse("/api?msg=category_notfound", status_code=303)  # Redirect if category doesn't exist

    return RedirectResponse("/api?msg=category_updated", status_code=303)  # Redirect after successful update

# POST route at "/delete-category" to delete a category.
@router.post("/delete-category")
def delete_category(name: str = Form(...), db: Session = Depends(get_db)):
    # Checks if the category exists before deletion
    if not ccrud.get_category_by_name(db, name):
        return RedirectResponse("/api?msg=category_notfound", status_code=303)
    
    ccrud.delete_category(db, name)  # Deletes the category
    return RedirectResponse("/api?msg=category_deleted", status_code=303)  # Redirect after deletion


# ITEM UI ROUTES
# POST route at "/create" to handle form submissions to create new items.
@router.post("/create")
def create_item(
    category_name: str = Form(...),
    name: str = Form(...),
    base_co2: float = Form(...),
    db: Session = Depends(get_db),
):
    # Checks if an item with this name already exists
    if icrud.get_item_by_name(db, name):
        return RedirectResponse("/api?msg=item_exists", status_code=303)  # Redirect without creating duplicate
    
    # Wraps form data into Pydantic schema and creates the item
    icrud.create_item(db, CreateItem(category_name=category_name, name=name, base_co2=base_co2))
    return RedirectResponse("/api?msg=item_created", status_code=303)  # Redirect after successful creation

# POST route at "/update" to update an existing item.
@router.post("/update")
def update_item_ui(
    original_name: str = Form(...),
    name: str = Form(...),
    category_name: str = Form(...),
    base_co2: float = Form(...),
    db: Session = Depends(get_db)
):
    # Wraps form data into CreateItem for CRUD
    updated_item = icrud.update_item(db, original_name, CreateItem(name=name, category_name=category_name, base_co2=base_co2))
    
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found to update")

    # Redirect back to UI page after successful update
    return RedirectResponse(url="/api/?msg=item_updated", status_code=303)

# POST route at "/delete" to delete an item.
@router.post("/delete")
def delete_item(name: str = Form(...), db: Session = Depends(get_db)):
    # Checks if the item exists before deletion
    if not icrud.get_item_by_name(db, name):
        return RedirectResponse("/api?msg=item_notfound", status_code=303)
    
    icrud.delete_item(db, name)  # Deletes the item
    return RedirectResponse("/api?msg=item_deleted", status_code=303)  # Redirect after deletion
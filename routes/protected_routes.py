from fastapi import APIRouter, Depends, Request, HTTPException  # Imports FastAPI classes and utilities for API routing, dependency injection, request handling, and exceptions
from database.database import get_db  # Imports the function to provide a DB session
from sqlalchemy.orm import Session  # Imports SQLAlchemy ORM Session for DB interaction
from config.jwt_handler import JWTHandler  # Imports custom JWT handling class
from crud.operations import UserCRUD, AdminUserCRUD  # Imports user-specific CRUD operations

# Initializes router and CRUD class instance
router = APIRouter()  # Creates a router instance to define API endpoints
ucrud = UserCRUD()  # Initializes the UserCRUD class instance for database operations
acrud = AdminUserCRUD() # Initializes the AdminUserCRUD class instance for database 

# Dependency function to authenticate the current user using a flexible approach (cookie → query param → header)
def get_current_user_flexible(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")  # Attempts to retrieve JWT from cookies
    
    if not access_token:
        access_token = request.query_params.get("token")  # Checks query params for token, if not in cookies,
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated - token missing")  # Rejects if no token found
    
    try:
        payload = JWTHandler.verify_login_token(access_token)  # Verifies the JWT token
        user = ucrud.get_user_by_email(db, payload.get("sub"))  # Extracts the user based on token subject which is the email
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")  # Returns error if user doesn't exist
        
        if not user.is_verified:
            raise HTTPException(status_code=401, detail="User account not verified")  # Returns error if user is unverified
        
        return user  # Returns authenticated user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")  # Handles any authentication/verification failures

# Dependency function to authenticate the current admin user using cookie-based JWT token
def get_current_admin_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token") # Attempts to retrieve JWT token from cookies
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated") # Rejects request if token is missing

    try:
        payload = JWTHandler.verify_login_token(token) # Verifies and decodes the JWT token
        user = acrud.get_admin_user_by_email(db, payload.get("sub")) # Fetches admin user from database using email inside token payload
        
        # Validates that the user exists and is verified
        if not user:
            raise HTTPException(status_code=401, detail="Admin not found") # Rejects if admin not in database
        if not user.is_verified:
            raise HTTPException(status_code=401, detail="Admin account not verified") # Rejects if admin account isn’t verified
        
        return user # Returns authenticated admin user object
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}") # Handles verification or decoding failures
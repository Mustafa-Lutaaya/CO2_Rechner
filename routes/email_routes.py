from fastapi import APIRouter, HTTPException, Depends, Request # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses, and Depends for dependency injection tools s
from fastapi.responses import HTMLResponse, RedirectResponse # Imports response classes to return rendered HTML pages &  to redirect client to another URL after a POST 
from fastapi.templating import Jinja2Templates # Imports Jinja2Templates to enable server-side rendering of HTML templates with variables.
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data

# Internal Modules
from crud.operations import UserCRUD, AdminUserCRUD # Imports CRUD operations for database interaction
from database.database import get_db, engine, Base # Imports SQLAlchemy engine connected to the database, dependency function to provide DB Session and declarative Base for models to create tables
from config.jwt_handler import JWTHandler # Imports JWT Handler Class 
from config.mail_handler import EmailHandler

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet existent
router = APIRouter() #  Creates a router instance to group related routes
ucrud = UserCRUD() # Initializes CRUD class instance to perorm DB Operations
acrud = AdminUserCRUD() # Initializes CRUD class instance to perorm DB Operations
templates = Jinja2Templates(directory="templates") # Initializes templates

# EMAIL ROUTES
# User Verification Route
@router.get("/verify")
def verify_user(token: str, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    try:
        payload = JWTHandler.decode_token(token) # Decodes the token sent via the email link
        email = payload["sub"]  # Extracts the email address from the token payload

        result = ucrud.verify_user(db, email)  # Verifies the user using CRUD logic
        if result is None:
            return RedirectResponse(url="/email/user_unfound", status_code=303) # Redirects to unfound page
        
        if result == "already_verified":
             return RedirectResponse(url="/email/already_verified", status_code=303) # Redirects to already verified page

        return RedirectResponse(url="/email/user_verified", status_code=303) # Redirects to approved page
    
    except Exception as e:
         return RedirectResponse(url="/email/expired_token", status_code=303) # Redirects to invalid token page if token is expired or invalid
    
@router.get("/resend-verification")
def resend_verification(email: str, db: Session = Depends(get_db)):
    print(f"Resend verification called for: {email}")
    try:
        user = ucrud.get_user_by_email(db, email)
        
        if not user:
            print("User not found.")
            return RedirectResponse(url="/email/user_unfound", status_code=303) # Redirects to unfound page

        if user.is_verified:
            print("User already verified.")
            return RedirectResponse(url="/email/already_verified", status_code=303) # Redirects to already verified page
        
        # Attempts to resend verification
        EmailHandler.send_confirmation_email(first_name=user.first_name, last_name=user.last_name,email=user.work_email)
        print("Email resent successfully.")
        return RedirectResponse(url="/email/verification", status_code=303) # Redirects to already verified page
        
    except Exception as e:
        print(f"ERROR during resend verification: {e}")
        return RedirectResponse(url="/email/error_verification", status_code=303)
    
# Approval User Route 
@router.get("/approve_user")
def approve_user(request: Request, db: Session = Depends(get_db)):

    token = request.query_params.get("token") # Gets token from string
    if not token:
        return RedirectResponse(url="/email/invalid_token", status_code=303)  # Redirects to invalid token page & if empty or missing
    
    try:
        # Decodes token and extracts email
        payload = JWTHandler.decode_token(token)
        email = payload["sub"]

        result = acrud.verify_admin_user(db, email) # Finds the admin user in the pending_users collection by email
        if result is None:
            return RedirectResponse(url="/email/unfound", status_code=303) # Redirects to unfound page
        
        if result == "already_verified":
           return RedirectResponse(url="/email/already_approved", status_code=303) # Redirects to unfound page
        
        return RedirectResponse(url="/email/approved", status_code=303) # Redirects to approved page
    
    except Exception as e:
        print(f"Error approving user: {e}")
        return RedirectResponse(url="/email/invalid_token", status_code=303) # Redirects to invalid token page if token is expired or invalid
    
# Rejection User Route 
@router.get("/reject_user")
def reject_user(request: Request, db: Session = Depends(get_db)):

    token = request.query_params.get("token") # Gets token from string
    if not token:
        return RedirectResponse(url="/email/invalid_token", status_code=303)  # Redirects to invalid token page & if empty or missing
    
    try:
        # Decodes token and extracts email
        payload = JWTHandler.decode_token(token)
        email = payload["sub"]

        result = acrud.register_admin_user(db, email) # Finds the user in the pending_users collection by email
        if result is None:
            return RedirectResponse(url="/email/unfound", status_code=303) # Redirects to unfound page
        
        if result == "already_verified":
            return RedirectResponse(url="/email/already_approved", status_code=303) # Redirects to unfound page
        
        return RedirectResponse(url="/email/rejected", status_code=303) # Redirects to approved page
    
    except Exception as e:
        print(f"Error rejecting user: {e}")
        return RedirectResponse(url="/email/invalid_token", status_code=303) # Redirects to invalid token page if token is expired or invalid

# HTML RESPONGE PAGES
@router.get("/approved", response_class=HTMLResponse)
def approved_page(request: Request):
    return templates.TemplateResponse("approved.html", {"request": request})

@router.get("/already_approved", response_class=HTMLResponse)
def already_approved_page(request: Request):
    return templates.TemplateResponse("already_approved.html", {"request": request})

@router.get("/rejected", response_class=HTMLResponse)
def rejected_page(request: Request):
    return templates.TemplateResponse("rejected.html", {"request": request})

@router.get("/unfound", response_class=HTMLResponse)
def unfound_page(request: Request):
    return templates.TemplateResponse("not_found.html", {"request": request})

@router.get("/invalid_token", response_class=HTMLResponse)
def invalid_token_page(request: Request):
    return templates.TemplateResponse("invalid.html", {"request": request})

@router.get("/user_verified", response_class=HTMLResponse)
def verified_page(request: Request):
    return templates.TemplateResponse("verified.html", {"request": request})

@router.get("/already_verified", response_class=HTMLResponse)
def already_verified_page(request: Request):
    return templates.TemplateResponse("already_verified.html", {"request": request})

@router.get("/user_unfound", response_class=HTMLResponse)
def user_not_found_page(request: Request):
    return templates.TemplateResponse("user_not_found.html", {"request": request})

@router.get("/expired_token", response_class=HTMLResponse)
def expired_token_page(request: Request):
    return templates.TemplateResponse("expired_token.html", {"request": request})

@router.get("/verification", response_class=HTMLResponse)
def verification_page(request: Request):
    return templates.TemplateResponse("re_verification.html", {"request": request})

@router.get("/error_verification", response_class=HTMLResponse)
def error_verification(request: Request):
    return templates.TemplateResponse("error_verification.html", {"request": request})
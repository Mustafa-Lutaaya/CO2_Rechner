# FastAPI Components to build the web app.
from fastapi import APIRouter, Request, Form,  Depends # Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses, and Depends for dependency injection tools s
from fastapi.responses import HTMLResponse, RedirectResponse # Imports response classes to return rendered HTML pages &  to redirect client to another URL after a POST 
from fastapi.templating import Jinja2Templates # Imports Jinja2Templates to enable server-side rendering of HTML templates with variables.
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data

# Internal Modules
from schemas.schemas import co2_createitem, user  # Imports request and response schemas respectively
from crud.operations import CRUD # Imports CRUD operations for database interaction
from database.database import get_db, engine, Base # Imports SQLAlchemy engine connected to the database, dependency function to provide DB Session and declarative Base for models to create tables
from config.jwt_handler import JWTHandler # Imports JWT Handler Class 

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet existent
router = APIRouter() #  Creates a router instance to group related routes
crud = CRUD() # Initializes CRUD class instance to perorm DB Operations
templates = Jinja2Templates(directory="templates") # Initializes templates

# EMAIL ROUTES
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

        result = crud.verify_user(db, email) # Finds the user in the pending_users collection by email
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

        result = crud.reject_user(db, email) # Finds the user in the pending_users collection by email
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
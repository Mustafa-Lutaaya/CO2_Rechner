from fastapi import APIRouter,Request, Form, Depends # Imports APIRouter to create a modular group of API Routes
from fastapi.responses import HTMLResponse, RedirectResponse # Imports response classes to return rendered HTML pages &  to redirect client to another URL after a POST 
from fastapi.templating import Jinja2Templates # Imports Jinja2Templates to enable server-side rendering of HTML templates with variables.
from crud.operations import AdminUserCRUD # Imports CRUD operations for database interaction
from schemas.schemas import  AdminRegistration # Imports request and response schemas respectively
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data
from database.database import get_db, engine, Base # Imports SQLAlchemy engine connected to the database, dependency function to provide DB Session and declarative Base for models to create tables
from config.jwt_handler import JWTHandler # Imports JWT Handler Class for token creation and validation
from utilities.utils import AuditLogger
import logging


Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet existent
router = APIRouter() #  Creates a router instance to group related routes
templates = Jinja2Templates(directory="templates") # Initializes templates
acrud = AdminUserCRUD() # Initializes AdminUserCRUD class instance to perorm DB Operations

# FORM PAGE ROUTES
# Form Handling Route (Registration & Login)
@router.get("/", response_class=HTMLResponse)
def root(request: Request, error: str = None, success: str = None):

    # Initializes variable to store messages
    alert = None
    success_message = None

    # Checks if an error code was passed and returns an alert message
    if error == "missing_name":
        alert = "Name is required for registration."
    elif error == "user_not_found":
        alert = "User not found or not approved."
    elif error == "missing_password":
        alert = "Password is required for login."
    elif error == "incorrect_password":
        alert = "Incorrect password."
    elif error == "invalid_action":
        alert = "Invalid action."
    elif error == "short_name":
        alert = "Name must be at least 4 characters."
    elif error == "user_exists":
        alert = "User Account already exists."
    elif error == "weak_password":
        alert = "Password must be 8+ chars, include uppercase, lowercase, number, and symbol."
    elif error == "password_mismatch":
        alert = "Passwords don't match"

    # Success messages
    if success == "registered":
        success_message = "Registration successful. A One-Time-Password will be sent to you upon successful verification."
    elif success == "password_changed":
        success_message = "Password change successful. Login again with your new password."

    context = {
        "request": request, # Passes the request for Jinja2 to access
        "alert": alert, # Adds alert to context so it's accessible in the HTML template
        "success": success_message,
    }
    return templates.TemplateResponse("admin.html", context)  # Renders the 'index.html' template with data from the context dictionary

# ADMIN AUTH ROUTES
# Route to handle admin login and set session cookie
@router.post("/login", response_class=HTMLResponse) # POST /admin/login authenticates admin credentials and sets JWT cookie
def admin_login_route(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    
    # Checks if email and password are provided
    if not email:
        return RedirectResponse(url="/admin?error=missing_email", status_code=303)
    if not password:
        return RedirectResponse(url="/admin?error=missing_password", status_code=303)

    # Checks if admin user exists and is verified
    admin = acrud.get_admin_user_by_email(db, email)
    if not admin:
        return RedirectResponse(url="/admin?error=user_not_found", status_code=303)
    if not admin.is_verified:
        return RedirectResponse(url="/admin?error=user_not_verified", status_code=303)

    # Confirms password is correct
    if not acrud.confirm_password(db, email=email, password=password):
        return RedirectResponse(url="/admin?error=incorrect_password", status_code=303)
    
    # Checks if this is the first login requiring password change
    if admin.force_password_change:
        return RedirectResponse(url=f"/admin/change_password?email={email}", status_code=303)
    
    # Logins successful redirect response
    response = RedirectResponse(url="/api", status_code=303)

    # Generates JWT token for admin login
    token = JWTHandler.create_login_token(email=admin.email, user_id=admin.id, first_name=admin.first_name, last_name=admin.last_name)

    # Logs login action
    AuditLogger.log_action(db=db, action="login", resource_type="Admin", resource_id=admin.id, user_id=None, admin_id=admin.id, status="success", details={"email": admin.email, "user_type": "admin"}, request=request)

    # Creates response object to set cookie
    response.set_cookie(key="access_token", value=token, httponly=True, secure=False, samesite="lax", max_age=86400, path="/")
    
    return response # Sends redirect with cookie set


# Route to handle admin registration and save new admin to database
@router.post("/register", response_class=HTMLResponse) # POST /admin/register registers new admin user
def admin_register_route(request: Request, first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    
    # Validates input fields
    if len(first_name) < 2 or len(last_name) < 2:
        return RedirectResponse(url="/admin?error=short_name", status_code=303)
    
    # Ensure name fields are not empty
    if not first_name or not last_name:
        return RedirectResponse(url="/admin?error=missing_name", status_code=303)
    
    # Checks if admin already exists
    existing_admin = acrud.get_admin_user_by_email(db, email=email)
    if existing_admin:
        return RedirectResponse(url="/admin?error=user_exists", status_code=303)

    # Creates & registers new admin user
    try:
        new_admin = AdminRegistration(first_name=first_name, last_name=last_name, email=email)
        created_admin = acrud.register_admin_user(db, new_admin, request) # Registers user and sends email to admin

        # Logs registration action
        AuditLogger.log_action(db=db, action="register_admin", resource_type="Admin", resource_id=created_admin.id, status="success", details={"email": created_admin.email, "first_name": created_admin.first_name}, request=request)

    except Exception as e:
        logging.error(f"An error occurred during admin registration: {e}", exc_info=True)
        return RedirectResponse(url="/admin?error=server_error", status_code=303)  # Handles unexpected database errors

    # Redirects after successful registration
    return RedirectResponse(url="/admin?success=registered", status_code=303)

# Route to handle admin logout and clear session cookie
@router.post("/logout", response_class=HTMLResponse) # POST /admin/logout clears admin session cookie
def admin_logout_route(db: Session = Depends(get_db), request: Request = None):
    # Extracts admin info from JWT cookie if present
    token = request.cookies.get("access_token")
    admin_id = None
    if token:
        try:
            payload = JWTHandler.verify_login_token(token)
            admin_id = payload.get("user_id")
        except:
            pass

    # Logs logout action
    AuditLogger.log_action(db=db, action="logout", resource_type="Admin", resource_id=admin_id, user_id=admin_id, admin_id=admin_id, status="success", details={}, request=request)

    # Clears cookie and redirects to admin login page
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie(key="access_token", path="/")

    return response # Returns response with cleared cookie

# Change password page
@router.get("/change_password", response_class=HTMLResponse)
def change_password_page(request: Request, email: str):
    return templates.TemplateResponse("change_password.html", {"request": request, "email": email})

# Password change handling
@router.post("/change_password")
def change_password_submit(request: Request, email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    # Validates that passwords match
    if password != confirm_password:
        return templates.TemplateResponse("change_password.html", {"request": request, "email": email, "alert": "Passwords do not match."})
    
    # Updates the password in the database
    result = acrud.change_password(db, email=email, new_password=password)

    if result != "success":
        return templates.TemplateResponse("change_password.html", {"request": request, "email": email, "alert": result}) # Displays a specific error from CRUD function

    return RedirectResponse(url="/admin?msg=password_changed", status_code=303)
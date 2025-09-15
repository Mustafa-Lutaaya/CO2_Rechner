from fastapi import APIRouter, Depends, Request# Imports APIRouter to create a modular group of API Routes, HTTPException for raising HTTP error responses
from fastapi.responses import JSONResponse # Added for JSONResponse
from sqlalchemy.orm import Session # Imports SQLAlchemy ORM database Session class for querying data
from database.database import get_db, engine, Base # Imports database configurations & dependency function to provide a database session for each request
from crud.operations import UserCRUD # Imports CRUD operations for database interaction
from schemas.schemas import LoginRequest, RegisterRequest, LoginResponse, RegisterResponse, LogoutResponse, CreateUser # Imports schema models for request validation and response serialization
from config.jwt_handler import JWTHandler # Imports JWT Handler Class for token creation and validation
from config.pwd_handler import PWDHandler # Imports Password handler for strength validation and hashing
from utilities.utils import AuditLogger

Base.metadata.create_all(bind=engine) # Creates all database tables based on the models if not yet present
router = APIRouter() #  Creates a router instance to group related routes
ucrud = UserCRUD() # Initializes UserCRUD class instance to perform DB Operations

# CLIENT AUTHENTIFICATION ROUTES
# User Login Routes
@router.post("/auth/login", response_model=LoginResponse) # POST /auth/login authenticates user credentials and returns token
def api_login_route(login_data: LoginRequest,db: Session = Depends(get_db), request: Request = None): # Injects DB session and receives login request

    # Checks if email and password are provided
    if not login_data.email:
        return JSONResponse(status_code=400,content={"success": False, "message": "Email is required", "error_code": "MISSING_EMAIL"}) # Returns error if email is missing

    if not login_data.password:
        return JSONResponse(status_code=400,content={"success": False,"message": "Password is required", "error_code": "MISSING_PASSWORD"}) # Returns error if password is missing

    # Checks if user exists in Database and is verified
    user = ucrud.get_client_by_email(db, login_data.email)
    if not user:
        return JSONResponse(status_code=401,content={"success": False, "message": "User not found", "error_code": "USER_NOT_FOUND"}) # Returns error if user not found
    
    if not user.is_verified:
        return JSONResponse(status_code=401,content={"success": False, "message": "User account not verified. Please check your email for verification link.", "error_code": "USER_NOT_VERIFIED"}) # Returns error if user is not verified
    
    # Checks if password is correct
    if not ucrud.confirm_password(db, password=login_data.password, email=login_data.email, user_type="client"):
        return JSONResponse(status_code=401, content={"success": False, "message": "Incorrect password", "error_code": "INVALID_PASSWORD"}) # Returns error if password is incorrect

    # Generates JWT token for login
    token = JWTHandler.create_login_token(email=user.email, user_id=user.id, first_name=user.first_name, last_name=user.last_name)

    # Logs login
    AuditLogger.log_action(db=db, action="login", resource_type="User", resource_id=user.id, user_id=user.id, admin_id=None, status="success", details={"email": user.email, "user_type": user.user_type}, request=request)

    # Returns successful login response
    response_content = {
        "success": True, 
        "message": "Login successful",
        "data": {
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "user_type": user.user_type,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "verified_at": user.verified_at.isoformat() if user.verified_at else None
                },
                "token": token
            }
        }
    
    # Creates response object to set cookie along with JSON content
    response = JSONResponse(status_code=200, content=response_content)
    
    # Sets JWT token as a secure HttpOnly cookie to be sent automatically in future requests
    response.set_cookie(key="access_token", value=token,
        httponly=True,        # Prevents JavaScript access to cookie 
        secure=False,          # Set to True in production (HTTPS only); False if testing locally with HTTP
        samesite="lax",       # Allow cross-origin requests for development (lax works with HTTP)
        max_age=86400,        # Cookie expiration time in seconds 
        path="/",
        domain=None           # Allow cookies to work across localhost ports
    )

    return response # Returns response with cookie set

# User Registration Route
@router.post("/auth/register", response_model=RegisterResponse)  # POST /auth/register registers a new user account
def api_register_route(register_data: RegisterRequest, db: Session = Depends(get_db), request: Request = None):  # Injects DB session and receives registration request
     
    # Validates name fields
    if len(register_data.first_name) < 4 or len(register_data.last_name) < 4:
        return JSONResponse(status_code=400, content={ "success": False, "message": "First name and last name must be at least 4 characters long", "error_code": "SHORT_NAME"})  # Returns error if either name is too short
     
    if not register_data.first_name or not register_data.last_name:
        return JSONResponse(status_code=400, content={"success": False, "message": "First name and last name are required", "error_code": "MISSING_NAME"}) # Returns error if either name fields are empty
     
    # Checks if user already exists for client users only
    existing_user = ucrud.get_client_by_email(db, register_data.email)
    if existing_user:
        return JSONResponse(
            status_code=409,content={"success": False, "message": "User account already exists", "error_code": "USER_EXISTS",
                "data": {
                    "field": "email",
                    "value": register_data.email
                }
            }
        )  # Returns error if email is already in use
     
    # Validates password strength
    if not PWDHandler.check_password_strength(register_data.password):
        return JSONResponse(status_code=400, content={"success": False, "message": "Password must be 8+ characters, include uppercase, lowercase, number, and symbol", "error_code": "WEAK_PASSWORD"}) # Returns error if password is weak
     
    # Compares & Confirms both passwords are the same
    if register_data.password != register_data.confirm_password:
        return JSONResponse(status_code=400, content={"success": False, "message": "Passwords don't match", "error_code": "PASSWORD_MISMATCH"})  # Returns error if passwords don't match

    try:
       # Creates user object from request data client user
        new_user = CreateUser(first_name=register_data.first_name, last_name=register_data.last_name, email=register_data.email,password=register_data.password)
        created_user = ucrud.create_user(db, new_user, user_type="client") # Calls CRUD function to save new client user in DB
        
        AuditLogger.log_action(db=db, action="register_user", resource_type="User", resource_id=created_user.id, user_id=created_user.id, admin_id=None, status="success", details={"email": created_user.work_email, "first_name": created_user.first_name}, request=request) # Logs user registration

        # Return successful registration response
        return JSONResponse(
            status_code=201, content={"success": True, "message": "Registration successful. Please check your email for verification link.",
                "data": {
                    "user": {
                        "id": created_user.id,
                        "first_name": created_user.first_name,
                        "last_name": created_user.last_name,
                        "email": created_user.email,
                        "user_type": created_user.user_type,
                        "is_verified": created_user.is_verified
                    }
                }
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Registration failed. Please try again.",
                "error_code": "REGISTRATION_FAILED"
            }
        ) # Returns error if something goes wrong

# User Logout Route
@router.post("/auth/logout", response_model=LogoutResponse)  # POST /auth/logout clears user session
def api_logout_route(db: Session = Depends(get_db), request: Request = None):

    # Extracts user info from JWT cookie if present
    token = request.cookies.get("access_token")
    user_id = None
    if token:
        try:
            payload = JWTHandler.verify_login_token(token)
            user_id = payload.get("user_id")
        except:
            pass
    AuditLogger.log_action(db=db, action="logout", resource_type="User", resource_id=user_id, user_id=user_id, admin_id=None, status="success", details={}, request=request) # Logs logoout
    # Logs out user by returning a confirmation response
    response = JSONResponse(status_code=200, content={"success": True, "message": "Logout successful"}) # Returns logout success message
    response.delete_cookie(key="access_token", path="/")  # Deletes the JWT cookie
    return response

# API Token Verification Route
@router.get("/auth/verify")  # GET /auth/verify verifies the authenticity of the JWT token
def api_verify_token_route(token: str): # Accepts token as query parameter
    # Decodes and verifies the token payload
    try:
        payload = JWTHandler.verify_login_token(token)
        return JSONResponse(status_code=200, content={"success": True, "message": "Token is valid",
                "data": {
                    "user_id": payload.get("user_id"),
                    "email": payload.get("sub"),
                    "first_name": payload.get("first_name"),
                    "last_name": payload.get("last_name")
                }
            }
        )  # Returns decoded payload if valid
    
    except ValueError as e:
        return JSONResponse(
            status_code=401, content={"success": False, "message": str(e), "error_code": "INVALID_TOKEN"}
        ) # Returns error if token is invalid or expired
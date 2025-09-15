from fastapi import HTTPException, Depends, Request, status #  Imports FastAPI exceptions, dependency injection, request object, and HTTP status codes
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # Imports HTTP Bearer security for extracting tokens from headers
from fastapi import Query # Imports Query to read query parameters from requests
from config.jwt_handler import JWTHandler # Handles JWT encoding and decoding
from crud.operations import UserCRUD # Imports CRUD operations for users
from database.database import get_db # Provides DB session dependency
from sqlalchemy.orm import Session  # SQLAlchemy DB session type
import logging # Imports built-in logging for debugging and monitoring

#Setsup logger and security
logger = logging.getLogger(__name__) # Logger instance for module
security = HTTPBearer() # Initializes bearer token security scheme
ucrud = UserCRUD() # Initializes user CRUD operations

# Middleware-style for handling JWT authentication
class AuthMiddleware:
    # Main Dependency to retrieve the currently authenticated user
    @staticmethod
    def get_current_user(request:Request, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db), token_query: str = Query(default=None, alias="token") ): # Extracts token from Authorization header & Injects DB session
        # Tries to get token from cookie first
        token = request.cookies.get("access_token")

        # Fallsback to Authorization header token if present, if no token in cookie
        if not token and credentials:
            token = credentials.credentials
        
        if not token and token_query:
            token = token_query
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated - token missing")

        try:
            # Verifies and decodes JWT token
            payload = JWTHandler.verify_login_token(token)
            user = ucrud.get_user_by_email(db, payload.get("sub")) # Retrieves user using email from token
            
            if not user:
                raise HTTPException(status_code=401, detail="User not found") # Returns 401 Error if user doesn't exist
            
            if not user.is_verified:
                raise HTTPException(status_code=401, detail="User account not verified")  # Returns 401 if user isn't verified
            
            return user # Returns the authenticated and verified user
        
        # Handles invalid or expired tokens
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        
        # Handles all other errors
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Function to get user only from cookie with no header or query fallback
    @staticmethod
    def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
            # Reads JWT from cookie set by the app
            token = request.cookies.get("access_token")
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated - token missing") # Raises 401 if no cookie
            
            payload = JWTHandler.verify_login_token(token) # Decodes and verifies token

            # Fetches user by email stored in token's 'sub' claim
            user = ucrud.get_user_by_email(db, payload["sub"])
            if not user:
                raise HTTPException(status_code=401, detail="User not found") # Raises error if token is ok but user doesnt exist
            
            # Enforces verified accounts only
            if not user.is_verified:
                raise HTTPException(status_code=401, detail="User account not verified")

            return user # Returns the authenticated user object for use
    
    # Function to ensure current user is admin
    @staticmethod
    def require_admin(current_user = Depends(get_current_user)):  
        # Gets current authenticated user first
        if not current_user.is_admin: # Checks if user has admin privileges
            logger.warning(f"Non-admin user {current_user.email} attempted admin access") # Logs security event for monitoring unauthorized admin access attempts
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Admin access required - insufficient privileges") # Raises 403 Forbidden error for insufficient privileges as HTTP 403 status code indicates user is authenticated but lacks required permissions
        
        logger.info(f"Admin access granted to: {current_user.email}")  # Logs successful admin authentication
        return current_user # Returns the authenticated admin user object for use in admin route handlers
import os # Accesses the environment variables..
from jose import JWTError, jwt # Creates and verifies Json Web Tokens
from dotenv import load_dotenv # Loads secrets from .env.
from datetime import datetime, timedelta # Imports date time Library for token expiration and timestamp handling

load_dotenv() # Loads Environment Variables from .env File

# Enviroment Configurations
JWT_SECRET = os.getenv("JWT")
JWT_ALGORITHM = "HS256" # HMAC SHA256 for signing JWTs
EMAIL_EXP = 5  # Expiration time for the JWT in minutes


class JWTHandler:
    @staticmethod
    def create_token(email: str, action: str, first_name: str, last_name: str): # Creates signed JWT token with email, action type and expiration time.
        exp = datetime.utcnow() + timedelta(minutes=EMAIL_EXP)
        payload = {
            "sub": email, # Subject email of the user
            "first_name": first_name, # First name
            "last_name": last_name, # Last name
            "action": action, # Email confirm action
            "exp": exp # Expiration time
        }
        # Generatea the token using JWT secret and algorithm
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_token(token:str): # Decodes the provided JWT token and verifies its authenticity.
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            raise ValueError("Invalid or Expired Token") # Raises exception if the token is invalid
    
    @staticmethod
    def create_login_token(email: str, user_id: int, first_name: str, last_name: str): 
        # Creates JWT token for user login with longer expiration
        exp = datetime.utcnow() + timedelta(hours=24) # Sets expiration time 24 hours from current UTC time
        payload = {
            "sub": email, # Sets subject of the token as user's email
            "user_id": user_id, # Unique identifier of the user
            "first_name": first_name, # User's first name for payload reference
            "last_name": last_name, # User's last name for payload reference
            "action": "login", # Custom claim indicating token is for login action
            "exp": exp # Expiration claim required by JWT to invalidate old tokens
        }
        # Encodes the payload into a JWT using the secret and specified algorithm
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token # Returns the signed JWT token
    
    @staticmethod
    def verify_login_token(token: str): 
        # Verifies the integrity and validity of a login JWT token
        try:
            # Decodes the token using the secret and allowed algorithm
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            # Checks if the action in the payload is "login" to ensure correct token type
            if payload.get("action") != "login":
                raise ValueError("Invalid token type")  # Raises error for incorrect token purpose
            return payload # Returns the decoded payload if valid
        
        except JWTError:
            raise ValueError("Invalid or Expired Login Token")  # Catches any token decoding errors including expiration 
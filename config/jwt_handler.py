import os # Accesses the environment variables..
from jose import JWTError, jwt # Creates and verifies Json Web Tokens
from dotenv import load_dotenv # Loads secrets from .env.

load_dotenv() # Loads Environment Variables from .env File

# Enviroment Configurations
JWT_SECRET = os.getenv("JWT")
JWT_ALGORITHM = "HS256" # HMAC SHA256 for signing JWTs

class JWTHandler:
    @staticmethod
    def create_token(email: str, action: str, name: str): # Creates signed JWT token with email & action type.
    
        payload = {
            "sub": email, # Subject email of the user
            "name": name,  # User's name
            "action": action, # Aprroval or rejection action
        }
        # Generates the token using JWT secret and algorithm
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def decode_token(token:str): # Decodes the provided JWT token and verifies its authenticity.
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            raise ValueError("Invalid or Expired Token") # Raises exception if the token is invalid
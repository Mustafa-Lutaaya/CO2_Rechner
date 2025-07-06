import random # Generates random passwords
import bcrypt # Securely hashes passwords
import string # For Letters, digits & symbols choice
import re # Enables regular expression matching to validate password strength

class PWDHandler:
    @staticmethod
    def generate_password(length=12): # Generates a random password with the specified length.
        characters = string.ascii_letters + string.digits + string.punctuation # The password includes uppercase, lowercase, digits, and special characters.
        return ''.join(random.choices(characters, k=length)) #  # Picks length characters randomly and joins them

    @staticmethod
    def hash_password(password): # Hashes a plain password using bcrypt.
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) # Hashes password with bcrypt
        return hashed.decode('utf-8') # Returns hashed password as string
    
    @staticmethod
    def verify_password(plain_password, hashed_password): # Verifies a password attempt against a stored bcrypt hash and returns True if they match, False otherwise
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')) # Since both inputs must be bytes, we encode them and check if passwords match
    
    @staticmethod
    def validate_password_strength(password):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'

        # Checks if passwords match the pattern
        if re.match(pattern, password):
            return True
        else:
            return False
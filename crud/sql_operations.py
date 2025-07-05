from models.models import CO2, VER # Imports the CO2 model used for querying the database
from sqlalchemy.orm import Session # Imports SQLAlchemy session object

# SQL OPERATIONS
class SQLCRUD:
    # Fetches all item records from the SQL database using db as an active SQLAlchemy database session
    def fetch_items_from_sql(self, db: Session):
        items = db.query(CO2).order_by(CO2.category.asc(), CO2.name.asc()).all() # Queries the Table, retrieves all rows and returns them as a list of CO2 Item Objects then sorts the data 
        return items
    
    # Function to return a single verified user by email & extract their name
    def get_ver_user_by_email(self, db: Session,  email: str):
        user = db.query(VER).filter(VER.email == email).first() # Queries the Verified Users Table filtering rows where the Email Column matches the input EMail. first() returns the first matching email or None if no match is found
        return user.email
from sqlalchemy.orm import Session # Imports Session to interact with the database
from models.models import CO2, USER  # Imports the ORM model for the items table plus pending & verified users tables
from schemas.schemas import co2_createitem, user, ver_user # Imports Pydantic models for input validation
from config.pwd_handler import PWDHandler # Imports password handler to be using during user verification
from config.mail_handler import EmailHandler # Imports email handler to be using during user registration

class CRUD:
    # ITEM OPERATIONS
    # Function to add new item to the database with parameters: the active database session and item following the CO2ItemCreate Structure to validate the data
    def create_item(self, db: Session, item: co2_createitem):
        new_item = CO2(**item.model_dump()) # Creates new instance of CO2Item ORM Model. **item.model_dump() converts the Pydantic model into a dictionary of field names and values as ** operator unpacks them as arguments to the CO2Item constructor
        db.add(new_item) # Adds new item object to the currrent database session
        db.commit() # Commits the session to save the new item permanently to the database
        db.refresh(new_item) # Refreshes the new_item object to get any updates made by the database like adding the auto generated id
        return new_item # Returns newly created item instance with id
    
    # Function to get all items from the database with active database session as parameter
    def get_all_items(self, db: Session):
        return db.query(CO2).order_by(CO2.category.asc(), CO2.name.asc()).all() # Queries the Table, retrieves all rows and returns them as a list of CO2 Item Objects then sorts the data 
    
    # Function to get a single item by name with active database session and item_name as parameteres
    def get_itemby_name(self, db: Session,  name: str):
        return db.query(CO2).filter(CO2.name == name).first() # Queries the CO2 Item filtering rows where the Name Column matches the input name. first() returns the first matchin item or None if no match is found

    # Function to update an exisiting item identified by 'Name'
    def update_item(self, db: Session, name: str, data: co2_createitem):
        item = self.get_itemby_name(db, name) # Fetches the item from database using the provided name
        # Updates item attributes with the new data provided , if the item exists
        if item:
            item.name = data.name # Updates the Name field in case its changed
            item.category = data.category # Updates the Category field in case its changed
            item.base_co2 = data.base_co2 # Updates the Base_CO2 field with the new CO2 value in case its changed
            db.commit() # Commits the session to save all the changes permanetly in the database
            db.refresh(item) # Refreshes the ORM instance to ensure it reflects the latest state from the database
        return item # Returns the updated item or None if no item was found to updated

    # Function to delete an item from the database identified by 'Name'
    def delete_item(self, db: Session, name: str):
        item = self.get_itemby_name(db, name) # Retrieves the item by name to ensure it exists before attempting deletion
        # Proceeds with deletion if the item exists in the database,
        if item:
            db.delete(item) # Marks the item for deletion in the current session
            db.commit() # Commit the transaction to remove the item from the database permanently
        return item  # Return the deleted item instance or None if the item was not found

    # USER OPERATIONS
    # Function to register new user and add them to the pending users databse with parameters: the active database session and penuser following the pen_user Structure to validate the data
    def register_user(self, db: Session, user: user):
        new_user = USER(**user.model_dump()) # Creates new instance of PENUser ORM Model. **user.model_dump() converts the Pydantic model into a dictionary of field names and values as ** operator unpacks them as arguments to the PENUser constructor
        EmailHandler.send_to_admin(new_user.name, new_user.email) # Sends email to admin for verification
        db.add(new_user) # Adds new user object to the currrent database session
        db.commit() # Commits the session to save the new user permanently to the database
        db.refresh(new_user) # Refreshes the new_user object to get any updates made by the database like adding the auto generated id
        return new_user # Returns newly created user instance with id
    
    # Function to get all pending users from the database with active database session as parameter
    def get_all_users(self, db: Session):
        return db.query(USER).all() # Queries the Table, retrieves all rows and returns them as a list of Pending User Objects
    
    # Function to return a single pending user by email with active database session and user email as parameteres
    def get_user_by_email(self, db: Session,  email: str):
        return db.query(USER).filter(USER.email == email).first() # Queries the Pending Users Table filtering rows where the Email Column matches the input EMail. first() returns the first matchin email or None if no match is found
    
    # Function to delete a pending user from the database identified by 'Email'
    def delete_user(self, db: Session, email: str):
        user = self.get_user_by_email(db, email) # Retrieves the pending user by email to ensure they exists before attempting deletion
        # Proceeds with deletion if the user exists in the database,
        if user:
            db.delete(user) # Marks the user for deletion in the current session
            db.commit() # Commit the transaction to remove the user from the database permanently
        return user  # Return the deleted user instance or None if the user was not found
    
    # Function to delete all pending users from the database
    def delete_users(self, db: Session):
        users = self.get_all_users(db) # Retrieves the pending users 
        # Proceeds with deletion 
        if users:
            for user in users:
                db.delete(user) #Deletes each user individually
            db.commit() # Commits the transaction to remove the users from the database permanently
        return users  # Returns list of deleted users or empty list
    
    # Function to verify pending user
    def verify_user(self, db: Session, email: str):
        user = self.get_user_by_email(db, email) # Retrieves the pending user
        
        # Returns none if user isnt found
        if not user:
            return None
        
        # Checks if user was already verified
        if user.is_verified:
            return "already_verified"
        
        pwd = PWDHandler.generate_password() # Generates password
        hashedpwd = PWDHandler.hash_password(pwd) # Hashes the password
        
        # Creates a verified user with required fields
        user.password = hashedpwd
        user.is_verified = True # Marks user as verified
        
        EmailHandler.send_to_user(user.name, user.email, pwd)
        
        db.commit() # Commits the transaction
        db.refresh(user) # Refreshes to get the new ID from database

        return user # Returns user plus unhashed password which can be emailed to user
    
    # Function to reject user
    def reject_user(self, db: Session, email: str):
        user = self.get_user_by_email(db, email) # Retrieves the pending user
        
        # Returns none if user isnt found
        if not user:
            return None
        
        # Checks if user was already verified
        if user.is_verified:
            return "already_verified"
        
        db.delete(user) # Deletes entirely from database
        db.commit() # Commits the transaction

        return "rejected" # Removes and returns rejected user
       
    # Function to update a verified users password by confirming their email
    def change_password(self, db: Session, email: str, new_password: str):
        user = self.get_user_by_email(db, email) # Fetches the user from database using the provided email

        if not user:
            return None # Raises an excpetion if user isnt found
        
        if not PWDHandler.validate_password_strength(new_password):
            return None   # Raises an exception if password doesn meant the criteria
            
        hashed_pwd = PWDHandler.hash_password(new_password) # Hashes the new password
        user.password = hashed_pwd # Updates the Password field 
        db.commit() # Commits the session to save all the changes permanetly in the database
        db.refresh(user) # Refreshes the ORM instance to ensure it reflects the latest state from the database
        return user # Returns the updated User or None if none was found

    
    # Function to confirm password
    def confirm_password(self, db: Session, password: str, email: str):
        user = self.get_user_by_email(db, email) # Fetches the user from database using the provided email

        if not user:
            return None # Raises an excpetion it user isnt found
        
        verify_pwd = PWDHandler.verify_password(password, user.password)
        if not verify_pwd:
            return None   # Raises an exception if passwords mismatch
            
        return user # Returns the updated User or None if none was found
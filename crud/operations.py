from sqlalchemy.orm import Session, joinedload # Imports SQLAlchemy Session for DB operations, and loading strategies for relationships
from fastapi import Request
from models.models import Admin, User, UserProfile, Item, Category # Imports all SQLAlchemy ORM models
from schemas.schemas import Create_AdminUser, CreateUser, CreateUserProfile, CreateCategory, CreateItem # Imports Pydantic schemas for request validation and response formatting
from config.pwd_handler import PWDHandler # Imports password hashing and verification handler
from config.mail_handler import EmailHandler # Imports email handler to send registration or verification emails
from utilities.utils import AuditLogger  # Imports audit helper class
from datetime import datetime # Used for handling and formatting datetime values

# ADMIN OPERATIONS
class AdminUserCRUD:
    # Function to register new admin user and add them to the pending users database with parameters: the active database session and user following the user Structure to validate the data
    def register_admin_user(self, db: Session, user: Create_AdminUser, request: Request = None):
        new_user = Admin(**user.model_dump()) # Creates new instance of User ORM Model. **user.model_dump() converts the Pydantic model into a dictionary of field names and values as ** operator unpacks them as arguments to the User constructor
        db.add(new_user) # Adds new user object to the currrent database session
        db.commit() # Commits the session to save the new user permanently to the database
        db.refresh(new_user) # Refreshes the new_user object to get any updates made by the database like adding the auto generated id
        EmailHandler.send_to_admin(new_user.first_name, new_user.last_name, new_user.email) # Sends email to admin for verification
        AuditLogger.log_action(db=db, action="register_admin_user", resource_type="Admin", resource_id=new_user.id, admin_id=new_user.id, status="success", details={"email": new_user.email, "first_name": new_user.first_name}, request=request) # Logs the action
        return new_user # Returns newly created user instance with id
    
    # Function to get all Admin Users from the database with active database session as parameter
    def get_all_admin_users(self, db: Session):
        return db.query(Admin).all() # Queries the Table, retrieves all rows and returns them as a list of User Objects
    
    # Function to return a single admin user by email with active database session and user email as parameters
    def get_admin_user_by_email(self, db: Session,  email: str):
        return db.query(Admin).filter(Admin.email == email).first() # Queries the Admin Users Table filtering rows where the Email Column matches the input Email. first() returns the first matchin email or None if no match is found
    
    # Function to delete an admin user from the database identified by 'Email'
    def delete_admin_user(self, db: Session, email: str, request: Request = None):
        user = self.get_admin_user_by_email(db, email) # Retrieves the admin user by email to ensure they exist before attempting deletion
        
        # Proceeds with deletion if the admin_user exists in the database,
        if user:
            db.delete(user) # Marks the user for deletion in the current session
            db.commit() # Commits the transaction to remove the user from the database permanently
            AuditLogger.log_action(db=db, action="delete_admin_user", resource_type="Admin", resource_id=user.id, admin_id=user.id, status="success", details={"email": user.email}, request=request) # Logs the action
        return user  # Return the deleted user instance or None if the user was not found
    
    # Function to delete all admin users from the database
    def delete_admin_users(self, db: Session):
        users = self.get_all_admin_users(db) # Retrieves all admin users 
        # Proceeds with deletion 
        if users:
            for user in users:
                db.delete(user) # Deletes each adminuser individually
            db.commit() # Commits the transaction to remove the admin users from the database permanently
        return users  # Returns list of deleted admin users or empty list

    # Function to verify pending Admin user
    def verify_admin_user(self, db: Session, email: str, request: Request = None):
        user = self.get_admin_user_by_email(db, email) # Retrieves the pending admin user
        
        # Returns none if admin user isnt found
        if not user:
            return None
        
        # Checks if admin user was already verified
        if user.is_verified:
            return "already_verified"
        
        pwd = PWDHandler.generate_password() # Generates password
        hashedpwd = PWDHandler.hash_password(pwd) # Hashes the password
        
        # Creates a verified admin user with required fields
        user.password = hashedpwd
        user.is_verified = True # Marks admin user as verified
        user.force_password_change = True # Forces password change on first login
        
        EmailHandler.send_to_user(user.first_name, user.email, pwd)
        
        db.commit() # Commits the transaction
        db.refresh(user) # Refreshes to get the new ID from database

        AuditLogger.log_action(db=db, action="verify_admin_user", resource_type="Admin", resource_id=user.id, admin_id=user.id, status="success", details={"email": user.email}, request=request) # Logs the action
        return user # Returns admin user plus unhashed password which can be emailed to user
    
    # Function to reject admin user
    def reject_admin_user(self, db: Session, email: str, request: Request = None):
        user = self.get_admin_user_by_email(db, email) # Retrieves the pending admin user
        
        # Returns none if admin user isnt found
        if not user:
            return None
        
        # Checks if admin user was already verified
        if user.is_verified:
            return "already_verified"
        
        db.delete(user) # Deletes entirely from database
        db.commit() # Commits the transaction

        AuditLogger.log_action(db=db, action="reject_admin_user", resource_type="Admin", resource_id=None, admin_id=None, staus="success", details={"email": email}, request=request) # Logs the action
        return "rejected" # Returns status
       
    # Function to update a verified admin users password by confirming their email
    def change_password(self, db: Session, email: str, new_password: str, request: Request = None):
        user = self.get_admin_user_by_email(db, email) # Fetches the admin user from database using the provided email

        if not user:
            return "User not found" # Raises an excpetion if admin user isnt found
        
        if not PWDHandler.validate_password_strength(new_password):
            return "Password must be at least 8 characters long, include upper and lower case letters, a number, and a special character."   # Raises an exception if new password doesnt meant the criteria
            
        hashed_pwd = PWDHandler.hash_password(new_password) # Hashes the new password
        user.password = hashed_pwd # Updates the Password field 
        user.force_password_change = False # Clears the force change flag
        db.commit() # Commits the session to save all the changes permanetly in the database
        db.refresh(user) # Refreshes the ORM instance to ensure it reflects the latest state from the database
        AuditLogger.log_action(db=db, action="change_password", resource_type="Admin", resource_id=user.id, admin_id=user.id, user_id=None, status="success", details={"email": email}, request=request) # Logs password change
        return "success" # Returns the updated Admin User or None if none was found
    
    # Function to confirm new password
    def confirm_password(self, db: Session, password: str, email: str):
        user = self.get_admin_user_by_email(db, email) # Fetches the admin user from database using the provided email

        if not user:
            return None # Raises an excpetion it admin user isnt found
        
        verify_pwd = PWDHandler.verify_password(password, user.password)
        if not verify_pwd:
            return None   # Raises an exception if passwords mismatch
            
        return user # Returns the updated User or None if none was found

# USER OPERATIONS
class UserCRUD:
    # Function to register new user and add them to the pending users databse with parameters: the active database session and user following the user Structure to validate the data
    def create_user(self, db: Session, user: CreateUser, user_type: str = "client", request: Request = None):

        # Checks Password strength
        if not PWDHandler.check_password_strength(user.password):
            raise ValueError("Password must be at least 8 characters long and include uppercase, lowercase, number, and symbol.")
        
        # Hashed the password
        hashed_password = PWDHandler.hash_password(user.password)

        # Creates new user with hashed password
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        user_data["user_type"] = user_type  # Sets user type

        new_user = User(**user_data)  # Creates new instance of User ORM Model. **user.model_dump() converts the Pydantic model into a dictionary of fields ** operator unpacks them as arguments to the User constructor
        EmailHandler.send_confirmation_email(new_user.first_name, new_user.last_name, new_user.work_email) # Initiates email verification workflow
        db.add(new_user) # Adds new user object to the currrent database session
        db.commit() # Commits the session to save the new user permanently to the database
        db.refresh(new_user) # Refreshes the new_user object to get any updates made by the database like adding the auto generated id

        # Auto-creates profile for client users to ensure data consistency
        if user_type == "client":
            profile_crud = UserProfileCRUD()    
            default_profile = CreateUserProfile(user_id=new_user.id, company_name="", industry="", preferences={}) # Creates basic profile with default values
            profile_crud.create_profile(db, default_profile, new_user.id)
        
        AuditLogger.log_action(db=db, action="create_user", resource_type="User", resource_id=new_user.id, user_id=new_user.id, status="success", details={"email": new_user.work_email, "first_name": new_user.first_name}, request=request) # Logs user registration
        return new_user # Returns newly created user instance with id
    
    # Function to get all users from the database with active database session as parameter
    def get_all_users(self, db: Session, user_type: str = None):
        query = db.query(User)
        if user_type:
            query = query.filter(User.user_type == user_type)
        return query.all() # Queries the Table, retrieves all rows and returns them as a list of User Objects then sorts the data
    
    # Function to get all admin users
    def get_all_admin_users(self, db: Session):
        return self.get_all_users(db, user_type="admin")
    
    # Function to get all client users
    def get_all_client_users(self, db: Session):
        return self.get_all_users(db, user_type="client")
    
    # Function to return a single user by email with active database session and user email as parameteres
    def get_user_by_email(self, db: Session, email: str, user_type: str = None):
        query = db.query(User).filter(User.email == email)
        if user_type:
            query = query.filter(User.user_type == user_type)
        return query.first() # Queries the Users Table filtering rows where the Email Column matches the input EMail. first() returns the first matchin email or None if no match is found
    
    # Function to get admin user by email
    def get_admin_by_email(self, db: Session, email: str):
        return self.get_user_by_email(db, email, user_type="admin")
    
    # Function to get client user by email
    def get_client_by_email(self, db: Session, email: str):
        return self.get_user_by_email(db, email, user_type="client")
    
    # Function to delete a  user from the database identified by 'Email'
    def delete_user(self, db: Session, work_email: str, user_type: str = None, request: Request = None):
        user = self.get_user_by_email(db, work_email, user_type) # Retrieves the user by email to ensure they exists before attempting deletion
        # Proceeds with deletion if the user exists in the database,
        if user:
            db.delete(user) # Marks the user for deletion in the current session
            db.commit() # Commit the transaction to remove the user from the database permanently

            AuditLogger.log_action(db=db, action="delete_user", resource_type="User", resource_id=user.id, user_id=None, status="success", details={"email": work_email}, request=request) # Logs deletion
        return user  # Return the deleted user instance or None if the user was not found
    
    # Function to verify pending user
    def verify_user(self, db: Session, email: str, user_type: str = None, request: Request = None):
        user = self.get_user_by_email(db, email, user_type) # Retrieves the unverified user
        
        # Returns none if unverified user isnt found
        if not user:
            return None
        
        # Checks if user was already verified
        if user.is_verified:
            return "already_verified"
        
        user.is_verified = True # Changes verification boolean from false to True
        user.verified_at = datetime.utcnow() # Indicates time user was verified

        db.commit()  # Commits the transaction
        db.refresh(user)  # Refreshes to get the new ID from database

        AuditLogger.log_action(db=db, action="verify_user", resource_type="User", resource_id=user.id, user_id=user.id, status="success", details={"email": email}, request=request) # Logs verification
        return user # Returns veified user
    
      
    # # Function to update a verified users password by confirming their email
    def change_password(self, db: Session, email: str, new_password: str, request: Request = None):
        user = self.get_user_by_email(db, email) # Fetches the admin user from database using the provided email

        if not user:
            return "User not found" # Raises an excpetion if admin user isnt found
        
        if not PWDHandler.check_password_strength(new_password):
            return "Password must be at least 8 characters long, include upper and lower case letters, a number, and a special character."   # Raises an exception if new password doesnt meant the criteria
            
        hashed_pwd = PWDHandler.hash_password(new_password) # Hashes the new password
        user.password = hashed_pwd # Updates the Password field 
        user.force_password_change = False # Clears the force change flag
        db.commit() # Commits the session to save all the changes permanetly in the database
        db.refresh(user) # Refreshes the ORM instance to ensure it reflects the latest state from the database
        AuditLogger.log_action(db=db, action="change_password", resource_type="Admin", resource_id=user.id, admin_id=user.id, user_id=None, status="success", details={"email": email}, request=request) # Logs password change
        return "success" # Returns the updated Admin User or None if none was found
    

    # Function to confirm password
    def confirm_password(self, db: Session, password: str, work_email: str, user_type: str = None, request: Request = None):
        user = self.get_user_by_email(db, work_email, user_type) # Fetches the user from the database using the provided work email 

        if not user: 
            return None # Raises an exception if the user isnt found 
        
        verifyPWD = PWDHandler.verify_password(password, user.password)
        if not verifyPWD:
            return None # Rasies an exception if password mismatch
        
        AuditLogger.log_action(db=db, action="confirm_password", resource_type="User", resource_id=user.id, user_id=user.id, status="success", details={"email": work_email}, request=request) # Logs password confirmation
        return user # Returns the  User or None if none was found 

# USER PROFILE OPERATIONS
class UserProfileCRUD:
    def create_profile(self, db: Session, profile_data: CreateUserProfile, user_id: int, request: Request = None):
        # Checks if profile already exists for this user
        existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if existing_profile:
            raise ValueError("User profile already exists") # Prevents duplicate profiles

        # Creates new profile with default preferences
        new_profile = UserProfile(user_id=user_id, name=profile_data.name, location=profile_data.location)
        db.add(new_profile) # Adds new user profile object to the currrent database session
        db.commit() # Commits the session to save the new user profile permanently to the database
        db.refresh(new_profile) # Refreshes the new_profile object to get any updates made by the database like adding the auto generated id

        AuditLogger.log_action(db=db, action="create_profile", resource_type="UserProfile", resource_id=new_profile.id, user_id=user_id, status="success", details={"name": profile_data.name, "location": profile_data.location}, request=request) # Logs profile creation
        return new_profile # Returns newly created user profile instance with id
    
    # Function to return a single user profile by user_id with active database session and user id as parameters
    def get_profile_by_user_id(self, db: Session, user_id: int):
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first() # Retrieves user profile
    
    # Function to upate a user profile
    def update_profile(self, db: Session, user_id: int, profile_data: CreateUserProfile, request: Request = None):
        # Retrieves profile before updating it
        profile = self.get_profile_by_user_id(db, user_id)
        if not profile:
            return None

        # Updates profile fields
        profile.name = profile_data.name
        profile.location = profile_data.location
        profile.updated_at = datetime.utcnow()

        db.commit() # Commits the session to save the updated user profile permanently to the database
        db.refresh(profile) # Refreshes the updated profile object to get any updates made by the database like adding the auto generated id
        
        AuditLogger.log_action(db=db, action="update_profile", resource_type="UserProfile", resource_id=profile.id, user_id=user_id, status="success", details={"name": profile_data.name, "location": profile_data.location}, request=request) # Logs profile update
        return profile # Returns upated user profile instance with id

# ITEM OPERATIONS
class ItemCRUD:
    # Function to add new item to the database with parameters: the active database session and item following the CreateItem Structure to validate the data
    def create_item(self, db: Session, item: CreateItem):
        # Looks up the category by its name to ensure it exists
        category = db.query(Category).filter(Category.name == item.category_name).first()
        if not category:
            raise ValueError(f"Category '{item.category_name}' does not exist")  # Enforces category requirement
        
        # Creates new item with category_id from the found category
        new_item = Item(
            name=item.name,
            count=getattr(item, "count", 0),
            base_co2=item.base_co2,
            category=category
        )

        db.add(new_item) # Adds new item object to the currrent database session
        db.commit() # Commits the session to save the new item permanently to the database
        db.refresh(new_item) # Refreshes the new_item object to get any updates made by the database like adding the auto generated id
        return new_item # Returns newly created item instance with id
    
    # Function to get all items from the database with active database session as parameter
    def get_all_items(self, db: Session):
        return (
            db.query(Item)
            .options(joinedload(Item.category))  # Eager loads category
            .order_by(Item.category_id.asc(), Item.name.asc())  # Sorts by category_id
            .all()
        )
    
    # Function to get a single item by name with active database session and item_name as parameteres
    def get_item_by_name(self, db: Session,  name: str):
        return db.query(Item).filter(Item.name == name).first() # Queries the CO2 Item filtering rows where the Name Column matches the input name. first() returns the first matchin item or None if no match is found
   
    # Function to update an exisiting item identified by 'Name'
    def update_item(self, db: Session, name: str, data: CreateItem):
        item = self.get_item_by_name(db, name) # Fetches the item from database using the provided name
        # Updates item attributes with the new data provided , if the item exists
        if item:
            item.name = data.name # Updates the Name field in case its changed
            # Finds category and update category_id
            category = db.query(Category).filter(Category.name == data.category_name).first()
            if not category:
                raise ValueError(f"Category '{data.category_name}' does not exist")
            item.category_id = category.id
            item.base_co2 = data.base_co2 # Updates the Base_CO2 field with the new CO2 value in case its changed
            db.commit() # Commits the session to save all the changes permanetly in the database
            db.refresh(item) # Refreshes the ORM instance to ensure it reflects the latest state from the database
        return item # Returns the updated item or None if no item was found to updated

    # Function to delete an item from the database identified by 'Name'
    def delete_item(self, db: Session, name: str):
        item = self.get_item_by_name(db, name) # Retrieves the item by name to ensure it exists before attempting deletion
        # Proceeds with deletion if the item exists in the database,
        if item:
            db.delete(item) # Marks the item for deletion in the current session
            db.commit() # Commit the transaction to remove the item from the database permanently
        return item  # Return the deleted item instance or None if the item was not found

# CATEGORY OPERATIONS
class CategoryCRUD:
    # Function to add new category to the database with parameters: the active database session and category following the CreateCategory Structure to validate the data
    def create_category(self, db: Session, category: CreateCategory):
        new_category = Category(**category.model_dump())  # Creates new instance of Category ORM Model
        db.add(new_category)  # Adds new category object to the current database session
        db.commit()  # Commits the session to save the new category permanently to the database
        db.refresh(new_category)  # Refreshes the object to get any updates from the database such as auto generated id
        return new_category  # Returns newly created category instance with id
    
    # Function to get all categories from the database with active database session as parameter
    def get_all_categories(self, db: Session):
        return db.query(Category).order_by(Category.name.asc()).all()  # Retrieves all rows and sorts them by category name

    # Function to get a single category by name with active database session and category_name as parameter
    def get_category_by_name(self, db: Session, name: str):
        return db.query(Category).filter(Category.name == name).first()  # Queries the Category filtering rows by Name

    # Function to update an existing category identified by 'Name'
    def update_category(self, db: Session, name: str, data: CreateCategory):
        category = self.get_category_by_name(db, name)  # Fetches the category from database using the provided name
        if category:
            category.name = data.name  # Updates the Name field
            category.description = data.description  # Updates the Description field if provided
            db.commit()  # Commits changes permanently
            db.refresh(category)  # Refreshes the ORM instance with latest state
        return category  # Returns updated category or None if no category was found

    # Function to delete a category from the database identified by 'Name'
    def delete_category(self, db: Session, name: str):
        category = self.get_category_by_name(db, name)  # Retrieves the category by name to ensure it exists
        if category:
            db.delete(category)  # Marks the category for deletion
            db.commit()  # Permanently deletes the category
        return category  # Returns deleted category instance or None if not found
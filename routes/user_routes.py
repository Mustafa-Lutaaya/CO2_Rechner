from fastapi import HTTPException, Depends, APIRouter # Imports exception handling, dependency injection, and routing
from fastapi.responses import JSONResponse  # JSON response handling
from sqlalchemy.orm import Session  # SQLAlchemy DB session management
from crud.operations import UserProfileCRUD  # Imports CRUD operations for users
from database.database import get_db # Provides DB session dependency
from config.auth_middleware import AuthMiddleware # JWT-based authentication middleware
from models.models import User # SQLAlchemy User model
from config.pwd_handler import PWDHandler # Password hashing and validation
from schemas.schemas import CreateUserProfile, UserProfileUpdate

router = APIRouter()  # Initializes API router
ucrud = UserProfileCRUD() # Initializes instance of User CRUD operations

# PROFILE MANAGEMENT
# Protected route to retrieve the current user's profile
@router.get("/profile") # GET /profile returns current user info
def get_user_profile(current_user: User = Depends(AuthMiddleware.get_current_user), db: Session = Depends(get_db)): # Injects DB session & authenticated user dependency
    # Gets current user's profile information
    try:
        if current_user.user_type != "client":
            raise HTTPException(status_code=403, detail="Profile access is only available for allowed users")
        
        profile = ucrud.get_profile_by_user_id(db, current_user.id)

        # Creates default profile if user doesnt have one yet
        if not profile:
            default_profile = CreateUserProfile(
                name="",
                location=""
            )
            profile = ucrud.create_profile(db, default_profile, current_user.id)
        
        # Returms all profile data
        return{"success": True,
                "profile": {
                        "user_id": profile.user_id,
                        "name": profile.name,
                        "location": profile.location,
                    }
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")

# Protected route to update user profile information
@router.put("/profile") # PUT /profile updates user info
def update_user_profile(profile_updates: UserProfileUpdate, current_user: User = Depends(AuthMiddleware.get_current_user), db: Session = Depends(get_db)):  # Injects DB session plus Incoming data for profile update & Authenticated user 
    # Update current user's profile information
    try:
        updated_profile = ucrud.update_profile(db, current_user.id, profile_updates)

        if not updated_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        
        return {"success": True, 
                "message": "Profile updated successfully",
                "updated_at": updated_profile.updated_at.isoformat(),
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


# DASHBOARD DATA 
# Route to retrieve user dashboard data
@router.get("/dashboard")
def get_user_dashboard_data(current_user: User = Depends(AuthMiddleware.get_current_user), db: Session = Depends(get_db)):
    try:
        user_id = current_user.id
        profile = ucrud.get_profile_by_user_id(db, user_id)
        
        
        # Returns comprehensive dashboard data
        return {
            "user_info": {
                "name": f"{current_user.first_name} {current_user.last_name}",
                "email": current_user.work_email,
                "company": profile.company_name if profile else "Not set"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

# Route to change user's password
@router.post("/change-password") # POST /user/change-password updates user password 
def change_password(password_data: dict, current_user: User = Depends(AuthMiddleware.get_current_user), db: Session = Depends(get_db)):  # Injects DB session plus incoming data including old and new passwords with Authenticated user
    #Change user's password
    try:
        old_password = password_data.get("old_password")
        new_password = password_data.get("new_password")
        confirm_password = password_data.get("confirm_password")
        
        # Validates that all password fields are provided
        if not old_password or not new_password or not confirm_password:
            return JSONResponse(
                status_code=400, content={"success": False, "message": "All password fields are required", "error_code": "MISSING_FIELDS"}
            )
        
        # Verifies old password
        if not ucrud.confirm_password(db, old_password, current_user.work_email):
            return JSONResponse(
                status_code=401,content={"success": False, "message": "Current password is incorrect", "error_code": "INVALID_OLD_PASSWORD"}
            )
        
        # Checks if new passwords match
        if new_password != confirm_password:
            return JSONResponse(
                status_code=400, content={"success": False, "message": "New passwords don't match", "error_code": "PASSWORD_MISMATCH"}
            )
        
        # Validate new password strength
        if not PWDHandler.check_password_strength(new_password):
            return JSONResponse(
                status_code=400, content={"success": False, "message": "Password must be 8+ characters, include uppercase, lowercase, number, and symbol", "error_code": "WEAK_PASSWORD"}
            )
        
        # Hashes new password and updates DB
        hashed_password = PWDHandler.hash_password(new_password)
        current_user.password = hashed_password
        db.commit()
        
        return JSONResponse(
            status_code=200, content={"success": True, "message": "Password changed successfully"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "message": "Failed to change password", "error_code": "PASSWORD_CHANGE_FAILED"}
        )
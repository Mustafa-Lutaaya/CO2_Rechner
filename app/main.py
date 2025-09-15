from fastapi import FastAPI # Imports FastAPI class to create the main app instance
from fastapi.middleware.cors import CORSMiddleware # Imports CORS to enable communication beteween frontend and backend
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from routes.admin_routes import router as admin_router # Imports Admin router instance from the admin_routes module and renames it as admin_router
from routes.protected_routes import router as protected_router  # Imports Protected router instance from the protected_routes module and renames it as protected_router
from fastapi.middleware.wsgi import WSGIMiddleware # Imports WSGI adapter to mount WSGI apps inside FastAPI
from fastapi.responses import RedirectResponse  # For returning HTML content in the welcome route
from routes.frontend_routes import router as frontend_router # Imports API router instance from the frontend_routes module and renames it as frontendrouter
from routes.backend_routes import router as backend_router  # Imports API router instance from the api_routes module and rename it as api_router
from routes.user_routes import router as user_router # Imports User router instance from the user_routes module and renames it as user_router
from routes.ui_routes import router as ui_router  # Imports UI router instance from the ui_routes module and rename it as ui_router
from routes.email_routes import router as email_router  # Imports Email router instance from the email_routes module and rename it as email_router
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support
from pathlib import Path # Provides object-oriented file system paths
import os

app = FastAPI(
    title="CO2 Spar Rechner",
    description="Welcome to the CO2 Savings Calculator. Use `/UI` for the user interface or `/api` for direct API access.", # Initializes the FastAPI application
    version="5.0.0"
) 


# Custom WSGI middleware to handle authentication by wrapping dash with cookie & auth headers support
class AuthenticatedWSGIMiddleware:
    def __init__(self, app):
        self.app = app # Stores app being wrapped
    
    # Ensures cookies and auth-headers are properly forwarded
    def __call__(self, environ, start_response):
        # Makes sure cookies exist
        if 'HTTP_COOKIE' not in environ:
            environ['HTTP_COOKIE'] = ''
        
        # Makes sure auth headers exists
        if 'HTTP_AUTHORIZATION' not in environ:
            environ['HTTP_AUTHORIZATION'] = ''
        
        # Add CORS headers so that Dash can be called from frontend
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('Access-Control-Allow-Origin', '*'))
            headers.append(('Access-Control-Allow-Credentials', 'true'))
            headers.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'))
            headers.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization'))
            return start_response(status, headers, exc_info)
            
        return self.app(environ, custom_start_response)  # Forwards request to wrapped app


app.mount("/static", StaticFiles(directory="static"), name="static") # Mounts the 'static' Files directory making it accessible via '/static' URL 
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder

# Registers routers for different features
app.include_router(backend_router, prefix="/api", tags=["Backend"]) # Adds the Backend router to the main app, prefixing all its routes with "/api" meaning every path inside the api_router will be available under "/api". The tags parameter groups the routes under a Backend tag in Swagger UI
app.include_router(frontend_router, prefix="/rec", tags=["Frontend"]) # Adds the Frontend router to the main app, prefixing all its routes with "/js" meaning every path inside the api_router will be available under "/js". The tags parameter groups the routes under a Frontend tag in Swagger UI
app.include_router(ui_router, prefix="/UI", tags=["UI"])# Adds the User Interaction router to the main app, prefixing all its routes with "/UI" meaning every path inside the UI_router will be available under "/UI". The tags parameter groups the routes under an UI tag in Swagger UI
app.include_router(email_router, prefix="/email", tags=["Email"])# Adds the Email router to the main app, prefixing all its routes with "/email" meaning every path inside the email_router will be available under "/email". The tags parameter groups the routes under an Email tag in Swagger UI
app.include_router(admin_router, prefix="/admin", tags=["Admin"])# Adds the Admin router to the main app, prefixing all its routes with "/admin" meaning every path inside the email_router will be available under "/admin. The tags parameter groups the routes under an Admin tag in Swagger UI
app.include_router(user_router, prefix="/user", tags=["User Profile"])# Adds the User router to the main app, prefixing all its routes with "/user meaning every path inside the user_router will be available under "/user". The tags parameter groups the routes under a User Profile tag in Swagger UI
app.include_router(protected_router, tags=["Pro"])  # Adds the Protected router to the main app, for routes that require authentification. The tags parameter groups the routes under a Pro tag in Swagger UI

ENV = os.getenv("ENV", "dev")
print(f"Current ENV: {ENV}")

if ENV not in ["dev", "prod"]:
    raise ValueError("Invalid ENV setting. Must be 'dev' or 'prod'.")

@app.get("/", response_class=RedirectResponse)
def root_redirect():
    if ENV == "prod":
        return RedirectResponse(url="https://co2-rechner.onrender.com/admin")
    else:
        return RedirectResponse(url="http://localhost:5050/admin")


# Domains allowed to make requests to the backend
origins = [
    "http://localhost:5000",   # Local dev server
    "http://127.0.0.1:5000",
    "https://co2-spar-rechner.onrender.com"
]

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Allows requests from these origins
    allow_credentials=True,     # Allows cookies and authentication headers
    allow_methods=["*"],        # Allows all HTTP methods 
    allow_headers=["*"],        # Allows all headers
)
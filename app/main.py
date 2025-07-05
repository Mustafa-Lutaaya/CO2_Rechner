from fastapi import FastAPI # Imports FastAPI class to create the main app instance
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from fastapi.responses import RedirectResponse  # For returning HTML content in the welcome route
from routes.ui_routes import router as ui_router  # Imports UI router instance from the ui_routes module and rename it as ui_router
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support
from pathlib import Path # Provides object-oriented file system paths
from fastapi.middleware.cors import CORSMiddleware # Imports CORS to enable communication beteween frontend and backend

app = FastAPI(
    title="CO2 Spar Rechner",
    description="Welcome to the CO2 Savings Calculator Demo Page.", # Initializes the FastAPI application
    version="1.0.0"
) 

app.mount("/static", StaticFiles(directory="static"), name="static") # Mounts the 'static' Files directory making it accessible via '/static' URL 
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder

app.include_router(ui_router, prefix="/UI", tags=["UI"])# Adds the User Interaction router to the main app, prefixing all its routes with "/UI" meaning every path inside the UI_router will be available under "/UI". The tags parameter groups the routes under an UI tag in Swagger UI

@app.get("/", response_class=RedirectResponse)
def demo_page():
    return RedirectResponse(url="/UI")

# Domains allowed to make requests to the backend
origins = [
    "http://localhost:5050",   # Local dev server
    "http://127.0.0.1:5050",
]

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Allows requests from these origins
    allow_credentials=True,     # Allows cookies and authentication headers
    allow_methods=["*"],        # Allows all HTTP methods 
    allow_headers=["*"],        # Allows all headers
)
from fastapi import FastAPI, Request  # Imports FastAPI class to create the main app instance
from fastapi.staticfiles import StaticFiles # Serves Static Files Like CSS, JS & Images
from fastapi.responses import HTMLResponse  # For returning HTML content in the welcome route
from routes.api_routes import router as api_router  # Imports API router instance from the api_routes module and rename it as api_router
from routes.ui_routes import router as ui_router  # Imports UI router instance from the ui_routes module and rename it as ui_router
from routes.email_routes import router as email_router  # Imports Email router instance from the email_routes module and rename it as email_router
from fastapi.templating import Jinja2Templates  # Imports Jinja2 template support
from pathlib import Path # Provides object-oriented file system paths
from fastapi.middleware.cors import CORSMiddleware # Imports CORS to enable communication beteween frontend and backend

app = FastAPI(
    title="CO2 Spar Rechner",
    description="Welcome to the CO2 Savings Calculator. Use `/UI` for the user interface or `/api` for direct API access.", # Initializes the FastAPI application
    version="1.0.0"
) 

app.mount("/static", StaticFiles(directory="static"), name="static") # Mounts the 'static' Files directory making it accessible via '/static' URL 
templates = Jinja2Templates(directory=Path(__file__).parent.parent/"templates")  # Sets up Jinja2Templates for dynamic HTML rendering from templates folder

app.include_router(api_router, prefix="/api", tags=["API"]) # Adds the API router to the main app, prefixing all its routes with "/api" meaning every path inside the api_router will be available under "/api". The tags parameter groups the routes under an API tag in Swagger UI
app.include_router(ui_router, prefix="/UI", tags=["UI"])# Adds the User Interaction router to the main app, prefixing all its routes with "/UI" meaning every path inside the UI_router will be available under "/UI". The tags parameter groups the routes under an UI tag in Swagger UI
app.include_router(email_router, prefix="/email", tags=["Email"])# Adds the Email router to the main app, prefixing all its routes with "/email" meaning every path inside the email_router will be available under "/email". The tags parameter groups the routes under an Email tag in Swagger UI


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request, "admin.html")  

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
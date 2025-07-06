
# CO2 SPAR RECHNER                 
This is the backend for the **YoungCaritas Kleidertausch CO₂ Savings Calculator**, developed as a final semester project to improve the original system with:

-  A complete admin dashboard
-  User registration & approval
-  Persistent data saving via PostgreSQL
-  A flexible CO₂ item management system

#### FEATURES 
- Admins can now:
  - Add, edit, or delete clothing items with CO₂ base values
  - Manage user registrations (approve/reject)
  - View & interact with data using a built-in UI or Swagger documentation
- Built with **FastAPI**, **PostgreSQL**, **Jinja2**, and **Docker**
- Swagger UI for API exploration: `/docs`
- Admin UI: `/UI/admin`

## MAIN SETUP
#### 1.0 Clone the Repository from : git clone https://github.com/Mustafa-Lutaaya/CO2_Spar_Rechner
cd CO2-Spar-Rechner

#### NOTE: 
1. Before running the app (via Makefile or Docker), you **must create a `.env` file** in the project root
2.  If you're using local development (not Docker), make sure your PostgreSQL server is running and a database named spar_db exists.
3. You can create it manually using: 

##### psql -U postgres

##### CREATE DATABASE spar_db;

#### 1.1 ". Create `.env` file:

##### The .env File should have:             
1. JWT=your_jwt_secret                                        
2. ADMIN_EMAIL=your_admin_email@example.com                   
3. SENDER_EMAIL=your_email@example.com                        
4. EMAIL_PASSWORD=your_email_password                                             
5. POSTGRES_USER=admin                                        
6. POSTGRES_PASSWORD=password                                 
7. POSTGRES_DB=spar_db                                        
8. DATABASE_URL differs based on usage:    

#### A: For Local Development with Makefile or localhost     
DATABASE_URL=postgresql://admin:password@localhost:5432/spar_db   
                                                           
#### B. For Docker Usage with docker compose up              
DATABASE_URL=postgresql://admin:password@db:5432/spar_db   

#### 1.2 Generate a JWT Secret:
- cd config

- Run: python generate_jwt_secret.py

- Copy the output and paste it into the JWT field in your .env file.

##  DOCKER SETUP

#### i.  Start Services
In the terminal run; docker-compose up --build

#### ii. Access
-App: http://localhost:8000

-Swagger Docs: http://localhost:8000/docs

-Admin UI: http://localhost:8000/UI/admin

##  LOCAL DEVELOPMENT SETUP - MAKEFILE OR LOCALHOST

#### i.  Download and install Make first then copy the bin file path to the system variables on windows

#### ii. Setup Virtual Enviroment with: make create

#### ii. Activate the Virtual Enviroment with: make act

#### iii. Install Dependencies with: make install

#### iv.  Start the Server with: make start

#### v.  Visit http://localhost:8000 to access the system.

## TESTING 
Run tests with: make pytest

## TECH STACK  
- Backend Framework: FastAPI 

- Database: PostgreSQL — Relational database for storing users, items, and CO₂ values

- Frontend (UI Layer): Jinja2 templating engine used to build admin/user-facing UI

- Authentication & Security: JWT (JSON Web Tokens)

- Secrets (Python): Used to generate secure JWT keys

- Environment & Dependency Management: Makefile — For simple local automation (virtualenv setup, running server, tests)

- Python virtualenv: Isolated environment for Python dependencies

- DevOps / Containerization: Docker Containerized environment for the app and database

- docker-compose: For managing multi-container setup (FastAPI + PostgreSQL)

- Testing: pytest — Unit and integration tests for API and database logic

- API Documentation: Swagger UI (via FastAPI) — Auto-generated API docs available at /docs

____________________________
MAINTAINER - MUSTAFA LUTAAYA
----------------------------
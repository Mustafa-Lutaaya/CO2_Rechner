# PostGreSQL Migration
'''
1. psql -U postgres
2. CREATE DATABASE name_db;
3. CREATE USER admin WITH PASSWORD '1234';
4. GRANT ALL PRIVILEGES ON DATABASE name_db TO admin;
5. GRANT ALL ON SCHEMA public TO admin;


1. Why use Schemas and Models in FastAPI?
Models
Purpose: Represent the database structure — how data is stored.

Typically defined using ORMs like SQLAlchemy e.g : A User model defines the users table with columns like id, name, email.

2. Schemas (Pydantic Models)
Purpose: Define how data is validated and structured for API input/output.

Used to ensure incoming requests have the right fields and format, and to control the shape of responses.
eg. A UserCreate schema might require name and email fields when creating a new user, but not include database-specific fields like id or timestamps.

Summary
Models = raw data storage (DB layer).

Schemas = data validation & transformation (API layer).

Difference between Unit Testing and Integration Testing
Aspect	      Unit Testing	                                  Integration Testing
Focus	      Tests a single piece of code in isolation	      Tests how multiple components work together
Scope	      Smallest parts (e.g., a function or method)	  Multiple modules, components, or systems
Dependencies  Mocks or stubs external dependencies	          Uses actual dependencies (DB, APIs, etc.)
Speed	      Fast	                                          Slower due to more components involved
Example	      Test a function that adds two numbers	          Test API endpoint including DB interaction
Purpose	      Ensure individual units behave correctly	      Ensure the system components integrate well


In FastAPI context:
Unit test: Test a single route function or utility function, mocking the database or external APIs.

Integration test: Test the actual HTTP request to your API, with the database and other services running.

docker-compose down -v
docker-compose build --no-cache
docker-compose up

for category in grouped_items:
    for item in category["items"]:
        mongo.co2.update_one(
            {"name": item["name"], "category": category["category"]},
            {"$set": item},
            upsert=True
        )
'''

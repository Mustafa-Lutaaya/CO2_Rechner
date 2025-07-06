from fastapi.testclient import TestClient # Imports the TestClient class from FastAPI, used to simulate requests to the app.
from app.main import app # Imports the FastAPI app instance from the app code

client = TestClient(app) # Creates a test client that can be used to send HTTP requests to the FastAPI app

# Test to verify POST /api/items endpoint works as expected by simulating creation of a new item and checks the response
def test_create_item_api():
    # Sends a POST request to create a new item with name, category, and base_co2 fields
    response = client.post("/api/items", 
                           json={
                               "name": "Mütze",
                               "category": "ACCESSORIES",
                               "base_co2": 12.5
                           })
    print("RESPONSE JSON:", response.json())
    assert response.status_code == 200 # Asserts that the response status code is 200 
    data = response.json() # Parses the response body as JSON
    assert data["name"] == "Mütze" # Asserts that the returned name matches the input
    assert data["category"] == "ACCESSORIES"  # Asserts that the returned category matches the input
    assert data["base_co2"] == 12.5  # Asserts that the returned base_co2 matches the input
    client.delete(f"/api/items/Mütze") # Deletes name after test to prevent duplication error

# Test to verify GET /api/items returns all items checking that the response is a list and has status code OK
def test_get_all_items_api():
    # Sends a GET request to retrieve all items
    response = client.get("/api/items")
    
    assert response.status_code == 200 # Asserts that the status code is 200 
    assert isinstance(response.json(), list) # Asserts that the response body is a list of items

# Test to verify GET /api/items/{name} returns 404 when item does not exist ensuring API handles non-existent items properly
def test_get_item_not_found():
    # Sends a GET request for an item that is not in the system
    response = client.get("/api/items/UnknownItem")

    assert response.status_code == 404 # Assert that the status code is 404 
    assert response.json()["detail"] == "Item not found" # Asserts that the detail message in the response indicates "Item not found"

# Test to verify PUT /api/items/{name} updates an existing item by creating the item, updatingit then verifying the update
def test_update_item_api():
    # 1. Creates the item with initial data
    client.post("/api/items", 
                json={
                    "name": "Schuhe", # Name of the item
                    "category": "EINTEILER & SCHUHE", # Category
                    "base_co2": 9.8 # Initial CO2 value
                })
    
    # 2. Sends a PUT request to update the item
    response = client.put("/api/items/Schuhe", 
                           json={
                               "name": "Schuhe", # Same Name
                               "category": "EINTEILER & SCHUHE", # Same Category
                               "base_co2": 10.5 # Updated CO2 value
                           })
    
    assert response.status_code == 200 # Asserts that the status code is 200
    assert response.json()["base_co2"] == 10.5 # Asserts that the base_co2 value has been updated correctly
    client.delete(f"/api/items/Schuhe") # Deletes name after test to prevent duplication error
    
# Test to verify DELETE /api/items/{name} deletes an existing item by creating the item, deleting it and ensuring its properly removed
def test_delete_item_api():
    # 1. Creates the item to be deleted
    client.post("/api/items", 
                json={
                    "name": "Rock", # Name of the item
                    "category": "UNTERTEIL", # Category
                    "base_co2": 7.0 # CO2 value
                })
    
    # 2. Sends a DELETE request to remove the item
    response = client.delete("/api/items/Rock")

    assert response.status_code == 200 # Asserts that the status code is 200
    assert response.json()["name"] == "Rock" # Asserts that the name in the response matches the deleted item's name
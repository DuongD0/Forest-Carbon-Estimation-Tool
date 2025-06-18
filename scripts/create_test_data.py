import requests
import json
import uuid

API_BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer dev-token-123"
}

def create_test_projects():
    """Create test projects"""
    print("Creating test projects...")
    
    projects = [
        {
            "name": "Vietnam Mangrove Restoration",
            "description": "Restoring 500 hectares of mangrove forests in the Mekong Delta",
            "project_type": "Forestry",
            "status": "Active"
        },
        {
            "name": "Central Highlands Reforestation",
            "description": "Reforestation project covering 1000 hectares in Dak Lak province",
            "project_type": "Forestry", 
            "status": "Active"
        },
        {
            "name": "Bamboo Forest Expansion",
            "description": "Expanding bamboo forests for carbon sequestration and sustainable materials",
            "project_type": "Forestry",
            "status": "Draft"
        }
    ]
    
    created_projects = []
    for project in projects:
        response = requests.post(f"{API_BASE_URL}/projects/", headers=HEADERS, json=project)
        if response.status_code == 200:
            created_projects.append(response.json())
            print(f"✓ Created project: {project['name']}")
        else:
            print(f"✗ Failed to create project: {project['name']} - {response.status_code}: {response.text}")
    
    return created_projects

def get_user_id():
    """Get the current user ID"""
    response = requests.get(f"{API_BASE_URL}/users/me", headers=HEADERS)
    if response.status_code == 200:
        return response.json()["id"]
    return None

def create_carbon_credits(project_id):
    """Create carbon credits for a project"""
    credit = {
        "project_id": project_id,
        "vcs_serial_number": f"VCS-VN-{uuid.uuid4().hex[:8].upper()}",
        "quantity_co2e": 10000.0,
        "vintage_year": 2024,
        "status": "ISSUED"
    }
    
    response = requests.post(f"{API_BASE_URL}/carbon-credits/", headers=HEADERS, json=credit)
    if response.status_code == 200:
        return response.json()
    return None

def create_marketplace_listing(credit_id, seller_id):
    """Create a marketplace listing"""
    listing = {
        "credit_id": credit_id,
        "seller_id": seller_id,
        "price_per_ton": 25.0,
        "quantity": 1000.0,
        "status": "ACTIVE"
    }
    
    response = requests.post(f"{API_BASE_URL}/p2p/listings", headers=HEADERS, json=listing)
    if response.status_code == 200:
        print("✓ Created marketplace listing")
        return response.json()
    else:
        print(f"✗ Failed to create listing: {response.status_code}: {response.text}")
    return None

def main():
    print("=" * 60)
    print("CREATING TEST DATA FOR FOREST CARBON ESTIMATION TOOL")
    print("=" * 60)
    
    # Get user ID
    user_id = get_user_id()
    if not user_id:
        print("✗ Failed to get user ID")
        return
    
    print(f"✓ User ID: {user_id}")
    
    # Create projects
    projects = create_test_projects()
    
    # Create carbon credits and marketplace listings for the first project
    if projects:
        print("\nCreating carbon credits and marketplace listing...")
        credit = create_carbon_credits(projects[0]["id"])
        if credit:
            print(f"✓ Created carbon credit: {credit['vcs_serial_number']}")
            listing = create_marketplace_listing(credit["id"], user_id)
    
    print("\n" + "=" * 60)
    print("TEST DATA CREATION COMPLETE")
    print("=" * 60)
    print("\nYou can now:")
    print("- View projects at http://localhost:3000/projects")
    print("- View marketplace at http://localhost:3000/marketplace")
    print("- Check dashboard at http://localhost:3000/")

if __name__ == "__main__":
    main() 
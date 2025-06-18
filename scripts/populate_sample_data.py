#!/usr/bin/env python3
"""
Populate the database with sample data for testing
"""
import requests
import json

def create_sample_ecosystem():
    """Create a sample ecosystem"""
    base_url = "http://localhost:8000/api/v1"
    headers = {
        "Authorization": "Bearer dev-token-123",
        "Content-Type": "application/json"
    }
    
    ecosystem_data = {
        "name": "Vietnamese Tropical Forest",
        "description": "Dense tropical forest ecosystem typical of Vietnam's mountainous regions",
        "carbon_factor": 15.5,
        "max_biomass_per_ha": 350.0,
        "biomass_growth_rate": 0.08,
        "lower_rgb": [20, 40, 20],
        "upper_rgb": [80, 120, 80],
        "forest_type": "dense_tropical"
    }
    
    try:
        response = requests.post(f"{base_url}/ecosystems/", headers=headers, json=ecosystem_data)
        if response.status_code == 200:
            print(f"✓ Created ecosystem: {response.json()['name']}")
            return response.json()
        else:
            print(f"✗ Failed to create ecosystem: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating ecosystem: {e}")
        return None

def create_sample_project(ecosystem_id=None):
    """Create a sample project"""
    base_url = "http://localhost:8000/api/v1"
    headers = {
        "Authorization": "Bearer dev-token-123",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "name": "Ba Vi National Park Reforestation",
        "description": "Reforestation project in Ba Vi National Park, focusing on native species restoration",
        "project_type": "Forestry",
        "ecosystem_id": ecosystem_id
    }
    
    try:
        response = requests.post(f"{base_url}/projects/", headers=headers, json=project_data)
        if response.status_code == 200:
            print(f"✓ Created project: {response.json()['name']}")
            return response.json()
        else:
            print(f"✗ Failed to create project: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating project: {e}")
        return None

def test_api_with_data():
    """Test API endpoints with the created data"""
    base_url = "http://localhost:8000/api/v1"
    headers = {
        "Authorization": "Bearer dev-token-123",
        "Content-Type": "application/json"
    }
    
    print("\nTesting API with sample data...")
    
    # Test ecosystems
    try:
        response = requests.get(f"{base_url}/ecosystems/", headers=headers)
        ecosystems = response.json()
        print(f"✓ Found {len(ecosystems)} ecosystems")
        for eco in ecosystems:
            print(f"  - {eco['name']}: {eco['forest_type']}")
    except Exception as e:
        print(f"✗ Error fetching ecosystems: {e}")
    
    # Test projects
    try:
        response = requests.get(f"{base_url}/projects/", headers=headers)
        projects = response.json()
        print(f"✓ Found {len(projects)} projects")
        for proj in projects:
            print(f"  - {proj['name']}: {proj['status']}")
    except Exception as e:
        print(f"✗ Error fetching projects: {e}")

if __name__ == "__main__":
    print("=== Populating Sample Data ===\n")
    
    # Create sample ecosystem
    ecosystem = create_sample_ecosystem()
    
    # Create sample project
    ecosystem_id = ecosystem['id'] if ecosystem else None
    project = create_sample_project(ecosystem_id)
    
    # Test the API with the new data
    test_api_with_data()
    
    print("\n🎉 Sample data creation completed!")
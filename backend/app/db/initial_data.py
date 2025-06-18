from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ecosystem import Ecosystem
from app.models.user import User
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
import uuid

def init_db(db: Session) -> None:
    # Create default ecosystems for Vietnam
    ecosystems_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Evergreen Forest",
            "description": "Tropical evergreen forests in Vietnam",
            "carbon_factor": 0.47,
            "max_biomass_per_ha": 250.0,
            "biomass_growth_rate": 0.05,
            "lower_rgb": [20, 40, 20],
            "upper_rgb": [80, 120, 80],
            "forest_type": "dense_tropical"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Deciduous Forest",
            "description": "Tropical deciduous forests in Vietnam",
            "carbon_factor": 0.45,
            "max_biomass_per_ha": 200.0,
            "biomass_growth_rate": 0.04,
            "lower_rgb": [30, 50, 20],
            "upper_rgb": [90, 130, 70],
            "forest_type": "medium_tropical"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mixed Forest",
            "description": "Mixed tropical forests in Vietnam",
            "carbon_factor": 0.46,
            "max_biomass_per_ha": 225.0,
            "biomass_growth_rate": 0.045,
            "lower_rgb": [25, 45, 20],
            "upper_rgb": [85, 125, 75],
            "forest_type": "mixed_tropical"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mangrove Forest",
            "description": "Coastal mangrove forests",
            "carbon_factor": 0.48,
            "max_biomass_per_ha": 280.0,
            "biomass_growth_rate": 0.06,
            "lower_rgb": [15, 35, 15],
            "upper_rgb": [60, 100, 60],
            "forest_type": "mangrove"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bamboo Forest",
            "description": "Bamboo forests and plantations",
            "carbon_factor": 0.43,
            "max_biomass_per_ha": 150.0,
            "biomass_growth_rate": 0.08,
            "lower_rgb": [40, 60, 30],
            "upper_rgb": [100, 140, 80],
            "forest_type": "bamboo"
        }
    ]
    
    # Check if ecosystems already exist
    existing_ecosystems = db.query(Ecosystem).first()
    if not existing_ecosystems:
        for eco_data in ecosystems_data:
            ecosystem = Ecosystem(**eco_data)
            db.add(ecosystem)
        db.commit()
        print(f"Created {len(ecosystems_data)} ecosystems")
    else:
        print("Ecosystems already exist, skipping...")
    
    # Create a test user if it doesn't exist
    test_email = "test@example.com"
    user = crud_user.get_by_email(db, email=test_email)
    if not user:
        user_in = UserCreate(
            email=test_email,
            first_name="Test",
            last_name="User",
            organization="Test Organization"
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"Created test user: {test_email}")
    else:
        print(f"Test user already exists: {test_email}")

def main() -> None:
    db = SessionLocal()
    try:
        init_db(db)
        print("Initial data loaded successfully!")
    except Exception as e:
        print(f"Error loading initial data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 
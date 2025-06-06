import asyncio
import sys
import os
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app import crud, schemas
from app.core.config import settings

def init_db(db: Session) -> None:
    # Create a default admin role and user
    role = crud.role.get_by_name(db, name="admin")
    if not role:
        role_in = schemas.RoleCreate(role_name="admin", description="Administrator")
        role = crud.role.create(db, obj_in=role_in)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role_id=role.id,
            is_active=True,
        )
        user = crud.user.create(db, obj_in=user_in)

    # Add Vietnam-specific allometric equations
    equations_data = [
        {"equation_name": "Vietnam_Tropical_AGB_1", "equation_formula": "0.0673 * (wood_density * (dbh**2) * height)**0.976", "region": "Vietnam", "species_group": "Tropical Broadleaf"},
        {"equation_name": "Vietnam_Mangrove_AGB_1", "equation_formula": "0.251 * wood_density * dbh**2.46", "region": "Vietnam", "species_group": "Mangrove"},
    ]
    
    db_equations = {}
    for eq_data in equations_data:
        equation = crud.allometric_equation.get_by_name(db, name=eq_data["equation_name"])
        if not equation:
            equation = crud.allometric_equation.create(db, obj_in=schemas.AllometricEquationCreate(**eq_data))
        db_equations[equation.equation_name] = equation

    # Add some common Vietnamese tree species
    species_data = [
        {"scientific_name": "Dipterocarpus alatus", "common_name_vi": "Dầu rái", "wood_density": 0.74, "default_allometric_equation_id": db_equations["Vietnam_Tropical_AGB_1"].equation_id},
        {"scientific_name": "Hopea odorata", "common_name_vi": "Sao đen", "wood_density": 0.78, "default_allometric_equation_id": db_equations["Vietnam_Tropical_AGB_1"].equation_id},
        {"scientific_name": "Rhizophora apiculata", "common_name_vi": "Đước", "wood_density": 0.85, "default_allometric_equation_id": db_equations["Vietnam_Mangrove_AGB_1"].equation_id},
    ]

    for sp_data in species_data:
        tree = crud.tree_species.get_by_scientific_name(db, scientific_name=sp_data["scientific_name"])
        if not tree:
            crud.tree_species.create(db, obj_in=schemas.TreeSpeciesCreate(**sp_data))

def main() -> None:
    print("Initializing data...")
    db = SessionLocal()
    init_db(db)
    db.close()
    print("Data initialized.")

if __name__ == "__main__":
    main() 